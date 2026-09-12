"""Process model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Process(Base):
    __tablename__ = "processes"

    id: Mapped[int] = mapped_column(primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    process_type: Mapped[str | None] = mapped_column(String, nullable=True)
    production_volume: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    factory: Mapped["Factory"] = relationship(back_populates="processes")

    energy_consumption: Mapped[list["EnergyConsumption"]] = relationship(
        back_populates="process",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    materials: Mapped[list["Material"]] = relationship(
        back_populates="process",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    waste: Mapped[list["Waste"]] = relationship(
        back_populates="process",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    emission_results: Mapped[list["EmissionResult"]] = relationship(
        back_populates="process",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
