"""Pydantic read schemas for emission calculation results."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EmissionResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    process_id: int
    category: str
    activity: str
    emission_factor: Decimal
    emission_factor_source: str | None
    co2e: Decimal
    period: str
    created_at: datetime


class CategoryBreakdown(BaseModel):
    category: str
    co2e: Decimal
    percentage: Decimal


class ProcessBreakdown(BaseModel):
    process_id: int
    process_name: str
    co2e: Decimal
    percentage: Decimal


class EmissionsBreakdownRead(BaseModel):
    factory_id: int
    factory_total_co2e: Decimal
    category_breakdown: list[CategoryBreakdown]
    process_breakdown: list[ProcessBreakdown]
    results: list[EmissionResultRead]


class HotspotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    process_id: int
    category: str
    activity: str
    emission_factor: Decimal
    emission_factor_source: str | None
    co2e: Decimal
    period: str
    percentage: Decimal
    is_hotspot: bool
