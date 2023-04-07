"""Overlay detected bubbles on the image."""

import xarray as xr

from boilercv.data import VIDEO
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.models.params import PARAMS
from boilercv.previews import draw_text_da, overlay_da


def main():
    gray_path = PARAMS.paths.gray_preview
    fill_path = PARAMS.paths.filled_preview
    with xr.open_dataset(gray_path) as gray, xr.open_dataset(fill_path) as filled:
        overlaid_da = draw_text_da(
            overlay_da(gray[VIDEO], scale_bool(filled[VIDEO])).transpose(
                "video_name", "ypx", "xpx", "channel"
            )
        )
        view_images(overlaid_da, play_rate=6)


if __name__ == "__main__":
    main()
