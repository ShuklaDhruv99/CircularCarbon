"""Prioritized Action Plan routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.action_plan import ActionPlanRead
from app.services import action_plan_service

router = APIRouter(prefix="/api/action-plan", tags=["action-plan"])


@router.get("/factory/{factory_id}", response_model=ActionPlanRead)
def get_action_plan(factory_id: int, db: Session = Depends(get_db)) -> ActionPlanRead:
    return action_plan_service.get_action_plan(db, factory_id)
