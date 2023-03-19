"""Example of trimming down CINE files and import them into cloud storage."""

import xarray as xr

from boilercv import get_8bit_images
from boilercv.gui import get_video_images
from boilercv.models.params import PARAMS


def main():
    source = PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine"
    images = xr.DataArray(
        list(get_8bit_images(get_video_images(source, start_frame=0, count=30)))
    )
    images.to_netcdf(PARAMS.paths.examples / f"{source.stem}.nc")


if __name__ == "__main__":
    main()
