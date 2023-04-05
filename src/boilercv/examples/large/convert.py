"""Convert CINE files to the NetCDF file format."""

from boilercv.data.video import prepare_dataset
from boilercv.models.paths import LOCAL_PATHS

NUM_FRAMES = 100


def main():
    destination = (
        LOCAL_PATHS.large_examples / f"{LOCAL_PATHS.large_example_cine.stem}.nc"
    )
    ds = prepare_dataset(LOCAL_PATHS.large_example_cine, num_frames=NUM_FRAMES)
    ds.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
