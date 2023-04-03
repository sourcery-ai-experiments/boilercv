"""Preview the binarization stage."""

import xarray as xr

from boilercv.gui import view_images
from boilercv.models.params import PARAMS


def main():
    with xr.open_dataset(PARAMS.paths.binarized_preview) as ds:
        view_images(ds)


if __name__ == "__main__":
    main()
