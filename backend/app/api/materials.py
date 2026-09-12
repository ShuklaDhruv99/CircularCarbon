"""Material create/list/delete routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material import MaterialCreate, MaterialRead
from app.services import material_service

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.post("", response_model=MaterialRead, status_code=status.HTTP_201_CREATED)
def create_material(data: MaterialCreate, db: Session = Depends(get_db)) -> MaterialRead:
    return material_service.create(db, data)


@router.get("", response_model=list[MaterialRead])
def list_materials(
    process_id: int | None = None, db: Session = Depends(get_db)
) -> list[MaterialRead]:
    return material_service.list_all(db, process_id)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: int, db: Session = Depends(get_db)) -> None:
    material_service.delete(db, material_id)
