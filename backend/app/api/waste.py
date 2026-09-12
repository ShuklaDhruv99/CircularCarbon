"""Waste create/list/delete routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.waste import WasteCreate, WasteRead
from app.services import waste_service

router = APIRouter(prefix="/api/waste", tags=["waste"])


@router.post("", response_model=WasteRead, status_code=status.HTTP_201_CREATED)
def create_waste(data: WasteCreate, db: Session = Depends(get_db)) -> WasteRead:
    return waste_service.create(db, data)


@router.get("", response_model=list[WasteRead])
def list_waste(
    process_id: int | None = None, db: Session = Depends(get_db)
) -> list[WasteRead]:
    return waste_service.list_all(db, process_id)


@router.delete("/{waste_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_waste(waste_id: int, db: Session = Depends(get_db)) -> None:
    waste_service.delete(db, waste_id)
