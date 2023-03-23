"""Store binarized images in a NetCDF file."""

from dataclasses import asdict
from pathlib import Path

import xarray as xr

from boilercv.data import prepare_images
from boilercv.images import threshold


def main():
    desktop = Path("C:/Users/Blake/Desktop")
    sources = (desktop / "video").iterdir()
    destinations = (desktop / "binarized" / f"{source.stem}.nc" for source in sources)
    for source, destination in zip(sources, destinations, strict=True):
        images, cine_header = prepare_images(source)
        binarized = [threshold(image.values) for image in images]
        images.values = binarized
        dataset = xr.Dataset({images.name: images}, attrs=asdict(cine_header))
        dataset.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
