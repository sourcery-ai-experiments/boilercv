"""Decompress sources to local storage."""


from loguru import logger

from boilercv.data.sets import get_dataset, get_unprocessed_destinations
from boilercv.models.params import PARAMS


def main():
    logger.info("start decompress")
    destinations = get_unprocessed_destinations(PARAMS.local_paths.uncompressed_sources)
    for source_name, _destination in destinations.items():
        # Touch the dataset to trigger decompression implicitly
        get_dataset(name=source_name, stage="sources")
    logger.info("finish decompress")


if __name__ == "__main__":
    main()
