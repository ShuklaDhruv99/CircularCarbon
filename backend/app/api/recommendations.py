"""Circular recommendation generation and retrieval routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recommendation import RecommendationRead
from app.services import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post("/generate/{factory_id}", response_model=list[RecommendationRead])
def generate_recommendations(
    factory_id: int, db: Session = Depends(get_db)
) -> list[RecommendationRead]:
    return recommendation_service.generate_for_factory(db, factory_id)


@router.get("/factory/{factory_id}", response_model=list[RecommendationRead])
def get_factory_recommendations(
    factory_id: int, db: Session = Depends(get_db)
) -> list[RecommendationRead]:
    return recommendation_service.get_for_factory(db, factory_id)
