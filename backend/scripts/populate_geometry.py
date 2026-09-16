from sqlalchemy import text

from app.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        print("Populating PostGIS geometry...")

        result = db.execute(
            text(
                """
                UPDATE climate_observations
                SET geometry = ST_SetSRID(
                    ST_MakePoint(longitude, latitude),
                    4326
                )
                WHERE geometry IS NULL
                """
            )
        )

        db.commit()

        print(
            f"Updated {result.rowcount:,} observations."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()