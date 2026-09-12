"""Unit tests for the deterministic What-If simulation aggregation pipeline.

Expected values below are hand-computed against the Step 06 emission
factors/candidate rules (see `test_recommendation_service.py`) and the
`COST_TIER_ESTIMATES` fixed placeholder scale from `app/data/cost_estimates.py`.
"""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.data.cost_estimates import COST_TIER_ESTIMATES
from app.models import Factory, Material, Process, Waste
from app.services import emission_calculation_service, recommendation_service
from app.services import simulation_service
from app.services.errors import ValidationError


def _make_factory(db_session: Session) -> Factory:
    factory = Factory(name="Acme Steel", industry="steel", assessment_period="2025-Q1")
    db_session.add(factory)
    db_session.flush()
    return factory


def _make_process(db_session: Session, factory: Factory, name: str = "Smelting") -> Process:
    process = Process(factory_id=factory.id, name=name)
    db_session.add(process)
    db_session.flush()
    return process


def _seed_material_hotspot(db_session: Session) -> tuple[Factory, Decimal]:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # 100 kg, 0% recycled -> effective factor 2.00 -> co2e = 200.00.
    db_session.add(
        Material(
            process_id=process.id,
            material_name="Iron ore",
            quantity=Decimal("100"),
            unit="kg",
            recycled_percentage=Decimal("0"),
        )
    )
    db_session.commit()
    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)
    return factory, breakdown.factory_total_co2e


def test_empty_selection_returns_zero_impact_result(db_session: Session) -> None:
    factory, baseline = _seed_material_hotspot(db_session)
    recommendation_service.generate_for_factory(db_session, factory.id)

    result = simulation_service.simulate_for_factory(db_session, factory.id, [])

    assert result.baseline_co2e == baseline
    assert result.projected_co2e == baseline
    assert result.co2_reduction == Decimal("0.00")
    assert result.reduction_percentage == Decimal("0.00")
    assert result.total_implementation_cost == Decimal("0.00")
    assert result.estimated_payback_months is None
    assert result.applied_recommendations == []


def test_known_subset_produces_hand_computed_values(db_session: Session) -> None:
    factory, baseline = _seed_material_hotspot(db_session)
    recommendations = recommendation_service.generate_for_factory(db_session, factory.id)

    # baseline == 200.00
    assert baseline == Decimal("200.00")

    substitute = next(r for r in recommendations if r.strategy == "substitute")
    reduce_candidate = next(
        r for r in recommendations if r.strategy == "process_optimization"
    )
    # substitute.co2_reduction == 150.00 (medium cost -> 200000, 12mo payback)
    # reduce_candidate.co2_reduction == 16.00 (low cost -> 50000, 9mo payback)
    assert substitute.co2_reduction == Decimal("150.00")
    assert reduce_candidate.co2_reduction == Decimal("16.00")

    result = simulation_service.simulate_for_factory(
        db_session, factory.id, [substitute.id, reduce_candidate.id]
    )

    expected_reduction = Decimal("150.00") + Decimal("16.00")  # 166.00
    expected_projected = baseline - expected_reduction  # 34.00
    expected_percentage = (expected_reduction / baseline * 100).quantize(Decimal("0.01"))
    expected_cost = (
        COST_TIER_ESTIMATES["medium"] + COST_TIER_ESTIMATES["low"]
    ).quantize(Decimal("0.01"))
    expected_payback = (
        (
            substitute.payback_period * COST_TIER_ESTIMATES["medium"]
            + reduce_candidate.payback_period * COST_TIER_ESTIMATES["low"]
        )
        / (COST_TIER_ESTIMATES["medium"] + COST_TIER_ESTIMATES["low"])
    ).quantize(Decimal("0.01"))

    assert result.baseline_co2e == baseline
    assert result.co2_reduction == expected_reduction
    assert result.projected_co2e == expected_projected
    assert result.reduction_percentage == expected_percentage
    assert result.total_implementation_cost == expected_cost
    assert result.estimated_payback_months == expected_payback
    assert {r.id for r in result.applied_recommendations} == {
        substitute.id,
        reduce_candidate.id,
    }


def test_reduction_exceeding_baseline_clamps_projected_to_zero(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # 100 kg landfilled -> co2e = 100 * 0.58 = 58.00.
    db_session.add(
        Waste(
            process_id=process.id,
            waste_type="slag",
            quantity=Decimal("100"),
            unit="kg",
            disposal_method="landfilled",
        )
    )
    db_session.commit()
    breakdown = emission_calculation_service.calculate_for_factory(db_session, factory.id)
    baseline = breakdown.factory_total_co2e
    assert baseline == Decimal("58.00")

    recommendations = recommendation_service.generate_for_factory(db_session, factory.id)
    # recycle (53.00) + reuse (56.00) + reduce (4.64) = 113.64, well over the
    # 58.00 baseline -- this combination is a deliberately unrealistic
    # "select every candidate for the same hotspot" scenario used purely to
    # exercise the clamp.
    all_ids = [r.id for r in recommendations]

    result = simulation_service.simulate_for_factory(db_session, factory.id, all_ids)

    assert result.projected_co2e == Decimal("0.00")
    assert result.co2_reduction == baseline


def test_unknown_recommendation_id_raises_validation_error(db_session: Session) -> None:
    factory, _ = _seed_material_hotspot(db_session)
    recommendation_service.generate_for_factory(db_session, factory.id)

    with pytest.raises(ValidationError):
        simulation_service.simulate_for_factory(db_session, factory.id, [999999])
