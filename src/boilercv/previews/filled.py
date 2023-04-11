"""Preview the filled contours stage."""

import xarray as xr

from boilercv import FRAMERATE_PREV
from boilercv.captivate.previews import view_images
from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv.models.params import PARAMS
from boilercv.previews import draw_text_da


def main():
    with xr.open_dataset(PARAMS.paths.filled_preview) as ds:
        da = draw_text_da(scale_bool(ds[VIDEO]))
        view_images(da, framerate=FRAMERATE_PREV)


if __name__ == "__main__":
    main()
