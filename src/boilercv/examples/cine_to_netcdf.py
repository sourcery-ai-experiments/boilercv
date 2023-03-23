"""Example of converting CINE files to the NetCDF file format."""

import xarray as xr

from boilercv.models.params import PARAMS
from boilercv.video.cine import load_cine


def main():
    source = PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine"
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    images = load_cine(source)
    dataset = xr.Dataset({images.name: images})
    dataset.to_netcdf(
        path=destination,
        # encoding={images.name: {"zlib": True}},
    )


if __name__ == "__main__":
    main()
