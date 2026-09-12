"""Hotspot ranking: orders EmissionResult rows by CO2e and flags top contributors.

A row is a hotspot if its cumulative percentage contribution (running sum of
CO2e-descending rows, factory-wide) is <= 80%, i.e. the smallest set of top
contributors whose combined share reaches 80% of the factory total. The
first row that pushes the cumulative sum past 80% is still included. If the
factory total CO2e is 0, no rows are flagged as hotspots.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EmissionResult
from app.schemas.emission_result import HotspotRead
from app.services import factory_service, process_service
from app.services.emission_calculation_service import compute_percentages
from app.services.errors import NotFoundError

HOTSPOT_THRESHOLD = Decimal("80.00")


def get_hotspots(db: Session, factory_id: int) -> list[HotspotRead]:
    factory_service.get(db, factory_id)
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

    # CO2e descending; tie-break by id for determinism.
    ordered = sorted(results, key=lambda r: (-r.co2e, r.id))
    factory_total = sum((r.co2e for r in ordered), Decimal("0"))
    percentages = compute_percentages([r.co2e for r in ordered], factory_total)

    hotspots: list[HotspotRead] = []
    cumulative = Decimal("0.00")
    for result, percentage in zip(ordered, percentages):
        is_hotspot = factory_total > 0 and cumulative < HOTSPOT_THRESHOLD
        cumulative += percentage
        hotspots.append(
            HotspotRead(
                id=result.id,
                process_id=result.process_id,
                category=result.category,
                activity=result.activity,
                emission_factor=result.emission_factor,
                emission_factor_source=result.emission_factor_source,
                co2e=result.co2e,
                period=result.period,
                percentage=percentage,
                is_hotspot=is_hotspot,
            )
        )

    return hotspots
