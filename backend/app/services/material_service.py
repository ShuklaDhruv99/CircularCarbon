"""Create/list/delete operations for material entries."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Material
from app.schemas.material import MaterialCreate
from app.services import process_service
from app.services.errors import NotFoundError


def create(db: Session, data: MaterialCreate) -> Material:
    process_service.get(db, data.process_id)

    material = Material(**data.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def list_all(db: Session, process_id: int | None = None) -> list[Material]:
    stmt = select(Material)
    if process_id is not None:
        stmt = stmt.where(Material.process_id == process_id)
    return list(db.scalars(stmt).all())


def delete(db: Session, material_id: int) -> None:
    material = db.get(Material, material_id)
    if material is None:
        raise NotFoundError(f"Material entry {material_id} not found")
    db.delete(material)
    db.commit()
