"""Convert CINE files to the NetCDF file format."""

from boilercv import EXAMPLE_FULL_CINE
from boilercv.data.video import prepare_dataset

NUM_FRAMES = 100


def main():
    destination = EXAMPLE_FULL_CINE.parent / f"{EXAMPLE_FULL_CINE.stem}.nc"
    ds = prepare_dataset(EXAMPLE_FULL_CINE, num_frames=NUM_FRAMES)
    ds.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
