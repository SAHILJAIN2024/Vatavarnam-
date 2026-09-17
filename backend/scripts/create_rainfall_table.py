from app.database import Base, engine

from app.models.rainfall import RainfallObservation


def main():
    print("Creating rainfall_observations table...")

    Base.metadata.create_all(
        bind=engine,
        tables=[
            RainfallObservation.__table__,
        ],
    )

    print("rainfall_observations table is ready.")


if __name__ == "__main__":
    main()