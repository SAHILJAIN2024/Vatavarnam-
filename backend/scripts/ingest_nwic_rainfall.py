from app.connectors.nwic_rainfall import NWICRainfallConnector
from app.database import SessionLocal
from app.models.rainfall import RainfallObservation


def main():
    connector = NWICRainfallConnector()

    print("Connecting to NWIC...")

    if not connector.connect():
        raise SystemExit(
            "Could not connect to NWIC API."
        )

    print("NWIC connection successful.")

    print("\nFetching Madhya Pradesh rainfall data...")

    records = connector.fetch(
        state="MADHYA PRADESH",
        limit=100,
    )

    print(f"Records received: {len(records)}")

    if not connector.validate(records):
        raise SystemExit(
            "NWIC response validation failed."
        )

    transformed = connector.transform(records)

    print(
        f"Records transformed: {len(transformed)}"
    )

    if not transformed:
        print("No rainfall records to ingest.")
        return

    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for item in transformed:
            existing = (
                db.query(RainfallObservation)
                .filter(
                    RainfallObservation.source_id
                    == item["source_id"]
                )
                .first()
            )

            if existing:
                skipped += 1
                continue

            observation = RainfallObservation(
                **item
            )

            db.add(observation)
            inserted += 1

        db.commit()

        print("\n===================================")
        print("NWIC RAINFALL INGESTION COMPLETE")
        print("===================================")

        print(f"Records received:  {len(records)}")
        print(f"Records transformed: {len(transformed)}")
        print(f"Records inserted:   {inserted}")
        print(f"Records skipped:    {skipped}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()