"""Store binarized images in a NetCDF file."""

from boilercv.data import VIDEO, apply_to_img_da
from boilercv.examples.large import example_dataset
from boilercv.images.cv import binarize


def main():
    with example_dataset(destination="binarized") as ds:
        ds[VIDEO] = apply_to_img_da(binarize, ds[VIDEO], vectorize=True)


if __name__ == "__main__":
    main()
