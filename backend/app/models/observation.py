from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ClimateObservation(Base):
    __tablename__ = "climate_observations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    dataset_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    variable: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    quality_flag: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    spatial_resolution: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    temporal_resolution: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    geometry = mapped_column(
        Geometry(
            geometry_type="POINT",
            srid=4326,
        ),
        nullable=True,
    )