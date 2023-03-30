"""Convert all CINEs to NetCDF."""

from boilercv import LARGE_SOURCES
from boilercv.data.dataset import prepare_dataset


def main():
    sources = sorted(LARGE_SOURCES.glob("*.cine"))
    for source in sources:
        destination = LARGE_SOURCES / f"{source.stem}.nc"
        if destination.exists():
            continue
        prepare_dataset(source).to_netcdf(path=destination)


if __name__ == "__main__":
    main()
