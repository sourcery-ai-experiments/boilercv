"""Overlay detected bubbles on the binarized stage."""

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
    source = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="sources")[VIDEO]
    bubbles = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="filled")[VIDEO]
    highlighted_bubbles = compose_da(source, scale_bool(bubbles)).transpose(
        "frame", "ypx", "xpx", "channel"
    )
    if PREVIEW:
        view_images(bubbles.isel(frame=0))
        view_images(highlighted_bubbles, framerate=FRAMERATE_CONT)
    if WRITE:
        write_video(LOCAL_PATHS.media / "binarized", source)
        write_video(LOCAL_PATHS.media / "bubbles", bubbles, preview_frame=True)
        write_video(LOCAL_PATHS.media / "binarized_highlighted", highlighted_bubbles)


if __name__ == "__main__":
    main()
