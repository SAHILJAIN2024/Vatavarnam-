from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Location Time Series"],
)


@router.get("/{latitude}/{longitude}/timeseries")
def get_location_timeseries(
    latitude: float,
    longitude: float,
    start_time: datetime | None = Query(
        default=None,
        description="Start of time range in UTC.",
    ),
    end_time: datetime | None = Query(
        default=None,
        description="End of time range in UTC.",
    ),
    variable: str | None = Query(
        default=None,
        description="Optional climate variable filter.",
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve the climate time series for the ERA5 grid point
    nearest to the requested latitude/longitude.
    """

    # ---------------------------------------------------------
    # 1. Validate coordinates
    # ---------------------------------------------------------

    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90.",
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180.",
        )

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be earlier than or equal to end_time.",
        )

    # ---------------------------------------------------------
    # 2. Find nearest ERA5 grid point
    # ---------------------------------------------------------

    nearest_query = text(
        """
        SELECT
            latitude,
            longitude,
            ST_Distance(
                geometry::geography,
                ST_SetSRID(
                    ST_MakePoint(:longitude, :latitude),
                    4326
                )::geography
            ) AS distance_meters
        FROM climate_observations
        WHERE geometry IS NOT NULL
        ORDER BY geometry <-> ST_SetSRID(
            ST_MakePoint(:longitude, :latitude),
            4326
        )
        LIMIT 1
        """
    )

    nearest = db.execute(
        nearest_query,
        {
            "latitude": latitude,
            "longitude": longitude,
        },
    ).mappings().first()

    if nearest is None:
        raise HTTPException(
            status_code=404,
            detail="No spatial climate observations found.",
        )

    nearest_latitude = nearest["latitude"]
    nearest_longitude = nearest["longitude"]
    distance_meters = float(nearest["distance_meters"])

    # ---------------------------------------------------------
    # 3. Retrieve time-series observations
    # ---------------------------------------------------------

    query = """
        SELECT
            timestamp,
            variable,
            value,
            unit,
            source,
            dataset_id,
            quality_flag,
            spatial_resolution,
            temporal_resolution
        FROM climate_observations
        WHERE latitude = :latitude
          AND longitude = :longitude
    """

    params = {
        "latitude": nearest_latitude,
        "longitude": nearest_longitude,
    }

    if start_time is not None:
        query += """
            AND timestamp >= :start_time
        """
        params["start_time"] = start_time

    if end_time is not None:
        query += """
            AND timestamp <= :end_time
        """
        params["end_time"] = end_time

    if variable is not None:
        query += """
            AND variable = :variable
        """
        params["variable"] = variable

    query += """
        ORDER BY timestamp ASC, variable ASC
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
            detail="No climate observations found for the requested location and time range.",
        )

    # ---------------------------------------------------------
    # 4. Group observations by timestamp
    # ---------------------------------------------------------

    time_series = {}

    for observation in observations:
        timestamp = observation["timestamp"].isoformat()

        if timestamp not in time_series:
            time_series[timestamp] = {}

        time_series[timestamp][observation["variable"]] = {
            "value": observation["value"],
            "unit": observation["unit"],
            "quality_flag": observation["quality_flag"],
            "spatial_resolution": observation["spatial_resolution"],
            "temporal_resolution": observation["temporal_resolution"],
        }

    # ---------------------------------------------------------
    # 5. Return structured response
    # ---------------------------------------------------------

    return {
        "requested_location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "nearest_grid_point": {
            "latitude": nearest_latitude,
            "longitude": nearest_longitude,
            "distance_meters": round(distance_meters, 2),
        },
        "source": observations[0]["source"],
        "dataset_id": observations[0]["dataset_id"],
        "start_time": observations[0]["timestamp"],
        "end_time": observations[-1]["timestamp"],
        "observation_count": len(observations),
        "time_points": len(time_series),
        "variables": sorted(
            {
                observation["variable"]
                for observation in observations
            }
        ),
        "time_series": time_series,
    }