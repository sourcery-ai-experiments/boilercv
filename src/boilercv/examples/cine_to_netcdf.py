"""Example of converting CINE files to the NetCDF file format."""


from pathlib import Path

from boilercv.data import assign_length_scales, prepare_dataset
from boilercv.models.params import PARAMS

NUM_FRAMES = 100


def main():
    source = Path("C:/Users/Blake/Desktop/2022-11-30T13-41-00.cine")
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    dataset = prepare_dataset(source, num_frames=NUM_FRAMES)
    assign_length_scales(dataset)
    dataset.to_netcdf(
        path=destination,
        # encoding={images.name: {"zlib": True}},
    )


if __name__ == "__main__":
    main()
