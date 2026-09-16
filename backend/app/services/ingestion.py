from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.observation import ClimateObservation


def create_observation(
    db: Session,
    *,
    dataset_id: str,
    source: str,
    timestamp: datetime,
    latitude: float,
    longitude: float,
    variable: str,
    value: float,
    unit: str,
    quality_flag: str | None = None,
    spatial_resolution: str | None = None,
    temporal_resolution: str | None = None,
):
    """
    Create one normalized climate observation.
    """

    if value != value:  # NaN check
        return None

    observation = ClimateObservation(
        dataset_id=dataset_id,
        source=source,
        timestamp=timestamp,
        latitude=latitude,
        longitude=longitude,
        variable=variable,
        value=float(value),
        unit=unit,
        quality_flag=quality_flag,
        spatial_resolution=spatial_resolution,
        temporal_resolution=temporal_resolution,
    )

    db.add(observation)

    return observation


def save_observations(
    db: Session,
    observations: Iterable[dict],
) -> int:
    """
    Insert a collection of normalized observations.
    """

    count = 0

    for item in observations:
        observation = create_observation(
            db,
            **item,
        )

        if observation is not None:
            count += 1

    db.commit()

    return count