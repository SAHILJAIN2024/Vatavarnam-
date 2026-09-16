from pathlib import Path
import xarray as xr

file_path = Path("../data/raw/era5_india_test.nc")

print("Opening:", file_path)

dataset = xr.open_dataset(file_path, engine="netcdf4")

print("\n========== DATASET ==========")
print(dataset)

print("\n========== VARIABLES ==========")

for variable in dataset.data_vars:
    data = dataset[variable]

    print(
        f"{variable}: "
        f"dims={data.dims}, "
        f"shape={data.shape}, "
        f"units={data.attrs.get('units')}"
    )

print("\n========== COORDINATES ==========")

for coordinate in dataset.coords:
    values = dataset[coordinate].values

    print(
        f"{coordinate}: "
        f"size={values.size}, "
        f"first={values.flat[0]}, "
        f"last={values.flat[-1]}"
    )

dataset.close()