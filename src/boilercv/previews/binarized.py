"""Preview the binarization stage."""

from xarray import open_dataset

from boilercv import FRAMERATE_PREV, PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv.models.params import PARAMS
from boilercv.previews import draw_text_da
from boilercv.types import DA


def main(preview: bool = PREVIEW) -> DA:
    with open_dataset(PARAMS.paths.binarized_preview) as ds:
        da = draw_text_da(scale_bool(ds[VIDEO]))
    if preview:
        view_images(da, framerate=FRAMERATE_PREV)
    return da


if __name__ == "__main__":
    main()
