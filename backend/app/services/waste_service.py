"""Create/list/delete operations for waste entries."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Waste
from app.schemas.waste import WasteCreate
from app.services import process_service
from app.services.errors import NotFoundError


def create(db: Session, data: WasteCreate) -> Waste:
    process_service.get(db, data.process_id)

    waste = Waste(**data.model_dump())
    db.add(waste)
    db.commit()
    db.refresh(waste)
    return waste


def list_all(db: Session, process_id: int | None = None) -> list[Waste]:
    stmt = select(Waste)
    if process_id is not None:
        stmt = stmt.where(Waste.process_id == process_id)
    return list(db.scalars(stmt).all())


def delete(db: Session, waste_id: int) -> None:
    waste = db.get(Waste, waste_id)
    if waste is None:
        raise NotFoundError(f"Waste entry {waste_id} not found")
    db.delete(waste)
    db.commit()
