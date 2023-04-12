"""Get bubble contours."""

import cv2 as cv

from boilercv.captivate.previews import view_images
from boilercv.data import IDX, VIDEO
from boilercv.data.sets import get_dataset
from boilercv.examples import EXAMPLE_CONTOURS, EXAMPLE_NUM_FRAMES, EXAMPLE_VIDEO_NAME
from boilercv.images import scale_bool
from boilercv.images.cv import draw_contours
from boilercv.stages.contours import get_all_contours
from boilercv.types import ArrInt, Img


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME, EXAMPLE_NUM_FRAMES)
    video = ds[VIDEO]
    df = get_all_contours(
        cv.bitwise_not(scale_bool(video.values)), method=cv.CHAIN_APPROX_SIMPLE
    )
    df.to_hdf(EXAMPLE_CONTOURS, "contours", complib="zlib", complevel=9)
    result: list[Img] = []
    for frame_num, frame in enumerate(video):
        contours: list[ArrInt] = list(  # type: ignore
            df.loc[IDX[frame_num], :]  # type: ignore
            .groupby("contour")
            .apply(lambda grp: grp.values)  # type: ignore
        )
        result.append(draw_contours(scale_bool(frame.values), contours))
    view_images(result)


if __name__ == "__main__":
    main()
