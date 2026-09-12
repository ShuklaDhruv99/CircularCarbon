"""EmissionResult model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmissionResult(Base):
    __tablename__ = "emission_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(
        ForeignKey("processes.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String, nullable=False)
    activity: Mapped[str] = mapped_column(String, nullable=False)
    emission_factor: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    emission_factor_source: Mapped[str | None] = mapped_column(String, nullable=True)
    co2e: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    process: Mapped["Process"] = relationship(back_populates="emission_results")

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="hotspot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
