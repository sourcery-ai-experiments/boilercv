"""Get bubble contours."""

import cv2 as cv

from boilercv.data import VIDEO
from boilercv.data.frames import idx
from boilercv.data.sets import get_dataset
from boilercv.examples import EXAMPLE_VIDEO_NAME
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.images.cv import draw_contours
from boilercv.models.params import PARAMS
from boilercv.stages.contours import get_all_contours
from boilercv.types import ArrInt, Img

NUM_FRAMES = 1000


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME, NUM_FRAMES)
    video = ds[VIDEO]
    df = get_all_contours(
        cv.bitwise_not(scale_bool(video.values)), method=cv.CHAIN_APPROX_SIMPLE
    )
    df.to_hdf(
        PARAMS.paths.examples / f"{EXAMPLE_VIDEO_NAME}.h5",
        "contours",
        complib="zlib",
        complevel=9,
    )
    result: list[Img] = []
    for frame_num, frame in enumerate(video):
        contours: list[ArrInt] = list(  # type: ignore
            df.loc[idx[frame_num], :]  # type: ignore
            .groupby("contour")
            .apply(lambda grp: grp.values)  # type: ignore
        )
        result.append(draw_contours(scale_bool(frame.values), contours))
    view_images(result)


if __name__ == "__main__":
    main()
