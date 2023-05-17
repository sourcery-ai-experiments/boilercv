"""Convert CINE files to the NetCDF file format."""

from boilercv.data.video import prepare_dataset
from boilercv.examples import EXAMPLE_NUM_FRAMES
from boilercv.models.params import PARAMS


def main():
    destination = (
        PARAMS.local_paths.large_examples
        / f"{PARAMS.local_paths.large_example_cine.stem}.nc"
    )
    ds = prepare_dataset(
        PARAMS.local_paths.large_example_cine, num_frames=EXAMPLE_NUM_FRAMES
    )
    ds.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
