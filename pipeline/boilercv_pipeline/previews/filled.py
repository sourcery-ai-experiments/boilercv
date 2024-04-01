"""Preview the filled contours stage."""

from xarray import open_dataset

from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv.types import DA
from boilercv_pipeline import FRAMERATE_PREV, PREVIEW
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.models.params import PARAMS
from boilercv_pipeline.previews import draw_text_da


def main(preview: bool = PREVIEW) -> DA:
    with open_dataset(PARAMS.paths.filled_preview) as ds:
        da = draw_text_da(scale_bool(ds[VIDEO]))
    if preview:
        view_images(da, framerate=FRAMERATE_PREV)
    return da


if __name__ == "__main__":
    main()
