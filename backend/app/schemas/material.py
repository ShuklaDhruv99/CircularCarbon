"""Pydantic schemas for material entries."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MaterialBase(BaseModel):
    material_name: str
    quantity: Decimal = Field(gt=0)
    unit: str
    recycled_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    source: str | None = None


class MaterialCreate(MaterialBase):
    process_id: int


class MaterialRead(MaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    process_id: int
    created_at: datetime
