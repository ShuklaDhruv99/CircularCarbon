"""Deterministic bucketing of current recommendations into a phased action plan.

Given a factory's currently-persisted `Recommendation` rows (via
`recommendation_service.get_for_factory`), buckets each recommendation into
one of three implementation horizons -- "now", "next", "later" -- using the
fixed thresholds documented in `app/data/action_plan_rules.py`, then
aggregates per-phase totals (`co2_reduction` sum, and implementation cost
sum via `cost_estimates.COST_TIER_ESTIMATES`). Computed on demand and not
persisted, matching Steps 07/08.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from sqlalchemy.orm import Session

from app.data.action_plan_rules import (
    LATER_PAYBACK_MONTHS_THRESHOLD,
    NOW_PAYBACK_MONTHS_THRESHOLD,
)
from app.data.cost_estimates import COST_TIER_ESTIMATES
from app.schemas.action_plan import ActionPlanPhaseRead, ActionPlanRead
from app.schemas.recommendation import RecommendationRead
from app.services import recommendation_service

TWO_PLACES = Decimal("0.01")

Phase = Literal["now", "next", "later"]


def _bucket(rec: RecommendationRead) -> Phase:
    """Assign a single recommendation to a phase using the fixed rules.

    Evaluated in order (first match wins):
    1. "later" if estimated_cost == "high" OR payback_period > LATER threshold
    2. "now" if estimated_cost == "low" AND (payback_period is None OR <= NOW threshold)
    3. "next" otherwise
    """

    payback = rec.payback_period

    if rec.estimated_cost == "high" or (
        payback is not None and payback > LATER_PAYBACK_MONTHS_THRESHOLD
    ):
        return "later"

    if rec.estimated_cost == "low" and (
        payback is None or payback <= NOW_PAYBACK_MONTHS_THRESHOLD
    ):
        return "now"

    return "next"


def _build_phase(phase: Phase, recommendations: list[RecommendationRead]) -> ActionPlanPhaseRead:
    total_co2_reduction = sum(
        (rec.co2_reduction for rec in recommendations), Decimal("0")
    ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    total_implementation_cost = sum(
        (COST_TIER_ESTIMATES[rec.estimated_cost] for rec in recommendations),
        Decimal("0"),
    ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return ActionPlanPhaseRead(
        phase=phase,
        recommendations=recommendations,
        total_co2_reduction=total_co2_reduction,
        total_implementation_cost=total_implementation_cost,
    )


def get_action_plan(db: Session, factory_id: int) -> ActionPlanRead:
    """Compute the prioritized action plan for a factory.

    Raises `NotFoundError` (via `recommendation_service.get_for_factory`,
    which delegates to `hotspot_service.get_hotspots`) if the factory
    doesn't exist or has no calculated emissions yet. Returns a plan with
    all three phases present (each possibly empty) if the factory has zero
    recommendations. Recommendations within each phase preserve the score
    desc / id asc ordering they arrive in from `get_for_factory`.
    """

    recommendations = recommendation_service.get_for_factory(db, factory_id)

    buckets: dict[Phase, list[RecommendationRead]] = {
        "now": [],
        "next": [],
        "later": [],
    }
    for rec in recommendations:
        buckets[_bucket(rec)].append(rec)

    return ActionPlanRead(
        factory_id=factory_id,
        now=_build_phase("now", buckets["now"]),
        next=_build_phase("next", buckets["next"]),
        later=_build_phase("later", buckets["later"]),
    )
