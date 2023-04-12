"""Overlay detected bubbles on the gray stage."""

from boilercv import FRAMERATE_CONT, PREVIEW, WRITE
from boilercv.captivate.captures import write_video
from boilercv.captivate.previews import view_images
from boilercv.data import VIDEO
from boilercv.data.sets import get_dataset
from boilercv.examples.previews import _EXAMPLE, _NUM_FRAMES
from boilercv.images import scale_bool
from boilercv.models.params import LOCAL_PATHS
from boilercv.previews import compose_da


def main():
    gray_source = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="large_sources")[VIDEO]
    bubbles = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="filled")[VIDEO]
    highlighted_bubbles = compose_da(gray_source, scale_bool(bubbles)).transpose(
        "frame", "ypx", "xpx", "channel"
    )
    if PREVIEW:
        view_images(highlighted_bubbles, framerate=FRAMERATE_CONT)
    if WRITE:
        path = LOCAL_PATHS.media / "examples" / _EXAMPLE / "gray_highlighted"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_video(path, highlighted_bubbles, preview_frame=True)


if __name__ == "__main__":
    main()
