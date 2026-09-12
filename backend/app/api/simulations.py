"""What-If simulation routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.simulation import SimulationRequest, SimulationResult
from app.services import simulation_service

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("/factory/{factory_id}", response_model=SimulationResult)
def simulate_factory(
    factory_id: int, body: SimulationRequest, db: Session = Depends(get_db)
) -> SimulationResult:
    return simulation_service.simulate_for_factory(
        db, factory_id, body.recommendation_ids
    )
