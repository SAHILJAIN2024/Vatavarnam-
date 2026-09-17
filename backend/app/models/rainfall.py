from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RainfallObservation(Base):
    __tablename__ = "rainfall_observations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    observation_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    daily_actual_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    daily_normal_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    daily_departure_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    daily_category: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    weekly_actual_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    weekly_normal_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    weekly_departure_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    weekly_category: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    cumulative_actual_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    cumulative_normal_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    cumulative_departure_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    cumulative_category: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    monthly_actual_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    monthly_normal_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    monthly_departure_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    monthly_category: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )