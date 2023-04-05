"""Decompress sources to local storage."""


from loguru import logger

from boilercv.data import ROI, VIDEO
from boilercv.data.packing import pack
from boilercv.data.sets import ALL_NAMES, get_dataset
from boilercv.models.params import PARAMS


def main():
    logger.info("start")
    destinations = [
        PARAMS.paths.contours / f"{video_name}.h5" for video_name in ALL_NAMES
    ]
    for source_name, destination in zip(ALL_NAMES, destinations, strict=True):
        if destination.exists():
            continue
        ds = get_dataset(source_name)
        ds = ds.drop_vars(ROI)
        ds[VIDEO] = pack(ds[VIDEO])
        ds.to_netcdf(path=destination)
    logger.info("finish")


if __name__ == "__main__":
    main()
