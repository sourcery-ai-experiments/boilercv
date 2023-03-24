"""Store binarized images in a NetCDF file."""

from pathlib import Path

from boilercv import IMAGES
from boilercv.data import prepare_dataset
from boilercv.images import threshold


def main():
    desktop = Path("C:/Users/Blake/Desktop")
    sources = (desktop / "video").iterdir()
    destinations = (desktop / "binarized" / f"{source.stem}.nc" for source in sources)
    for source, destination in zip(sources, destinations, strict=True):
        dataset = prepare_dataset(source)[IMAGES]
        images = dataset[IMAGES]
        images.values = (threshold(image.values) for image in images)
        dataset.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
