from app.connectors.nwic_rainfall import NWICRainfallConnector


def main():
    connector = NWICRainfallConnector()

    print("Testing NWIC connection...")

    connected = connector.connect()

    print(f"Connected: {connected}")

    if not connected:
        raise SystemExit(
            "Could not connect to NWIC API."
        )

    print("\nFetching Gwalior rainfall data...")

    records = connector.fetch(
        state="MADHYA PRADESH",
        district="GWALIOR",
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

    for record in transformed[:3]:
        print("\n--- RECORD ---")

        for key, value in record.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()