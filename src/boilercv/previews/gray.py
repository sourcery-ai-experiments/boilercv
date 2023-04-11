"""Preview the grayscale stage."""

import xarray as xr

from boilercv import FRAMERATE_PREV, PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.data import VIDEO
from boilercv.models.params import PARAMS
from boilercv.previews import draw_text_da
from boilercv.types import DA


def main(preview: bool = PREVIEW) -> DA:
    with xr.open_dataset(PARAMS.paths.gray_preview) as ds:
        da = draw_text_da(ds[VIDEO])
    if preview:
        view_images(da, framerate=FRAMERATE_PREV)
    return da


if __name__ == "__main__":
    main()
