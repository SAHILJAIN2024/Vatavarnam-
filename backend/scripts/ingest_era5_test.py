from pathlib import Path

import xarray as xr
from sqlalchemy import text

from app.database import SessionLocal
from app.services.ingestion import save_observations


FILE_PATH = Path("../data/raw/era5_india_test.nc")

DATASET_ID = "era5_india_test"
SOURCE = "ECMWF_CDS"

VARIABLE_MAP = {
    "t2m": {
        "name": "temperature_2m",
        "unit": "K",
    },
    "sp": {
        "name": "surface_pressure",
        "unit": "Pa",
    },
    "u10": {
        "name": "wind_u_10m",
        "unit": "m/s",
    },
    "v10": {
        "name": "wind_v_10m",
        "unit": "m/s",
    },
    "blh": {
        "name": "boundary_layer_height",
        "unit": "m",
    },
}


def main():
    print("Opening ERA5 dataset...")

    dataset = xr.open_dataset(
        FILE_PATH,
        engine="netcdf4",
    )

    print(dataset)

    time_dim = "valid_time"
    lat_dim = "latitude"
    lon_dim = "longitude"

    # ---------------------------------------------------------
    # Validate dimensions
    # ---------------------------------------------------------

    required_dims = {
        time_dim,
        lat_dim,
        lon_dim,
    }

    missing_dims = required_dims - set(dataset.dims)

    if missing_dims:
        raise RuntimeError(
            f"Missing required dimensions: {missing_dims}"
        )

    # ---------------------------------------------------------
    # Validate variables
    # ---------------------------------------------------------

    available_variables = set(dataset.data_vars)

    variables = [
        variable
        for variable in VARIABLE_MAP
        if variable in available_variables
    ]

    if not variables:
        raise RuntimeError(
            "None of the expected ERA5 variables were found."
        )

    print("\nVariables to ingest:")

    for variable in variables:
        print(f" - {variable}")

    # ---------------------------------------------------------
    # Coordinates
    # ---------------------------------------------------------

    times = dataset[time_dim].values
    latitudes = dataset[lat_dim].values
    longitudes = dataset[lon_dim].values

    print("\nDataset dimensions:")
    print(f"Times:      {len(times)}")
    print(f"Latitudes:  {len(latitudes)}")
    print(f"Longitudes: {len(longitudes)}")

    total_expected = (
        len(times)
        * len(latitudes)
        * len(longitudes)
        * len(variables)
    )

    print(f"\nExpected observations: {total_expected:,}")

    # ---------------------------------------------------------
    # Build observations
    # ---------------------------------------------------------

    observations = []

    for variable in variables:

        metadata = VARIABLE_MAP[variable]

        data = dataset[variable]

        print(
            f"\nProcessing {variable} "
            f"({data.shape})..."
        )

        for time_index, timestamp in enumerate(times):

            for lat_index, latitude in enumerate(latitudes):

                values = data.isel(
                    {
                        time_dim: time_index,
                        lat_dim: lat_index,
                    }
                ).values

                for lon_index, longitude in enumerate(longitudes):

                    value = values[lon_index]

                    if value != value:
                        continue

                    observations.append(
                        {
                            "dataset_id": DATASET_ID,
                            "source": SOURCE,
                            "timestamp": timestamp.astype("datetime64[us]").item(),
                            "latitude": float(latitude),
                            "longitude": float(longitude),
                            "variable": metadata["name"],
                            "value": float(value),
                            "unit": metadata["unit"],
                            "quality_flag": "raw",
                            "spatial_resolution": "0.25 degree",
                            "temporal_resolution": "6 hourly",
                        }
                    )

    print(
        f"\nPrepared {len(observations):,} observations."
    )

    # ---------------------------------------------------------
    # Database insertion
    # ---------------------------------------------------------

    db = SessionLocal()

    try:

        print("Inserting observations into PostGIS...")

        count = save_observations(
            db,
            observations,
        )

        print(
            f"Successfully inserted {count:,} observations."
        )

    finally:
        db.close()
        dataset.close()

    print("\nERA5 ingestion completed.")


if __name__ == "__main__":
    main()