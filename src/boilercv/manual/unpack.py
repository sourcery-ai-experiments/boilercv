"""Unpack sources to local storage."""


from pathlib import Path

from loguru import logger

from boilercv.data import ROI, VIDEO
from boilercv.data.packing import pack
from boilercv.data.sets import get_all_datasets
from boilercv.models.params import PARAMS
from boilercv.types import DS


def main():
    logger.info("start")
    for ds, video in get_all_datasets():
        destination = PARAMS.paths.uncompressed_sources / f"{video}.nc"
        if destination.exists():
            continue
        try:
            loop(ds, destination)
        except Exception:
            logger.exception(video)
            continue
    logger.info("finish")


def loop(ds: DS, destination: Path):
    ds = ds.drop_vars(ROI)
    ds[VIDEO] = pack(ds[VIDEO])
    ds.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
