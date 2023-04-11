"""Preview detected regions on an image from the dataset."""

import xarray as xr

from boilercv import PREVIEW, WRITE
from boilercv.captivate.captures import write_image
from boilercv.captivate.previews import view_images
from boilercv.colors import BLUE, GREEN, RED
from boilercv.data import ROI, VIDEO
from boilercv.data.sets import get_dataset
from boilercv.examples.detect_surface import find_boiling_surface
from boilercv.examples.previews import _EXAMPLE
from boilercv.images import overlay, scale_bool
from boilercv.models.params import LOCAL_PATHS, PARAMS


def main():
    ds = get_dataset(_EXAMPLE)
    gray = (
        xr.open_dataset(PARAMS.paths.gray_preview)[VIDEO]
        .sel(video_name=_EXAMPLE)
        .values
    )
    roi = ds[ROI].values
    highlighted_roi = overlay(gray, scale_bool(roi), color=BLUE, alpha=0.2)

    surface, _ = find_boiling_surface(scale_bool(roi))
    highlighted_surface = overlay(
        highlighted_roi, scale_bool(surface), color=RED, alpha=1
    )

    filled = (
        xr.open_dataset(PARAMS.paths.filled_preview)[VIDEO]
        .sel(video_name=_EXAMPLE)
        .values
    )
    highlighted_bubbles = overlay(
        highlighted_surface, scale_bool(filled), color=GREEN, alpha=0.4
    )

    if PREVIEW:
        view_images(highlighted_bubbles)
    if WRITE:
        write_image(LOCAL_PATHS.media / "roi", highlighted_roi)
        write_image(LOCAL_PATHS.media / "composite", highlighted_bubbles)


if __name__ == "__main__":
    main()
