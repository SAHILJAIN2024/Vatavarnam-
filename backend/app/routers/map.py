from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.observation import ClimateObservation


router = APIRouter(
    prefix="/api/v1/map",
    tags=["map"],
)


# Variables physically stored in the database.
STORED_VARIABLES = {
    "temperature_2m",
    "surface_pressure",
    "wind_u_10m",
    "wind_v_10m",
    "boundary_layer_height",
}


SUPPORTED_VARIABLES = STORED_VARIABLES | {
    "wind_speed",
}


@router.get("/grid")
def get_map_grid(
    variable: str = Query(
        "temperature_2m",
        description="Climate variable to visualize",
    ),
    timestamp: datetime | None = Query(
        None,
        description="Observation timestamp",
    ),
    db: Session = Depends(get_db),
):
    """
    Return the climate grid as GeoJSON.

    Supported variables:
        temperature_2m
        surface_pressure
        wind_u_10m
        wind_v_10m
        wind_speed
        boundary_layer_height
    """

    if variable not in SUPPORTED_VARIABLES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported climate variable",
                "supported_variables": sorted(
                    SUPPORTED_VARIABLES
                ),
            },
        )

    # --------------------------------------------------
    # Determine timestamp
    # --------------------------------------------------

    if timestamp is None:
        timestamp = db.scalar(
            select(
                func.max(
                    ClimateObservation.timestamp
                )
            ).where(
                ClimateObservation.dataset_id
                == "era5_india_test"
            )
        )

        if timestamp is None:
            raise HTTPException(
                status_code=404,
                detail="No climate observations found.",
            )

    # --------------------------------------------------
    # Derived wind speed
    # --------------------------------------------------

    if variable == "wind_speed":
        observations = db.execute(
            select(ClimateObservation)
            .where(
                ClimateObservation.dataset_id
                == "era5_india_test",
                ClimateObservation.timestamp
                == timestamp,
                ClimateObservation.variable.in_(
                    [
                        "wind_u_10m",
                        "wind_v_10m",
                    ]
                ),
            )
            .order_by(
                ClimateObservation.latitude.desc(),
                ClimateObservation.longitude.asc(),
            )
        ).scalars().all()

        grouped: dict[
            tuple[float, float],
            dict[str, float],
        ] = {}

        for observation in observations:
            key = (
                observation.latitude,
                observation.longitude,
            )

            if key not in grouped:
                grouped[key] = {}

            grouped[key][
                observation.variable
            ] = observation.value

        features = []

        for (
            latitude,
            longitude,
        ), values in grouped.items():

            u = values.get("wind_u_10m")
            v = values.get("wind_v_10m")

            if u is None or v is None:
                continue

            speed = (
                u * u + v * v
            ) ** 0.5

            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            longitude,
                            latitude,
                        ],
                    },
                    "properties": {
                        "dataset_id": "era5_india_test",
                        "source": "ECMWF_CDS",
                        "timestamp": timestamp.isoformat(),
                        "latitude": latitude,
                        "longitude": longitude,
                        "variable": "wind_speed",
                        "value": speed,
                        "unit": "m/s",
                    },
                }
            )

        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "variable": "wind_speed",
                "unit": "m/s",
                "timestamp": timestamp.isoformat(),
                "source": "ECMWF_CDS",
                "dataset_id": "era5_india_test",
                "derived": True,
            },
        }

    # --------------------------------------------------
    # Normal stored variables
    # --------------------------------------------------

    observations = db.execute(
        select(ClimateObservation)
        .where(
            ClimateObservation.dataset_id
            == "era5_india_test",
            ClimateObservation.timestamp
            == timestamp,
            ClimateObservation.variable
            == variable,
        )
        .order_by(
            ClimateObservation.latitude.desc(),
            ClimateObservation.longitude.asc(),
        )
    ).scalars().all()

    features = []

    for observation in observations:
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        observation.longitude,
                        observation.latitude,
                    ],
                },
                "properties": {
                    "id": observation.id,
                    "dataset_id": observation.dataset_id,
                    "source": observation.source,
                    "timestamp": observation.timestamp.isoformat(),
                    "latitude": observation.latitude,
                    "longitude": observation.longitude,
                    "variable": observation.variable,
                    "value": observation.value,
                    "unit": observation.unit,
                    "quality_flag": observation.quality_flag,
                    "spatial_resolution": observation.spatial_resolution,
                    "temporal_resolution": observation.temporal_resolution,
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "variable": variable,
            "unit": (
                observations[0].unit
                if observations
                else None
            ),
            "timestamp": (
                timestamp.isoformat()
                if timestamp
                else None
            ),
            "source": "ECMWF_CDS",
            "dataset_id": "era5_india_test",
            "derived": False,
        },
    }