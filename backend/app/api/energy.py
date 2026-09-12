"""Energy consumption create/list/delete routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.energy_consumption import EnergyConsumptionCreate, EnergyConsumptionRead
from app.services import energy_service

router = APIRouter(prefix="/api/energy", tags=["energy"])


@router.post("", response_model=EnergyConsumptionRead, status_code=status.HTTP_201_CREATED)
def create_energy(
    data: EnergyConsumptionCreate, db: Session = Depends(get_db)
) -> EnergyConsumptionRead:
    return energy_service.create(db, data)


@router.get("", response_model=list[EnergyConsumptionRead])
def list_energy(
    process_id: int | None = None, db: Session = Depends(get_db)
) -> list[EnergyConsumptionRead]:
    return energy_service.list_all(db, process_id)


@router.delete("/{energy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_energy(energy_id: int, db: Session = Depends(get_db)) -> None:
    energy_service.delete(db, energy_id)
