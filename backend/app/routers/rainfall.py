from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rainfall import RainfallObservation


router = APIRouter(
    prefix="/api/v1/rainfall",
    tags=["Rainfall"],
)


def serialize_rainfall(
    observation: RainfallObservation,
) -> dict:
    return {
        "id": observation.id,
        "source_id": observation.source_id,

        "state": observation.state,
        "district": observation.district,
        "date": observation.observation_date.isoformat(),

        "daily": {
            "actual_mm": observation.daily_actual_mm,
            "normal_mm": observation.daily_normal_mm,
            "departure_percent": observation.daily_departure_percent,
            "category": observation.daily_category,
        },

        "weekly": {
            "actual_mm": observation.weekly_actual_mm,
            "normal_mm": observation.weekly_normal_mm,
            "departure_percent": observation.weekly_departure_percent,
            "category": observation.weekly_category,
        },

        "cumulative": {
            "actual_mm": observation.cumulative_actual_mm,
            "normal_mm": observation.cumulative_normal_mm,
            "departure_percent": observation.cumulative_departure_percent,
            "category": observation.cumulative_category,
        },

        "monthly": {
            "actual_mm": observation.monthly_actual_mm,
            "normal_mm": observation.monthly_normal_mm,
            "departure_percent": observation.monthly_departure_percent,
            "category": observation.monthly_category,
        },

        "source": {
            "provider": "NWIC",
            "dataset": "NWIC / IMD Rainfall",
            "unit": "mm",
        },
    }


@router.get(
    "/district/{state}/{district}",
)
def get_district_rainfall(
    state: str,
    district: str,
    db: Session = Depends(get_db),
):
    observations = (
        db.query(RainfallObservation)
        .filter(
            RainfallObservation.state.ilike(state),
            RainfallObservation.district.ilike(district),
        )
        .order_by(
            RainfallObservation.observation_date.asc()
        )
        .all()
    )

    if not observations:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "No rainfall data found.",
                "state": state,
                "district": district,
            },
        )

    return {
        "state": observations[0].state,
        "district": observations[0].district,
        "observation_count": len(observations),
        "start_date": observations[0].observation_date.isoformat(),
        "end_date": observations[-1].observation_date.isoformat(),
        "records": [
            serialize_rainfall(observation)
            for observation in observations
        ],
    }


@router.get(
    "/latest/{state}/{district}",
)
def get_latest_district_rainfall(
    state: str,
    district: str,
    db: Session = Depends(get_db),
):
    observation = (
        db.query(RainfallObservation)
        .filter(
            RainfallObservation.state.ilike(state),
            RainfallObservation.district.ilike(district),
        )
        .order_by(
            RainfallObservation.observation_date.desc()
        )
        .first()
    )

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "No rainfall data found.",
                "state": state,
                "district": district,
            },
        )

    return serialize_rainfall(observation)


@router.get("/map")
def get_rainfall_map(
    state: str | None = None,
    observation_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(RainfallObservation)

    if state:
        query = query.filter(
            RainfallObservation.state.ilike(state)
        )

    if observation_date:
        query = query.filter(
            RainfallObservation.observation_date
            == observation_date
        )

    observations = (
        query
        .order_by(
            RainfallObservation.observation_date.desc()
        )
        .all()
    )

    return {
        "source": "NWIC",
        "dataset": "NWIC / IMD Rainfall",
        "observation_count": len(observations),
        "has_coordinates": False,
        "records": [
            serialize_rainfall(observation)
            for observation in observations
        ],
    }