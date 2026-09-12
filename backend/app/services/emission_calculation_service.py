"""Deterministic carbon calculation pipeline.

For every process under a factory, looks up the relevant emission factor for
each energy/material/waste row, computes CO2e using `Decimal` arithmetic,
persists `EmissionResult` rows (replacing any prior results for the factory
in a single transaction), and aggregates process/category/factory totals and
percentage contributions.

`transport` is out of scope for this step -- only `energy`, `materials`, and
`waste` categories are calculated (see Step 05 spec).
"""

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.data.emission_factors import (
    ENERGY_EMISSION_FACTORS,
    MATERIAL_RECYCLED_FACTOR,
    MATERIAL_VIRGIN_FACTOR,
    WASTE_DISPOSAL_FACTORS,
    emission_factor_citation,
)
from app.models import EmissionResult, Factory, Process
from app.schemas.emission_result import (
    CategoryBreakdown,
    EmissionResultRead,
    EmissionsBreakdownRead,
    ProcessBreakdown,
)
from app.services import factory_service, process_service
from app.services.errors import NotFoundError

TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100")


def _derive_non_energy_period(factory: Factory) -> str:
    """Period for Material/Waste-derived EmissionResult rows.

    Material and Waste have no `period` column, so the derived period is the
    factory's `assessment_period`, falling back to the literal "unspecified".
    """

    return factory.assessment_period if factory.assessment_period else "unspecified"


def compute_percentages(values: list[Decimal], total: Decimal) -> list[Decimal]:
    """Compute rounded percentage contributions that sum to exactly 100.00.

    Each value's raw percentage is rounded to 2 decimal places with
    ROUND_HALF_UP. The single largest-value row's rounded percentage is then
    adjusted by the residual so the full set sums to exactly 100.00. If
    `total` is 0, returns all-zero percentages without adjustment.
    """

    if total == 0 or not values:
        return [Decimal("0.00") for _ in values]

    rounded = [
        ((value / total) * HUNDRED).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        for value in values
    ]
    residual = Decimal("100.00") - sum(rounded)
    if residual != 0:
        max_index = max(range(len(values)), key=lambda i: values[i])
        rounded[max_index] = rounded[max_index] + residual
    return rounded


def _build_breakdown(
    factory: Factory, processes: list[Process], results: list[EmissionResult]
) -> EmissionsBreakdownRead:
    factory_total = sum((r.co2e for r in results), Decimal("0"))

    # Per-category totals, in a fixed deterministic order.
    category_order = ["energy", "materials", "waste"]
    category_totals: dict[str, Decimal] = {}
    for result in results:
        category_totals[result.category] = category_totals.get(
            result.category, Decimal("0")
        ) + result.co2e
    categories = [c for c in category_order if c in category_totals]
    category_values = [category_totals[c] for c in categories]
    category_percentages = compute_percentages(category_values, factory_total)
    category_breakdown = [
        CategoryBreakdown(category=category, co2e=value, percentage=percentage)
        for category, value, percentage in zip(
            categories, category_values, category_percentages
        )
    ]

    # Per-process totals, ordered by process id for determinism.
    process_names = {process.id: process.name for process in processes}
    process_totals: dict[int, Decimal] = {}
    for result in results:
        process_totals[result.process_id] = process_totals.get(
            result.process_id, Decimal("0")
        ) + result.co2e
    process_ids = sorted(process_totals.keys())
    process_values = [process_totals[pid] for pid in process_ids]
    process_percentages = compute_percentages(process_values, factory_total)
    process_breakdown = [
        ProcessBreakdown(
            process_id=pid,
            process_name=process_names.get(pid, ""),
            co2e=value,
            percentage=percentage,
        )
        for pid, value, percentage in zip(process_ids, process_values, process_percentages)
    ]

    results_read = [
        EmissionResultRead.model_validate(r)
        for r in sorted(results, key=lambda r: r.id)
    ]

    return EmissionsBreakdownRead(
        factory_id=factory.id,
        factory_total_co2e=factory_total,
        category_breakdown=category_breakdown,
        process_breakdown=process_breakdown,
        results=results_read,
    )


def calculate_for_factory(db: Session, factory_id: int) -> EmissionsBreakdownRead:
    """Run the deterministic calculation pipeline for every process under a factory.

    Deletes and replaces the factory's existing `EmissionResult` rows and
    returns the aggregated emissions breakdown. Delete + insert + aggregate
    happens within a single commit for atomicity.
    """

    factory = factory_service.get(db, factory_id)
    processes = process_service.list_all(db, factory_id=factory_id)
    process_ids = [process.id for process in processes]

    if process_ids:
        db.execute(delete(EmissionResult).where(EmissionResult.process_id.in_(process_ids)))

    new_results: list[EmissionResult] = []
    non_energy_period = _derive_non_energy_period(factory)

    for process in processes:
        for energy in process.energy_consumption:
            factor_entry = ENERGY_EMISSION_FACTORS.get(
                energy.energy_type, ENERGY_EMISSION_FACTORS["other"]
            )
            co2e = energy.quantity * factor_entry.factor
            new_results.append(
                EmissionResult(
                    process_id=process.id,
                    category="energy",
                    activity=energy.energy_type,
                    emission_factor=factor_entry.factor,
                    emission_factor_source=emission_factor_citation(factor_entry),
                    co2e=co2e,
                    period=energy.period,
                )
            )

        for material in process.materials:
            recycled_fraction = material.recycled_percentage / HUNDRED
            effective_factor = MATERIAL_VIRGIN_FACTOR.factor * (
                Decimal("1") - recycled_fraction
            ) + MATERIAL_RECYCLED_FACTOR.factor * recycled_fraction
            co2e = material.quantity * effective_factor
            new_results.append(
                EmissionResult(
                    process_id=process.id,
                    category="materials",
                    activity=material.material_name,
                    emission_factor=effective_factor,
                    emission_factor_source=(
                        f"Blend of virgin ({emission_factor_citation(MATERIAL_VIRGIN_FACTOR)}) "
                        f"and recycled ({emission_factor_citation(MATERIAL_RECYCLED_FACTOR)}) "
                        f"material factors at {material.recycled_percentage}% recycled content"
                    ),
                    co2e=co2e,
                    period=non_energy_period,
                )
            )

        for waste in process.waste:
            factor_entry = WASTE_DISPOSAL_FACTORS.get(
                waste.disposal_method, WASTE_DISPOSAL_FACTORS["other"]
            )
            co2e = waste.quantity * factor_entry.factor
            new_results.append(
                EmissionResult(
                    process_id=process.id,
                    category="waste",
                    activity=waste.disposal_method,
                    emission_factor=factor_entry.factor,
                    emission_factor_source=emission_factor_citation(factor_entry),
                    co2e=co2e,
                    period=non_energy_period,
                )
            )

    for result in new_results:
        db.add(result)
    db.commit()

    for result in new_results:
        db.refresh(result)

    return _build_breakdown(factory, processes, new_results)


def get_breakdown(db: Session, factory_id: int) -> EmissionsBreakdownRead:
    """Return the persisted emissions breakdown for a factory.

    Raises `NotFoundError` if the factory does not exist, has zero
    processes, or has processes but zero `EmissionResult` rows (not yet
    calculated). A calculated factory with a legitimate 0 total returns the
    breakdown normally.
    """

    factory = factory_service.get(db, factory_id)
    processes = process_service.list_all(db, factory_id=factory_id)
    if not processes:
        raise NotFoundError(f"Factory {factory_id} has no processes")

    process_ids = [process.id for process in processes]
    results = list(
        db.scalars(
            select(EmissionResult).where(EmissionResult.process_id.in_(process_ids))
        ).all()
    )
    if not results:
        raise NotFoundError(f"Factory {factory_id} has not been calculated yet")

    return _build_breakdown(factory, processes, results)
