"""Pydantic read schema for circular recommendations."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

Strategy = Literal[
    "reduce", "reuse", "recycle", "substitute", "recover", "process_optimization"
]
CostTier = Literal["low", "medium", "high"]


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotspot_id: int
    hotspot_category: str
    """The parent hotspot's `EmissionResult.category`, for display context."""
    hotspot_activity: str
    """The parent hotspot's `EmissionResult.activity`, for display context."""
    title: str
    description: str
    strategy: Strategy
    estimated_cost: CostTier
    co2_reduction: Decimal
    payback_period: Decimal | None
    score: Decimal | None
    created_at: datetime
