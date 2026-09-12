"""Recommendation model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotspot_id: Mapped[int] = mapped_column(
        ForeignKey("emission_results.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    strategy: Mapped[str] = mapped_column(String, nullable=False)
    estimated_cost: Mapped[str] = mapped_column(String, nullable=False)
    co2_reduction: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    payback_period: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    hotspot: Mapped["EmissionResult"] = relationship(back_populates="recommendations")
