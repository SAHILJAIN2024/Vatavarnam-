from pathlib import Path
import zipfile
import cdsapi

OUTPUT_DIR = Path("../data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ARCHIVE_FILE = OUTPUT_DIR / "era5_india_test_download.zip"
OUTPUT_FILE = OUTPUT_DIR / "era5_india_test.nc"

client = cdsapi.Client()

request = {
    "product_type": "reanalysis",
    "variable": [
        "2m_temperature",
        "surface_pressure",
        "total_precipitation",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "surface_solar_radiation_downwards",
        "boundary_layer_height",
    ],
    "year": "2025",
    "month": "01",
    "day": ["01"],
    "time": [
        "00:00",
        "06:00",
        "12:00",
        "18:00",
    ],
    "area": [37.0, 68.0, 6.0, 97.5],
    "data_format": "netcdf",
}

print("Starting ERA5 download...")
print(f"Download archive: {ARCHIVE_FILE}")

client.retrieve(
    "reanalysis-era5-single-levels",
    request,
    str(ARCHIVE_FILE),
)

print("Download completed.")

print("\nInspecting downloaded archive...")

with zipfile.ZipFile(ARCHIVE_FILE, "r") as archive:
    files = archive.namelist()

    print("Files inside archive:")
    for file in files:
        print(" -", file)

    nc_files = [
        file for file in files
        if file.lower().endswith((".nc", ".nc4"))
    ]

    if not nc_files:
        raise RuntimeError(
            "No NetCDF file found inside the downloaded archive."
        )

    selected_file = nc_files[0]

    print(f"\nExtracting: {selected_file}")

    archive.extract(selected_file, OUTPUT_DIR)

    extracted_path = OUTPUT_DIR / selected_file

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    extracted_path.rename(OUTPUT_FILE)

print("\nERA5 NetCDF ready.")
print(f"Saved to: {OUTPUT_FILE}")

# Remove archive after successful extraction
ARCHIVE_FILE.unlink()

print("Temporary archive removed.")