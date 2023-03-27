"""Prepare the video for saving to disk.

Computing the median is a costly operation, so don't do it if we don't have to. Padding
with OpenCV is faster than numpy padding.
"""

from pathlib import Path
from warnings import warn

import numpy as np
import pandas as pd

from boilercv import EXAMPLE_BIG_CINE, EXAMPLE_CINE, EXAMPLE_CINE_ZOOMED
from boilercv.data.dataset import (
    VIDEO,
    prepare_dataset,
)
from boilercv.data.frames import df_points, frame_lines
from boilercv.gui import compare_images, save_roi
from boilercv.images import (
    binarize,
    close_and_erode,
    draw_contours,
    find_contours,
    find_line_segments,
    flood,
    mask,
)
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt

NUM_FRAMES = 200
DRAWN_CONTOUR_THICKNESS = 2


def main():
    mask_roi(
        EXAMPLE_BIG_CINE,
        EXAMPLE_BIG_CINE.parent / f"{EXAMPLE_BIG_CINE.stem}.yaml",
    )
    mask_roi(
        PARAMS.paths.examples / EXAMPLE_CINE,
        PARAMS.paths.examples / f"{EXAMPLE_CINE.stem}.yaml",
    )
    mask_roi(
        PARAMS.paths.examples / EXAMPLE_CINE_ZOOMED,
        PARAMS.paths.examples / f"{EXAMPLE_CINE_ZOOMED.stem}.yaml",
    )


def mask_roi(source: Path, roi_path: Path):
    ds = prepare_dataset(source, NUM_FRAMES)
    video = ds[VIDEO]
    maximum: ArrInt = video.max("frames").data
    flooded = flood(maximum)
    eroded = close_and_erode(flooded)
    contours = find_contours(~eroded)
    roi = contours.pop()
    if len(contours) > 1:
        warn("More than one contour found when searching for the ROI.")
    first_image = video.isel(frames=0).values
    binarized_first = binarize(first_image)
    contoured = draw_contours(first_image, contours)
    save_roi(roi, roi_path)
    lined, line = detect_lines(maximum)
    max_length = 40
    filtered = line.loc[(line.length > max_length).squeeze()]
    masked = mask(binarized_first, [roi])
    compare_images(
        dict(
            first_image=first_image,
            maximum=maximum,
            flood_vs_erode=flooded ^ eroded,
            contoured=contoured,
            masked=masked,
            lined=lined,
        )
    )


def detect_lines(image):
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
