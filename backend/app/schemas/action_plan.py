"""Pydantic schemas for the Prioritized Action Plan endpoint."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.recommendation import RecommendationRead


class ActionPlanPhaseRead(BaseModel):
    phase: Literal["now", "next", "later"]
    recommendations: list[RecommendationRead]
    total_co2_reduction: Decimal
    total_implementation_cost: Decimal


class ActionPlanRead(BaseModel):
    factory_id: int
    now: ActionPlanPhaseRead
    next: ActionPlanPhaseRead
    later: ActionPlanPhaseRead
