"""Populate video sources."""

from boilercv import FRAMES_PER_SOURCE
from boilercv.models.params import PARAMS
from boilercv.video.cine import convert_cine_to_netcdf


def main():
    variable_name = "images"
    cine_sources = {
        source
        for source in PARAMS.paths.cine_sources.iterdir()
        if source.suffix == ".cine"
    }
    for cine_source in cine_sources:
        destination = PARAMS.paths.sources / f"{cine_source.stem}.nc"
        convert_cine_to_netcdf(
            variable_name, cine_source, destination, FRAMES_PER_SOURCE
        )


if __name__ == "__main__":
    main()
