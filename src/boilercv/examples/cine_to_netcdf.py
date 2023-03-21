"""Example of converting CINE files to the NetCDF file format."""


import xarray as xr

from boilercv import get_8bit_images
from boilercv.gui import (
    get_attrs_and_timestamps_from_header,
    get_header,
    get_video_images,
)
from boilercv.models.params import PARAMS


def main():
    source = PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine"
    header = get_header(source)
    attrs, timestamps = get_attrs_and_timestamps_from_header(header)
    images = xr.DataArray(
        data=list(get_8bit_images(get_video_images(source))),
        dims=("image", "y", "x"),
        coords={"image": timestamps},
        attrs=attrs,
    )
    images.to_netcdf(
        path=PARAMS.paths.examples / f"{source.stem}.nc",
        encoding={"__xarray_dataarray_variable__": {"zlib": True}},
    )


if __name__ == "__main__":
    main()
