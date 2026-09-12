"""Emission calculation, breakdown, and hotspot routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.emission_result import EmissionsBreakdownRead, HotspotRead
from app.services import emission_calculation_service, hotspot_service

router = APIRouter(prefix="/api/emissions", tags=["emissions"])


@router.post("/calculate/{factory_id}", response_model=EmissionsBreakdownRead)
def calculate_emissions(
    factory_id: int, db: Session = Depends(get_db)
) -> EmissionsBreakdownRead:
    return emission_calculation_service.calculate_for_factory(db, factory_id)


@router.get("/factory/{factory_id}", response_model=EmissionsBreakdownRead)
def get_factory_emissions(
    factory_id: int, db: Session = Depends(get_db)
) -> EmissionsBreakdownRead:
    return emission_calculation_service.get_breakdown(db, factory_id)


@router.get("/hotspots/{factory_id}", response_model=list[HotspotRead])
def get_hotspots(factory_id: int, db: Session = Depends(get_db)) -> list[HotspotRead]:
    return hotspot_service.get_hotspots(db, factory_id)
