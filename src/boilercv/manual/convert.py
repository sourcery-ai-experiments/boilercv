"""Convert all CINEs to NetCDF."""

from loguru import logger

from boilercv.data.video import prepare_dataset
from boilercv.models.params import PARAMS
from boilercv.models.paths import iter_sorted


def main():
    sources = iter_sorted(PARAMS.paths.cines)
    for source in sources:
        destination = PARAMS.paths.large_sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        try:
            prepare_dataset(source).to_netcdf(path=destination)
        except Exception:
            logger.exception(source.stem)
            continue


if __name__ == "__main__":
    main()
