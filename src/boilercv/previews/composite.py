"""Overlay detected bubbles on the image."""

from skvideo.io import vwrite

from boilercv import PREVIEW, WRITE
from boilercv.data import VIDEO
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.models.params import LOCAL_PATHS, PARAMS
from boilercv.previews import FRAMERATE, compose_da, draw_text_da, get_preview


def main():
    gray = get_preview(PARAMS.paths.gray_preview)
    filled = get_preview(PARAMS.paths.filled_preview)
    composed_da = draw_text_da(
        compose_da(gray[VIDEO], scale_bool(filled[VIDEO])).transpose(
            "video_name", "ypx", "xpx", "channel"
        )
    )
    if PREVIEW:
        view_images(composed_da, play_rate=FRAMERATE)
    if WRITE:
        vwrite(
            LOCAL_PATHS.media / "composite.mp4",
            composed_da,
            inputdict={"-r": str(FRAMERATE)},
        )


if __name__ == "__main__":
    main()
