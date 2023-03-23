"""Example of converting CINE files to the NetCDF file format."""

from dataclasses import asdict

import xarray as xr

from boilercv.data import assign_length_scales, prepare_images
from boilercv.models.params import PARAMS

NUM_FRAMES = 100


def main():
    source = PARAMS.paths.examples / "2022-11-30T13-41-00.cine"
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    images, cine_header = prepare_images(source, num_frames=NUM_FRAMES)
    images = assign_length_scales(images)
    dataset = xr.Dataset({images.name: images}, attrs=asdict(cine_header))
    dataset.to_netcdf(
        path=destination,
        # encoding={images.name: {"zlib": True}},
    )


if __name__ == "__main__":
    main()
