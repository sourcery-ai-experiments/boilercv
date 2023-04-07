"""Decompress sources to local storage."""


import xarray as xr
from loguru import logger

from boilercv.data import HEADER, VIDEO
from boilercv.data.sets import ALL_NAMES
from boilercv.models.params import LOCAL_PATHS, PARAMS


def main():
    logger.info("start decompress")
    for source_name in ALL_NAMES:
        destination = LOCAL_PATHS.uncompressed_sources / f"{source_name}.nc"
        if destination.exists():
            continue
        source = PARAMS.paths.sources / f"{source_name}.nc"
        with xr.open_dataset(source) as ds:
            xr.Dataset({VIDEO: ds[VIDEO], HEADER: ds[HEADER]}).to_netcdf(destination)
    logger.info("finish decompress")


if __name__ == "__main__":
    main()
