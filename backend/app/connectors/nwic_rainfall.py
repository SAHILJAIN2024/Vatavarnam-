from datetime import date
from typing import Any

import httpx

from app.connectors.base import DataConnector


class NWICRainfallConnector(DataConnector):
    BASE_URL = "https://nwdp.nwic.gov.in/api/3/action/datastore_search"

    RESOURCE_ID = "8752174f-1d17-4aaf-8058-2eb396f50157"

    def connect(self) -> bool:
        try:
            response = httpx.get(
                self.BASE_URL,
                params={
                    "resource_id": self.RESOURCE_ID,
                    "limit": 1,
                },
                timeout=30.0,
            )

            response.raise_for_status()

            data = response.json()

            return bool(
                data.get("success") is True
                and "result" in data
            )

        except Exception:
            return False

    def fetch(
    self,
    state: str | None = None,
    district: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:

        import json

        all_records: list[dict[str, Any]] = []
        offset = 0

        while True:
            params: dict[str, Any] = {
            "resource_id": self.RESOURCE_ID,
            "limit": limit,
            "offset": offset,
        }

            filters: dict[str, str] = {}

            if state:
                filters["State"] = state

            if district:
                filters["District"] = district

            if filters:
                params["filters"] = json.dumps(filters)

            response = httpx.get(
                self.BASE_URL,
                params=params,
                timeout=60.0,
            )

            response.raise_for_status()

            payload = response.json()

            if payload.get("success") is not True:
                raise RuntimeError(
                    "NWIC API returned an unsuccessful response."
                )

            records = (
                payload
                .get("result", {})
                .get("records", [])
            )

            if not records:
                break

            all_records.extend(records)

            print(
                f"Fetched {len(records)} records "
                f"(total: {len(all_records)})"
            )

            if len(records) < limit:
                break

            offset += limit

        return all_records
    
    @staticmethod
    def _float(value: Any) -> float | None:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

            value = value.replace("%", "")

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _date(value: Any) -> date | None:
        if value is None:
            return None

        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return None

    def validate(self, data: Any) -> bool:
        if not isinstance(data, list):
            return False

        if not data:
            return True

        required = {
            "State",
            "District",
            "Date",
            "Daily Actual",
            "Daily Normal",
            "Daily Departure Per",
            "Daily Category",
        }

        return required.issubset(data[0].keys())

    def transform(
        self,
        data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        transformed = []

        for record in data:
            observation_date = self._date(record.get("Date"))

            if observation_date is None:
                continue

            transformed.append(
                {
                    "source_id": record.get("_id"),

                    "state": str(
                        record.get("State", "")
                    ).strip(),

                    "district": str(
                        record.get("District", "")
                    ).strip(),

                    "observation_date": observation_date,

                    "daily_actual_mm": self._float(
                        record.get("Daily Actual")
                    ),

                    "daily_normal_mm": self._float(
                        record.get("Daily Normal")
                    ),

                    "daily_departure_percent": self._float(
                        record.get("Daily Departure Per")
                    ),

                    "daily_category": record.get(
                        "Daily Category"
                    ),

                    "weekly_actual_mm": self._float(
                        record.get("Weekly \nActual")
                    ),

                    "weekly_normal_mm": self._float(
                        record.get("Weekly Normal")
                    ),

                    "weekly_departure_percent": self._float(
                        record.get("Weekly Departure Per")
                    ),

                    "weekly_category": record.get(
                        "Weekly Category"
                    ),

                    "cumulative_actual_mm": self._float(
                        record.get("Cumulative Actual")
                    ),

                    "cumulative_normal_mm": self._float(
                        record.get("Cumulative Normal")
                    ),

                    "cumulative_departure_percent": self._float(
                        record.get("Cumulative Departue Per")
                    ),

                    "cumulative_category": record.get(
                        "Cumulative \nCategory"
                    ),

                    "monthly_actual_mm": self._float(
                        record.get("Monthly Acutual")
                    ),

                    "monthly_normal_mm": self._float(
                        record.get("Monthly Normal")
                    ),

                    "monthly_departure_percent": self._float(
                        record.get("Monthly \nDeparture Per")
                    ),

                    "monthly_category": record.get(
                        "Monthly Category"
                    ),
                }
            )

        return transformed