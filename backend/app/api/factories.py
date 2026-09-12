"""Factory CRUD routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.factory import FactoryCreate, FactoryRead, FactoryUpdate
from app.services import factory_service

router = APIRouter(prefix="/api/factories", tags=["factories"])


@router.post("", response_model=FactoryRead, status_code=status.HTTP_201_CREATED)
def create_factory(data: FactoryCreate, db: Session = Depends(get_db)) -> FactoryRead:
    return factory_service.create(db, data)


@router.get("", response_model=list[FactoryRead])
def list_factories(db: Session = Depends(get_db)) -> list[FactoryRead]:
    return factory_service.list_all(db)


@router.get("/{factory_id}", response_model=FactoryRead)
def get_factory(factory_id: int, db: Session = Depends(get_db)) -> FactoryRead:
    return factory_service.get(db, factory_id)


@router.patch("/{factory_id}", response_model=FactoryRead)
def update_factory(
    factory_id: int, data: FactoryUpdate, db: Session = Depends(get_db)
) -> FactoryRead:
    return factory_service.update(db, factory_id, data)


@router.delete("/{factory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factory(factory_id: int, db: Session = Depends(get_db)) -> None:
    factory_service.delete(db, factory_id)
