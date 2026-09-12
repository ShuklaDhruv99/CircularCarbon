"""CRUD operations for factories."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Factory
from app.schemas.factory import FactoryCreate, FactoryUpdate
from app.services.errors import NotFoundError


def create(db: Session, data: FactoryCreate) -> Factory:
    factory = Factory(**data.model_dump())
    db.add(factory)
    db.commit()
    db.refresh(factory)
    return factory


def list_all(db: Session) -> list[Factory]:
    return list(db.scalars(select(Factory)).all())


def get(db: Session, factory_id: int) -> Factory:
    factory = db.get(Factory, factory_id)
    if factory is None:
        raise NotFoundError(f"Factory {factory_id} not found")
    return factory


def update(db: Session, factory_id: int, data: FactoryUpdate) -> Factory:
    factory = get(db, factory_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(factory, field, value)
    db.commit()
    db.refresh(factory)
    return factory


def delete(db: Session, factory_id: int) -> None:
    factory = get(db, factory_id)
    db.delete(factory)
    db.commit()
