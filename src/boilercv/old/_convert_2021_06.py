"""Handle weird CINEs from 2021-06 to the end of the year.

There is some state being shared between iterations, with the prior frame count
poisoning the next iteration. There's probably a caching issue in the CINE reading
library. Restarting this script after one successful conversion yields another
successful conversion each time.
"""

from loguru import logger

from boilercv.data.video import prepare_dataset
from boilercv.models.params import LOCAL_PATHS
from boilercv.models.paths import get_sorted_paths

FRAMES = {
    "2021-06-21T17-06-43": 3089,
    "2021-08-31T13-59-08": 4411,
    "2021-08-31T14-25-12": 1338,
    "2021-08-31T14-56-17": 3330,
    "2021-08-31T15-13-27": 4176,
    "2021-10-12T12-52-44": 1820,
    "2021-10-12T13-57-43": 4337,
    "2021-10-12T14-37-32": 2368,
    "2021-10-12T17-03-27": 2892,
    "2021-10-13T13-10-59": 3650,
    "2021-12-09T13-04-57": 3455,
}


def main():
    sources = get_sorted_paths(LOCAL_PATHS.data / "weird")
    for source in sources:
        num_frames = FRAMES[source.stem] - 1
        destination = LOCAL_PATHS.large_sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        try:
            prepare_dataset(source, num_frames).to_netcdf(path=destination)
        except Exception:
            logger.exception(source.stem)
            continue


if __name__ == "__main__":
    main()
