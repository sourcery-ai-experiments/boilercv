"""Preview the binarization stage."""

import xarray as xr

from boilercv.data import VIDEO
from boilercv.gui import view_images
from boilercv.models.params import PARAMS
from boilercv.previews import draw_text_da


def main():
    with xr.open_dataset(PARAMS.paths.gray_preview) as ds:
        da = draw_text_da(ds[VIDEO])
        view_images(da, play_rate=6)


if __name__ == "__main__":
    main()
