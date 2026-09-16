from pathlib import Path
from typing import Any

import cdsapi

from app.config import settings
from app.connectors.base import DataConnector


class ERA5Connector(DataConnector):

    def __init__(self):
        self.client = cdsapi.Client()

    def connect(self) -> bool:
        try:
            # Client initialization itself verifies
            # that the CDS configuration is available.
            return True
        except Exception:
            return False

    def fetch(
        self,
        year: int,
        month: int,
        day: int,
        output_file: str,
    ) -> str:

        variables = [
            "2m_temperature",
            "surface_pressure",
            "total_precipitation",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "surface_solar_radiation_downwards",
            "boundary_layer_height",
        ]

        request = {
            "product_type": "reanalysis",
            "variable": variables,
            "year": str(year),
            "month": f"{month:02d}",
            "day": f"{day:02d}",
            "time": [
                "00:00",
                "06:00",
                "12:00",
                "18:00",
            ],
            "data_format": "netcdf",
            "download_format": "unarchived",
        }

        output_path = Path(
            settings.data_raw_path
        ) / output_file

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client.retrieve(
            settings.cds_dataset,
            request,
            str(output_path),
        )

        return str(output_path)

    def validate(self, data: Any) -> bool:
        return data is not None

    def transform(self, data: Any) -> Any:
        return data