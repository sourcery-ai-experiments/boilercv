"""Trim down CINE files and import them into cloud storage."""

import xarray as xr

from boilercv import get_8bit_images
from boilercv.gui import get_video_images
from boilercv.models.params import PARAMS


def main():
    for source in PARAMS.paths.sources.iterdir():
        images = get_8bit_images(get_video_images(source, start_frame=0, count=120))
        data_array = xr.DataArray(images)
        data_array.to_netcdf(f"{PARAMS.paths.trimmed / source.stem}.nc")


if __name__ == "__main__":
    main()
