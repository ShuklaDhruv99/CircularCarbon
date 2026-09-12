"""Process CRUD routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.process import ProcessCreate, ProcessRead, ProcessUpdate
from app.services import process_service

router = APIRouter(prefix="/api/processes", tags=["processes"])


@router.post("", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
def create_process(data: ProcessCreate, db: Session = Depends(get_db)) -> ProcessRead:
    return process_service.create(db, data)


@router.get("", response_model=list[ProcessRead])
def list_processes(
    factory_id: int | None = None, db: Session = Depends(get_db)
) -> list[ProcessRead]:
    return process_service.list_all(db, factory_id)


@router.get("/{process_id}", response_model=ProcessRead)
def get_process(process_id: int, db: Session = Depends(get_db)) -> ProcessRead:
    return process_service.get(db, process_id)


@router.patch("/{process_id}", response_model=ProcessRead)
def update_process(
    process_id: int, data: ProcessUpdate, db: Session = Depends(get_db)
) -> ProcessRead:
    return process_service.update(db, process_id, data)


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(process_id: int, db: Session = Depends(get_db)) -> None:
    process_service.delete(db, process_id)
