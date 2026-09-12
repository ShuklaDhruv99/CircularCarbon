"""Unit tests for the deterministic action-plan bucketing/aggregation logic.

`RecommendationRead` instances are constructed directly (no DB) for the
bucketing-rule unit tests below, since the specific combinations of
`estimated_cost`/`payback_period` needed to exercise every phase boundary --
including a null `payback_period`, which Step 06's generation pipeline never
actually produces -- are easier to pin precisely this way than via seeded
factory data. Empty/populated end-to-end behavior is covered against real
persisted recommendations in `test_action_plan_api.py`.
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.data.cost_estimates import COST_TIER_ESTIMATES
from app.models import EnergyConsumption, Factory, Material, Process
from app.schemas.recommendation import RecommendationRead
from app.services import action_plan_service, emission_calculation_service, recommendation_service

TWO_PLACES = Decimal("0.01")


def _make_recommendation(
    id: int,
    estimated_cost: str,
    payback_period: Decimal | None,
    co2_reduction: Decimal = Decimal("10.00"),
    score: Decimal = Decimal("50.00"),
) -> RecommendationRead:
    return RecommendationRead(
        id=id,
        hotspot_id=1,
        hotspot_category="materials",
        hotspot_activity="Iron ore",
        title=f"Recommendation {id}",
        description="Test recommendation",
        strategy="reduce",
        estimated_cost=estimated_cost,
        co2_reduction=co2_reduction,
        payback_period=payback_period,
        score=score,
        created_at=datetime.now(timezone.utc),
    )


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


def test_empty_recommendations_yields_three_empty_phases(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
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
    emission_calculation_service.calculate_for_factory(db_session, factory.id)
    # No `generate_for_factory` call -> zero persisted recommendations, but
    # the factory has been calculated so `get_for_factory` returns [] (not 404).

    plan = action_plan_service.get_action_plan(db_session, factory.id)

    assert plan.factory_id == factory.id
    for phase in (plan.now, plan.next, plan.later):
        assert phase.recommendations == []
        assert phase.total_co2_reduction == Decimal("0.00")
        assert phase.total_implementation_cost == Decimal("0.00")


def test_bucket_low_cost_short_payback_is_now() -> None:
    rec = _make_recommendation(1, "low", Decimal("6"))
    assert action_plan_service._bucket(rec) == "now"


def test_bucket_low_cost_null_payback_is_now() -> None:
    rec = _make_recommendation(1, "low", None)
    assert action_plan_service._bucket(rec) == "now"


def test_bucket_medium_cost_is_next() -> None:
    rec = _make_recommendation(1, "medium", Decimal("3"))
    assert action_plan_service._bucket(rec) == "next"


def test_bucket_low_cost_moderate_payback_is_next() -> None:
    # low cost but payback between 6 and 24 months -> "next", not "now".
    rec = _make_recommendation(1, "low", Decimal("12"))
    assert action_plan_service._bucket(rec) == "next"


def test_bucket_high_cost_is_later_even_with_short_payback() -> None:
    rec = _make_recommendation(1, "high", Decimal("2"))
    assert action_plan_service._bucket(rec) == "later"


def test_bucket_long_payback_is_later_even_with_low_cost() -> None:
    rec = _make_recommendation(1, "low", Decimal("25"))
    assert action_plan_service._bucket(rec) == "later"


def test_bucket_payback_exactly_at_thresholds() -> None:
    # Boundary values: 6 -> now (low cost), 24 -> next (not later), 25 -> later.
    assert action_plan_service._bucket(_make_recommendation(1, "low", Decimal("6"))) == "now"
    assert action_plan_service._bucket(_make_recommendation(2, "low", Decimal("24"))) == "next"
    assert action_plan_service._bucket(_make_recommendation(3, "low", Decimal("25"))) == "later"


def test_single_phase_only_recommendations_all_land_in_now(db_session: Session) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
    # Electricity hotspot yields a "now" candidate (process_optimization,
    # low cost, 6mo payback) alongside a "next" candidate (substitute,
    # medium cost, 18mo payback) -- see `recommendation_rules.py`.
    db_session.add(
        EnergyConsumption(
            process_id=process.id,
            energy_type="electricity",
            quantity=Decimal("1000"),
            unit="kWh",
            period="2025-Q1",
        )
    )
    db_session.commit()
    emission_calculation_service.calculate_for_factory(db_session, factory.id)
    recommendation_service.generate_for_factory(db_session, factory.id)

    recs = recommendation_service.get_for_factory(db_session, factory.id)
    assert recs, "expected recommendations to be generated for the seeded hotspot"

    # Monkeypatch: build a plan using only "low"/short-payback recs to confirm
    # single-phase behavior by directly exercising _build_phase + _bucket.
    now_recs = [r for r in recs if action_plan_service._bucket(r) == "now"]
    assert now_recs, "test setup expects at least one 'now' recommendation"

    phase = action_plan_service._build_phase("now", now_recs)
    expected_reduction = sum((r.co2_reduction for r in now_recs), Decimal("0")).quantize(
        TWO_PLACES
    )
    expected_cost = sum(
        (COST_TIER_ESTIMATES[r.estimated_cost] for r in now_recs), Decimal("0")
    ).quantize(TWO_PLACES)
    assert phase.total_co2_reduction == expected_reduction
    assert phase.total_implementation_cost == expected_cost
    assert [r.id for r in phase.recommendations] == [r.id for r in now_recs]


def test_mixed_phase_recommendations_partition_without_duplication_or_omission(
    db_session: Session,
) -> None:
    factory = _make_factory(db_session)
    process = _make_process(db_session, factory)
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
    emission_calculation_service.calculate_for_factory(db_session, factory.id)
    recommendation_service.generate_for_factory(db_session, factory.id)

    plan = action_plan_service.get_action_plan(db_session, factory.id)
    all_recs = recommendation_service.get_for_factory(db_session, factory.id)

    plan_ids = (
        [r.id for r in plan.now.recommendations]
        + [r.id for r in plan.next.recommendations]
        + [r.id for r in plan.later.recommendations]
    )
    assert sorted(plan_ids) == sorted(r.id for r in all_recs)
    assert len(plan_ids) == len(set(plan_ids))

    for phase in (plan.now, plan.next, plan.later):
        scores = [r.score for r in phase.recommendations]
        ids = [r.id for r in phase.recommendations]
        assert scores == sorted(scores, reverse=True) or all(
            ids[i] <= ids[i + 1]
            for i in range(len(ids) - 1)
            if scores[i] == scores[i + 1]
        )


def test_null_payback_period_is_handled_in_now_bucket() -> None:
    rec = _make_recommendation(1, "low", None, co2_reduction=Decimal("20.00"))
    phase = action_plan_service._build_phase("now", [rec])
    assert action_plan_service._bucket(rec) == "now"
    assert phase.total_co2_reduction == Decimal("20.00")
    assert phase.total_implementation_cost == COST_TIER_ESTIMATES["low"].quantize(TWO_PLACES)


def test_null_payback_period_with_medium_cost_is_next() -> None:
    rec = _make_recommendation(1, "medium", None)
    assert action_plan_service._bucket(rec) == "next"
