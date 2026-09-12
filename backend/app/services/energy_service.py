"""Create/list/delete operations for energy consumption entries."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EnergyConsumption
from app.schemas.energy_consumption import EnergyConsumptionCreate
from app.services import process_service
from app.services.errors import NotFoundError


def create(db: Session, data: EnergyConsumptionCreate) -> EnergyConsumption:
    process_service.get(db, data.process_id)

    energy = EnergyConsumption(**data.model_dump())
    db.add(energy)
    db.commit()
    db.refresh(energy)
    return energy


def list_all(db: Session, process_id: int | None = None) -> list[EnergyConsumption]:
    stmt = select(EnergyConsumption)
    if process_id is not None:
        stmt = stmt.where(EnergyConsumption.process_id == process_id)
    return list(db.scalars(stmt).all())


def delete(db: Session, energy_id: int) -> None:
    energy = db.get(EnergyConsumption, energy_id)
    if energy is None:
        raise NotFoundError(f"Energy consumption entry {energy_id} not found")
    db.delete(energy)
    db.commit()
