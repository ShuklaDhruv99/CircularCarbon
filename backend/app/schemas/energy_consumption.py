"""Pydantic schemas for energy consumption entries."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EnergyType = Literal[
    "electricity",
    "natural_gas",
    "diesel",
    "coal",
    "other",
    "renewable_electricity",
]


class EnergyConsumptionBase(BaseModel):
    energy_type: EnergyType
    quantity: Decimal = Field(gt=0)
    unit: str
    period: str


class EnergyConsumptionCreate(EnergyConsumptionBase):
    process_id: int


class EnergyConsumptionRead(EnergyConsumptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    process_id: int
    created_at: datetime
