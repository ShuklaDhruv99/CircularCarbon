"""Deterministic What-If simulation aggregation.

Given a factory and a subset of its currently-persisted `Recommendation`
ids, computes the combined projected impact of applying that subset on top
of the factory's already-calculated baseline total CO2e. No new emission
math is introduced here -- every number is derived by summing/aggregating
the already-verified `co2_reduction`, `estimated_cost`, and
`payback_period` fields produced by Step 06's deterministic scoring
pipeline. Results are computed on demand and are not persisted.
"""

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.data.cost_estimates import COST_TIER_ESTIMATES
from app.schemas.recommendation import RecommendationRead
from app.schemas.simulation import SimulationResult
from app.services import emission_calculation_service, recommendation_service
from app.services.errors import ValidationError

TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100")


def simulate_for_factory(
    db: Session, factory_id: int, recommendation_ids: list[int]
) -> SimulationResult:
    """Run the deterministic what-if aggregation for a factory.

    Raises `NotFoundError` (via `emission_calculation_service.get_breakdown`)
    if the factory doesn't exist or has no emissions calculated yet. Raises
    `ValidationError` if any requested id does not belong to a
    currently-persisted recommendation of that factory. Order-independent,
    duplicate ids are ignored. An empty `recommendation_ids` list is valid
    and yields a zero-impact result.
    """

    breakdown = emission_calculation_service.get_breakdown(db, factory_id)
    baseline_co2e = breakdown.factory_total_co2e

    all_recommendations = recommendation_service.get_for_factory(db, factory_id)
    by_id = {rec.id: rec for rec in all_recommendations}

    requested_ids = set(recommendation_ids)
    unknown_ids = requested_ids - by_id.keys()
    if unknown_ids:
        raise ValidationError(
            "Unknown recommendation id(s) for this factory: "
            f"{sorted(unknown_ids)}"
        )

    selected: list[RecommendationRead] = [
        by_id[rec_id] for rec_id in sorted(requested_ids)
    ]
    selected.sort(key=lambda r: (-(r.score or Decimal("0")), r.id))

    total_reduction = sum((rec.co2_reduction for rec in selected), Decimal("0"))
    projected_co2e = max(baseline_co2e - total_reduction, Decimal("0")).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )
    co2_reduction = (baseline_co2e - projected_co2e).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )

    if baseline_co2e > 0:
        reduction_percentage = (
            (co2_reduction / baseline_co2e) * HUNDRED
        ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    else:
        reduction_percentage = Decimal("0.00")

    total_implementation_cost = sum(
        (COST_TIER_ESTIMATES[rec.estimated_cost] for rec in selected), Decimal("0")
    ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    weighted_sum = Decimal("0")
    weight_total = Decimal("0")
    for rec in selected:
        if rec.payback_period is None:
            continue
        weight = COST_TIER_ESTIMATES[rec.estimated_cost]
        weighted_sum += rec.payback_period * weight
        weight_total += weight

    estimated_payback_months = (
        (weighted_sum / weight_total).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        if weight_total > 0
        else None
    )

    return SimulationResult(
        factory_id=factory_id,
        baseline_co2e=baseline_co2e,
        projected_co2e=projected_co2e,
        co2_reduction=co2_reduction,
        reduction_percentage=reduction_percentage,
        total_implementation_cost=total_implementation_cost,
        estimated_payback_months=estimated_payback_months,
        applied_recommendations=selected,
    )
