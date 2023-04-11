"""Preview the binarization stage."""

import xarray as xr

from boilercv import FRAMERATE_PREV
from boilercv.data import VIDEO
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.models.params import PARAMS
from boilercv.previews import draw_text_da


def main():
    with xr.open_dataset(PARAMS.paths.binarized_preview) as ds:
        da = draw_text_da(scale_bool(ds[VIDEO]))
        view_images(da, framerate=FRAMERATE_PREV)


if __name__ == "__main__":
    main()
