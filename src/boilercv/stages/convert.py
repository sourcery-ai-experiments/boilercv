"""Convert all CINEs to NetCDF."""

from boilercv.data.video import prepare_dataset
from boilercv.models.params import PARAMS


def main():
    sources = sorted(PARAMS.paths.large_sources.glob("*.cine"))
    for source in sources:
        destination = PARAMS.paths.large_sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        prepare_dataset(source).to_netcdf(path=destination)


if __name__ == "__main__":
    main()
