"""Compress the video data in a NetCDF file.

Compression is slow for grayscale files of ~2GB size, but may work better for binarized
files.
"""

import xarray as xr

from boilercv import LARGE_EXAMPLES, LARGE_SOURCES
from boilercv.data import VIDEO


def main():
    source = sorted(LARGE_SOURCES.glob("*.nc"))[-1]
    destination = LARGE_EXAMPLES / f"{source.stem}.nc"
    with xr.open_dataset(source) as ds:
        ds.to_netcdf(path=destination, encoding={VIDEO: {"zlib": True}})


if __name__ == "__main__":
    main()
