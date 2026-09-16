from datetime import datetime

import numpy as np
import xarray as xr


VARIABLE_MAP = {
    "t2m": {
        "name": "temperature_2m",
        "unit": "K",
    },
    "sp": {
        "name": "surface_pressure",
        "unit": "Pa",
    },
    "tp": {
        "name": "precipitation",
        "unit": "m",
    },
    "u10": {
        "name": "wind_u_10m",
        "unit": "m/s",
    },
    "v10": {
        "name": "wind_v_10m",
        "unit": "m/s",
    },
    "ssrd": {
        "name": "solar_radiation_downwards",
        "unit": "J/m²",
    },
    "blh": {
        "name": "boundary_layer_height",
        "unit": "m",
    },
}


def detect_variable_name(dataset: xr.Dataset, variable: str) -> str | None:
    """
    Find the ERA5 variable in the NetCDF dataset.
    """

    if variable in dataset.data_vars:
        return variable

    return None


def process_era5_file(
    file_path: str,
    dataset_id: str = "era5",
    source: str = "ECMWF_CDS",
):
    """
    Convert an ERA5 NetCDF file into normalized observations.

    This function intentionally returns dictionaries instead
    of writing directly to the database.
    """

    dataset = xr.open_dataset(file_path)

    observations = []

    for source_variable, metadata in VARIABLE_MAP.items():

        actual_variable = detect_variable_name(
            dataset,
            source_variable,
        )

        if actual_variable is None:
            continue

        variable_data = dataset[actual_variable]

        dimensions = list(variable_data.dims)

        time_dimension = next(
            (
                dimension
                for dimension in dimensions
                if dimension.lower() in {"time", "valid_time"}
            ),
            None,
        )

        latitude_dimension = next(
            (
                dimension
                for dimension in dimensions
                if dimension.lower() in {"latitude", "lat"}
            ),
            None,
        )

        longitude_dimension = next(
            (
                dimension
                for dimension in dimensions
                if dimension.lower() in {"longitude", "lon"}
            ),
            None,
        )

        if not all(
            [
                time_dimension,
                latitude_dimension,
                longitude_dimension,
            ]
        ):
            continue

        for timestamp in variable_data[time_dimension].values:

            timestamp = np.datetime64(timestamp).astype(
                "datetime64[us]"
            ).astype(datetime)

            for latitude in variable_data[latitude_dimension].values:

                for longitude in variable_data[longitude_dimension].values:

                    value = variable_data.sel(
                        {
                            time_dimension: timestamp,
                            latitude_dimension: latitude,
                            longitude_dimension: longitude,
                        },
                        method="nearest",
                    ).values

                    if np.ndim(value) != 0:
                        continue

                    value = float(value)

                    if np.isnan(value):
                        continue

                    observations.append(
                        {
                            "dataset_id": dataset_id,
                            "source": source,
                            "timestamp": timestamp,
                            "latitude": float(latitude),
                            "longitude": float(longitude),
                            "variable": metadata["name"],
                            "value": value,
                            "unit": metadata["unit"],
                            "quality_flag": "raw",
                        }
                    )

    dataset.close()

    return observations