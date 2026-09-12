"""Pydantic schemas for processes."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.energy_consumption import EnergyConsumptionRead
from app.schemas.material import MaterialRead
from app.schemas.waste import WasteRead


class ProcessBase(BaseModel):
    name: str
    process_type: str | None = None
    production_volume: Decimal | None = None


class ProcessCreate(ProcessBase):
    factory_id: int


class ProcessUpdate(BaseModel):
    name: str | None = None
    process_type: str | None = None
    production_volume: Decimal | None = None


class ProcessRead(ProcessBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factory_id: int
    created_at: datetime
    energy_consumption: list[EnergyConsumptionRead] = []
    materials: list[MaterialRead] = []
    waste: list[WasteRead] = []
