"""Get bubble contours."""

import cv2 as cv
import numpy as np
import pandas as pd

from boilercv.data import VIDEO
from boilercv.data.frames import df_points, frame_lines
from boilercv.data.sets import get_dataset
from boilercv.examples import EXAMPLE_VIDEO_NAME
from boilercv.images.cv import find_contours, find_line_segments
from boilercv.types import DF, Vid

NUM_FRAMES = 1000


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME, NUM_FRAMES)
    video = ds[VIDEO]
    roi = ds["roi"]
    df = get_all_contours(video.values, method=cv.CHAIN_APPROX_SIMPLE)


def get_all_contours(video: Vid, method: int = cv.CHAIN_APPROX_NONE) -> DF:
    """Get all contours."""
    all_contours: list[DF] = []
    contours_index = ["contour", "point"]
    index = ["frame", *contours_index]
    for image in ~video:
        contours = pd.concat(
            axis="index",
            names=["contour", "point"],
            objs={
                contour_num: df_points(
                    contour
                )  # TODO: See if this can be done outside. 60% of the time is spent here.
                # TODO: Compare binarized to non-binarized contour results. Binarized
                # TODO: might be producing a lot more?
                for contour_num, contour in enumerate(find_contours(image, method))
            },
        )
        all_contours.append(contours)
    return pd.concat(
        axis="index",
        names=["frame", "contour", "point"],
        objs=dict(enumerate(all_contours)),
    )


# TODO: Is this faster?


def get_all_contours2(video: Vid, method: int = cv.CHAIN_APPROX_NONE):
    """Get all contours."""
    all_contours: list[DF] = []
    contours_index = ["contour", "point"]
    index = ["frame", *contours_index]
    for image in ~video:
        contours = pd.concat(
            axis="index",
            names=["contour", "point"],
            objs={
                contour_num: pd.DataFrame(contour)
                for contour_num, contour in enumerate(find_contours(image, method))
            },
        )
        all_contours.append(contours)
    return pd.concat(
        axis="index",
        names=["frame", "contour", "point"],
        objs=dict(enumerate(all_contours)),
    )


def later(all_contours):
    with pd.HDFStore("store.h5", "w") as store:
        for frame, contours in enumerate(all_contours):
            for j, contour in enumerate(contours):
                contour.to_hdf(store, f"c_{frame}_{j}")

    all_contours2 = []
    with pd.HDFStore("store.h5", "r") as store:
        all_contours2.extend(
            [pd.read_hdf(store, f"c_{frame}_{j}") for j, _ in enumerate(contours)]
            for frame, contours in enumerate(all_contours)
        )

    for contours, contours2 in zip(all_contours, all_contours2, strict=True):
        for contour, contour2 in zip(contours, contours2, strict=True):
            assert contour.equals(contour2)


def get_lines2(image):
    """Get line segments in an image."""
    lines_, lsd = find_line_segments(image)
    lined = lsd.drawSegments(image, lines_)
    lines = frame_lines(lines_)
    midpoints = df_points([lines.ypx.T.mean(), lines.xpx.T.mean()])
    distances = df_points([lines.ypx[1] - lines.ypx[0], lines.xpx[1] - lines.xpx[0]])
    lengths = distances.T.pow(2).sum().pow(1 / 2).rename("px")
    angles = pd.Series(np.arctan2(distances.ypx, distances.xpx)).rename("deg")
    lines = (
        pd.concat(
            axis="columns",
            keys=["line", "midpoint", "length", "angle"],
            objs=[
                lines.set_axis(axis="columns", labels=["ypx0", "xpx0", "ypx1", "xpx1"]),
                midpoints,
                lengths,
                angles,
            ],
        )
        .rename_axis(axis="index", mapper="line")
        .rename_axis(axis="columns", mapper=["metric", "dim"])
    )
    return lined, lines


if __name__ == "__main__":
    main()
