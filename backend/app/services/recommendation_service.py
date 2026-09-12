"""Deterministic circular-recommendation generation and scoring pipeline.

For every hotspot (`is_hotspot=True` `EmissionResult` row) of a factory,
looks up the fixed candidate strategies from `recommendation_rules.py`,
computes each candidate's `co2_reduction` (Decimal) using the alternate
emission factor or fixed reduction percentage, scores the candidate with the
fixed weighted formula from the Step 06 spec, persists `Recommendation`
rows, and returns them ordered by `score` descending.
"""

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.data.recommendation_rules import RecommendationCandidate, get_candidates
from app.models import EmissionResult, Recommendation
from app.schemas.emission_result import HotspotRead
from app.schemas.recommendation import RecommendationRead
from app.services import hotspot_service, process_service

TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100")

COST_SCORES: dict[str, Decimal] = {
    "low": Decimal("100"),
    "medium": Decimal("60"),
    "high": Decimal("30"),
}

CIRCULARITY_SCORES: dict[str, Decimal] = {
    "recycle": Decimal("100"),
    "reuse": Decimal("100"),
    "recover": Decimal("100"),
    "substitute": Decimal("70"),
    "reduce": Decimal("50"),
    "process_optimization": Decimal("50"),
}


def _payback_score(payback_months: int) -> Decimal:
    if payback_months <= 6:
        return Decimal("100")
    if payback_months <= 12:
        return Decimal("70")
    if payback_months <= 24:
        return Decimal("40")
    return Decimal("10")


def _compute_co2_reduction(
    hotspot: HotspotRead, candidate: RecommendationCandidate
) -> Decimal:
    if candidate.reduction_percentage is not None:
        raw = hotspot.co2e * (candidate.reduction_percentage / HUNDRED)
    else:
        assert candidate.alt_factor is not None
        quantity = (
            hotspot.co2e / hotspot.emission_factor
            if hotspot.emission_factor != 0
            else Decimal("0")
        )
        candidate_co2e = quantity * candidate.alt_factor.factor
        raw = hotspot.co2e - candidate_co2e
    return raw.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _compute_score(
    hotspot: HotspotRead, candidate: RecommendationCandidate, co2_reduction: Decimal
) -> Decimal:
    if hotspot.co2e > 0:
        impact_raw = (co2_reduction / hotspot.co2e) * HUNDRED
    else:
        impact_raw = Decimal("0")
    impact = min(impact_raw, HUNDRED).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    cost = COST_SCORES[candidate.estimated_cost]
    feasibility = Decimal(candidate.feasibility)
    circularity = CIRCULARITY_SCORES[candidate.strategy]
    payback = _payback_score(candidate.payback_months)

    final = (
        impact * Decimal("0.35")
        + cost * Decimal("0.20")
        + feasibility * Decimal("0.20")
        + circularity * Decimal("0.15")
        + payback * Decimal("0.10")
    )
    return final.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _to_read(rec: Recommendation, category: str, activity: str) -> RecommendationRead:
    return RecommendationRead(
        id=rec.id,
        hotspot_id=rec.hotspot_id,
        hotspot_category=category,
        hotspot_activity=activity,
        title=rec.title,
        description=rec.description,
        strategy=rec.strategy,
        estimated_cost=rec.estimated_cost,
        co2_reduction=rec.co2_reduction,
        payback_period=rec.payback_period,
        score=rec.score,
        created_at=rec.created_at,
    )


def generate_for_factory(db: Session, factory_id: int) -> list[RecommendationRead]:
    """Recalculate and persist recommendations for every current hotspot.

    Deletes and replaces this factory's existing `Recommendation` rows
    (scoped via their linked hotspots), generates fresh candidates for every
    `is_hotspot=True` row, and returns them ordered by `score` descending.
    """

    hotspots = hotspot_service.get_hotspots(db, factory_id)
    processes = process_service.list_all(db, factory_id=factory_id)
    process_ids = [process.id for process in processes]

    if process_ids:
        hotspot_ids_subquery = select(EmissionResult.id).where(
            EmissionResult.process_id.in_(process_ids)
        )
        db.execute(
            delete(Recommendation).where(
                Recommendation.hotspot_id.in_(hotspot_ids_subquery)
            )
        )

    flagged = [h for h in hotspots if h.is_hotspot]

    new_recs: list[tuple[Recommendation, str, str]] = []
    for hotspot in flagged:
        candidates = get_candidates(hotspot.category, hotspot.activity)
        for candidate in candidates:
            co2_reduction = _compute_co2_reduction(hotspot, candidate)
            score = _compute_score(hotspot, candidate, co2_reduction)
            rec = Recommendation(
                hotspot_id=hotspot.id,
                title=candidate.title.format(activity=hotspot.activity),
                description=candidate.description.format(activity=hotspot.activity),
                strategy=candidate.strategy,
                estimated_cost=candidate.estimated_cost,
                co2_reduction=co2_reduction,
                payback_period=Decimal(candidate.payback_months),
                score=score,
            )
            db.add(rec)
            new_recs.append((rec, hotspot.category, hotspot.activity))

    db.commit()
    for rec, _, _ in new_recs:
        db.refresh(rec)

    results = [_to_read(rec, category, activity) for rec, category, activity in new_recs]
    results.sort(key=lambda r: (-r.score, r.id))
    return results


def get_for_factory(db: Session, factory_id: int) -> list[RecommendationRead]:
    """Return the persisted recommendations for a factory, ranked by score.

    Reuses `hotspot_service.get_hotspots`'s 404 semantics (factory missing /
    no processes / not yet calculated). Returns an empty list (not 404) if
    the factory has been calculated but has zero hotspots.
    """

    hotspot_service.get_hotspots(db, factory_id)

    processes = process_service.list_all(db, factory_id=factory_id)
    process_ids = [process.id for process in processes]
    if not process_ids:
        return []

    stmt = (
        select(Recommendation, EmissionResult.category, EmissionResult.activity)
        .join(EmissionResult, Recommendation.hotspot_id == EmissionResult.id)
        .where(EmissionResult.process_id.in_(process_ids))
        .order_by(Recommendation.score.desc(), Recommendation.id.asc())
    )
    rows = db.execute(stmt).all()
    return [_to_read(rec, category, activity) for rec, category, activity in rows]
