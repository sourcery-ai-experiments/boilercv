"""Overlay detected bubbles on the image."""

from boilercv import FRAMERATE_PREV, PREVIEW, WRITE
from boilercv.captivate.captures import write_video
from boilercv.captivate.previews import view_images
from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv.models.params import LOCAL_PATHS, PARAMS
from boilercv.previews import compose_da, draw_text_da, get_preview
from boilercv.types import DA


def main(preview: bool = PREVIEW) -> DA:
    gray = get_preview(PARAMS.paths.gray_preview)
    filled = get_preview(PARAMS.paths.filled_preview)
    composed = draw_text_da(
        compose_da(gray[VIDEO], scale_bool(filled[VIDEO])).transpose(
            "video_name", "ypx", "xpx", "channel"
        )
    )
    if preview:
        view_images(composed, framerate=FRAMERATE_PREV)
    if WRITE:
        write_video(
            LOCAL_PATHS.media / "examples/composite", composed, framerate=FRAMERATE_PREV
        )
    return composed


if __name__ == "__main__":
    main()
