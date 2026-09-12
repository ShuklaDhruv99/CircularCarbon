"""Gemini-backed recommendation explanation routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.explanation import ExplanationRead
from app.services import explanation_service

router = APIRouter(prefix="/api/explanations", tags=["explanations"])


@router.post("/generate/{factory_id}", response_model=list[ExplanationRead])
def generate_explanations(
    factory_id: int, db: Session = Depends(get_db)
) -> list[ExplanationRead]:
    return explanation_service.generate_for_factory(db, factory_id)
