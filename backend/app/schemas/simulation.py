"""Pydantic schemas for the What-If simulation endpoint."""

from decimal import Decimal

from pydantic import BaseModel

from app.schemas.recommendation import RecommendationRead


class SimulationRequest(BaseModel):
    recommendation_ids: list[int]


class SimulationResult(BaseModel):
    factory_id: int
    baseline_co2e: Decimal
    projected_co2e: Decimal
    co2_reduction: Decimal
    reduction_percentage: Decimal
    total_implementation_cost: Decimal
    estimated_payback_months: Decimal | None
    applied_recommendations: list[RecommendationRead]
