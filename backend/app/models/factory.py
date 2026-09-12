"""Factory model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Factory(Base):
    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    production_volume: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    production_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    assessment_period: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    processes: Mapped[list["Process"]] = relationship(
        back_populates="factory",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
