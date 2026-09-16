from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.observation import ClimateObservation
from app.schemas.climate import ClimateObservationResponse


router = APIRouter(
    prefix="/api/v1/observations",
    tags=["Climate Observations"],
)


@router.get(
    "/",
    response_model=list[ClimateObservationResponse],
)
def get_observations(
    variable: str | None = None,
    source: str | None = None,
    dataset_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    min_lat: float | None = Query(
        default=None,
        ge=-90,
        le=90,
    ),
    max_lat: float | None = Query(
        default=None,
        ge=-90,
        le=90,
    ),
    min_lon: float | None = Query(
        default=None,
        ge=-180,
        le=180,
    ),
    max_lon: float | None = Query(
        default=None,
        ge=-180,
        le=180,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=10000,
    ),
    db: Session = Depends(get_db),
):
    query = db.query(
        ClimateObservation
    )

    if variable:
        query = query.filter(
            ClimateObservation.variable == variable
        )

    if source:
        query = query.filter(
            ClimateObservation.source == source
        )

    if dataset_id:
        query = query.filter(
            ClimateObservation.dataset_id == dataset_id
        )

    if start_time:
        query = query.filter(
            ClimateObservation.timestamp >= start_time
        )

    if end_time:
        query = query.filter(
            ClimateObservation.timestamp <= end_time
        )

    if min_lat is not None:
        query = query.filter(
            ClimateObservation.latitude >= min_lat
        )

    if max_lat is not None:
        query = query.filter(
            ClimateObservation.latitude <= max_lat
        )

    if min_lon is not None:
        query = query.filter(
            ClimateObservation.longitude >= min_lon
        )

    if max_lon is not None:
        query = query.filter(
            ClimateObservation.longitude <= max_lon
        )

    return (
        query
        .order_by(
            ClimateObservation.timestamp.desc()
        )
        .limit(limit)
        .all()
    )