"""Overlay detected bubbles on the binarization stage."""

from skvideo.io import vwrite

from boilercv import PREVIEW, WRITE
from boilercv.data import VIDEO
from boilercv.data.sets import get_dataset
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.models.params import LOCAL_PATHS
from boilercv.previews import compose_da

EXAMPLE = "2021-02-23T14-37-47"
FRAMERATE = 30
NUM_FRAMES = 300


def main():
    source = get_dataset(EXAMPLE, NUM_FRAMES)
    bubbles = get_dataset(EXAMPLE, NUM_FRAMES, stage="filled")
    highlighted_bubbles = compose_da(
        source[VIDEO], scale_bool(bubbles[VIDEO])
    ).transpose("frame", "ypx", "xpx", "channel")
    if PREVIEW:
        view_images(bubbles[VIDEO].isel(frame=0))
        view_images(highlighted_bubbles, play_rate=FRAMERATE)
    if WRITE:
        vwrite(
            LOCAL_PATHS.media / "binarized.mp4",
            scale_bool(source[VIDEO]),
            inputdict={"-r": str(FRAMERATE)},
        )
        vwrite(
            LOCAL_PATHS.media / "bubbles.mp4",
            scale_bool(bubbles[VIDEO]),
            inputdict={"-r": str(FRAMERATE)},
        )
        vwrite(
            LOCAL_PATHS.media / "binar_highlighted.mp4",
            highlighted_bubbles,
            inputdict={"-r": str(FRAMERATE)},
        )


if __name__ == "__main__":
    main()
