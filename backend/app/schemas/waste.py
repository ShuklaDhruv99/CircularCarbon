"""Pydantic schemas for waste entries."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DisposalMethod = Literal["reused", "recycled", "sold", "landfilled", "other"]


class WasteBase(BaseModel):
    waste_type: str
    quantity: Decimal = Field(gt=0)
    unit: str
    disposal_method: DisposalMethod
    recycled_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    landfilled_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    reused_quantity: Decimal = Field(default=Decimal("0"), ge=0)


class WasteCreate(WasteBase):
    process_id: int


class WasteRead(WasteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    process_id: int
    created_at: datetime
