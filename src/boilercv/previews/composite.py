"""Overlay detected bubbles on the image."""

from boilercv import FRAMERATE_PREV, PREVIEW, WRITE
from boilercv.data import VIDEO
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.models.params import LOCAL_PATHS, PARAMS
from boilercv.previews import compose_da, draw_text_da, get_preview
from boilercv.write import write_video


def main():
    gray = get_preview(PARAMS.paths.gray_preview)
    filled = get_preview(PARAMS.paths.filled_preview)
    composed = draw_text_da(
        compose_da(gray[VIDEO], scale_bool(filled[VIDEO])).transpose(
            "video_name", "ypx", "xpx", "channel"
        )
    )
    if PREVIEW:
        view_images(composed, framerate=FRAMERATE_PREV)
    if WRITE:
        write_video(LOCAL_PATHS.media / "composite", composed, framerate=FRAMERATE_PREV)


if __name__ == "__main__":
    main()
