from sqlalchemy import text

from app.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT
                    id,
                    latitude,
                    longitude,
                    ST_AsText(geometry) AS geometry
                FROM climate_observations
                WHERE geometry IS NOT NULL
                LIMIT 5
                """
            )
        )

        print("\n========== SPATIAL DATA ==========")

        for row in result:
            print(
                f"id={row.id}, "
                f"lat={row.latitude}, "
                f"lon={row.longitude}, "
                f"geometry={row.geometry}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()