from datetime import datetime

from pydantic import BaseModel, Field


class ClimateObservationCreate(BaseModel):
    dataset_id: str
    source: str

    timestamp: datetime

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )

    variable: str
    value: float
    unit: str

    quality_flag: str | None = None
    spatial_resolution: str | None = None
    temporal_resolution: str | None = None


class ClimateObservationResponse(
    ClimateObservationCreate
):
    id: int

    class Config:
        from_attributes = True