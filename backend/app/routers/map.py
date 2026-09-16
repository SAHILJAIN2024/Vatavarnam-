from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(
    prefix="/api/v1/map",
    tags=["Map"],
)


@router.get("/grid")
def get_climate_grid(
    timestamp: datetime | None = Query(
        default=None,
        description="UTC timestamp. If omitted, latest available timestamp is used.",
    ),
    variable: str | None = Query(
        default=None,
        description="Optional variable to visualize.",
    ),
    db: Session = Depends(get_db),
):
    """
    Return climate grid observations as GeoJSON.

    Each feature represents one ERA5 grid point.
    """

    # ---------------------------------------------------------
    # 1. Determine timestamp
    # ---------------------------------------------------------

    if timestamp is None:
        timestamp_query = text(
            """
            SELECT MAX(timestamp)
            FROM climate_observations
            """
        )

        selected_timestamp = db.execute(
            timestamp_query
        ).scalar()

    else:
        selected_timestamp = timestamp

    if selected_timestamp is None:
        raise HTTPException(
            status_code=404,
            detail="No climate observations available.",
        )

    # ---------------------------------------------------------
    # 2. Retrieve grid
    # ---------------------------------------------------------

    query = """
        SELECT
            id,
            latitude,
            longitude,
            variable,
            value,
            unit,
            source,
            dataset_id,
            quality_flag,
            spatial_resolution,
            temporal_resolution
        FROM climate_observations
        WHERE timestamp = :timestamp
    """

    params = {
        "timestamp": selected_timestamp,
    }

    if variable is not None:
        query += """
            AND variable = :variable
        """

        params["variable"] = variable

    query += """
        ORDER BY latitude DESC, longitude ASC
    """

    observations = (
        db.execute(
            text(query),
            params,
        )
        .mappings()
        .all()
    )

    if not observations:
        raise HTTPException(
            status_code=404,
            detail="No grid observations found.",
        )

    # ---------------------------------------------------------
    # 3. Convert observations to GeoJSON
    # ---------------------------------------------------------

    features = []

    for observation in observations:
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        observation["longitude"],
                        observation["latitude"],
                    ],
                },
                "properties": {
                    "id": observation["id"],
                    "latitude": observation["latitude"],
                    "longitude": observation["longitude"],
                    "variable": observation["variable"],
                    "value": observation["value"],
                    "unit": observation["unit"],
                    "source": observation["source"],
                    "dataset_id": observation["dataset_id"],
                    "quality_flag": observation["quality_flag"],
                    "spatial_resolution": observation[
                        "spatial_resolution"
                    ],
                    "temporal_resolution": observation[
                        "temporal_resolution"
                    ],
                },
            }
        )

    # ---------------------------------------------------------
    # 4. Return GeoJSON FeatureCollection
    # ---------------------------------------------------------

    return {
        "type": "FeatureCollection",
        "metadata": {
            "timestamp": selected_timestamp,
            "variable": variable,
            "feature_count": len(features),
            "source": observations[0]["source"],
            "dataset_id": observations[0]["dataset_id"],
            "spatial_resolution": observations[0][
                "spatial_resolution"
            ],
            "temporal_resolution": observations[0][
                "temporal_resolution"
            ],
        },
        "features": features,
    }