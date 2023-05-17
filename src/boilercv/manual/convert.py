"""Convert all CINEs to NetCDF."""

from loguru import logger

from boilercv.data.video import prepare_dataset
from boilercv.models.params import PARAMS
from boilercv.models.paths import get_sorted_paths


def main():
    logger.info("start convert")
    for source in get_sorted_paths(PARAMS.local_paths.cines):
        destination = PARAMS.local_paths.large_sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        prepare_dataset(source).to_netcdf(path=destination)
    logger.info("finish convert")


if __name__ == "__main__":
    main()
