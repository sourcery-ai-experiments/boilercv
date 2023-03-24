"""Populate video sources."""

import xarray as xr

from boilercv import FRAMES_PER_SOURCE
from boilercv.data import prepare_dataset
from boilercv.models.params import PARAMS

# from py7zr import SevenZipFile


def main():
    for cine in sorted(PARAMS.paths.cine_sources.glob("*.cine")):
        images = prepare_dataset(cine, FRAMES_PER_SOURCE)
        dataset = xr.Dataset({images.name: images})
        dataset.to_netcdf(PARAMS.paths.sources / f"{cine.stem}.nc")
    # archive_directory(PARAMS.paths.sources)


# def archive_directory(path: Path, name: str = "sources.7z"):
#     with SevenZipFile(path / name, "w") as archive:
#         for nc in path.glob("*.nc"):
#             archive.write(nc, path)


if __name__ == "__main__":
    main()
