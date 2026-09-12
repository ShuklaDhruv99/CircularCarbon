"""Waste model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Waste(Base):
    __tablename__ = "waste"

    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(
        ForeignKey("processes.id", ondelete="CASCADE"), nullable=False
    )
    waste_type: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    disposal_method: Mapped[str] = mapped_column(String, nullable=False)
    recycled_quantity: Mapped[Decimal] = mapped_column(
        Numeric, nullable=False, server_default=text("0")
    )
    landfilled_quantity: Mapped[Decimal] = mapped_column(
        Numeric, nullable=False, server_default=text("0")
    )
    reused_quantity: Mapped[Decimal] = mapped_column(
        Numeric, nullable=False, server_default=text("0")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    process: Mapped["Process"] = relationship(back_populates="waste")
