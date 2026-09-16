from app.database import SessionLocal
from app.models.dataset import Dataset


def main():

    db = SessionLocal()

    try:

        existing = (
            db.query(Dataset)
            .filter(
                Dataset.dataset_id == "era5_india_test"
            )
            .first()
        )

        if existing:
            print("ERA5 test dataset already registered.")
            return

        dataset = Dataset(
            dataset_id="era5_india_test",
            name="ERA5 India Test Dataset",
            source="ECMWF_CDS",
            domain="Atmospheric & Surface Reanalysis",
            description=(
                "ERA5 reanalysis subset covering India "
                "at 0.25 degree spatial resolution "
                "for January 1, 2025."
            ),
            status="active",
        )

        db.add(dataset)
        db.commit()

        print("ERA5 test dataset registered successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()