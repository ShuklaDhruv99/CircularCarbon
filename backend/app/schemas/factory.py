"""Pydantic schemas for factories."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.process import ProcessRead

Industry = Literal[
    "Metal Manufacturing",
    "Textile Manufacturing",
    "Food Processing",
    "Electronics Manufacturing",
    "Chemical Manufacturing",
    "Plastics & Rubber",
    "Paper & Packaging",
    "Pharmaceuticals",
    "Automotive Manufacturing",
    "Construction Materials",
    "Other Manufacturing",
]


class FactoryBase(BaseModel):
    name: str
    industry: Industry
    location: str | None = None
    production_volume: Decimal | None = None
    production_unit: str | None = None
    assessment_period: str | None = None


class FactoryCreate(FactoryBase):
    pass


class FactoryUpdate(BaseModel):
    name: str | None = None
    industry: Industry | None = None
    location: str | None = None
    production_volume: Decimal | None = None
    production_unit: str | None = None
    assessment_period: str | None = None


class FactoryRead(FactoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    processes: list[ProcessRead] = []
