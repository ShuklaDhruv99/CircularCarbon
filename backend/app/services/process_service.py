"""CRUD operations for processes."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Process
from app.schemas.process import ProcessCreate, ProcessUpdate
from app.services import factory_service
from app.services.errors import NotFoundError


def create(db: Session, data: ProcessCreate) -> Process:
    factory_service.get(db, data.factory_id)

    process = Process(**data.model_dump())
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


def list_all(db: Session, factory_id: int | None = None) -> list[Process]:
    stmt = select(Process)
    if factory_id is not None:
        stmt = stmt.where(Process.factory_id == factory_id)
    return list(db.scalars(stmt).all())


def get(db: Session, process_id: int) -> Process:
    process = db.get(Process, process_id)
    if process is None:
        raise NotFoundError(f"Process {process_id} not found")
    return process


def update(db: Session, process_id: int, data: ProcessUpdate) -> Process:
    process = get(db, process_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(process, field, value)
    db.commit()
    db.refresh(process)
    return process


def delete(db: Session, process_id: int) -> None:
    process = get(db, process_id)
    db.delete(process)
    db.commit()
