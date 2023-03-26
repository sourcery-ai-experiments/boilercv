"""Prepare the video for saving to disk.

Computing the median is a costly operation, so don't do it if we don't have to. Padding
with OpenCV is faster than numpy padding.
"""


from pathlib import Path
from warnings import warn

from boilercv import EXAMPLE_BIG_CINE, EXAMPLE_CINE, EXAMPLE_CINE_ZOOMED
from boilercv.data.arrays import build_lines_da, build_points_da
from boilercv.data.dataset import (
    VIDEO,
    assign_other_roi_ds,
    assign_roi_ds,
    prepare_dataset,
)
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
    maximum: ArrInt = video.max("frame").data
    flooded = flood(maximum)
    eroded = close_and_erode(flooded)
    contours = find_contours(~eroded)
    roi = contours.pop()
    if len(contours) > 1:
        warn("More than one contour found when searching for the ROI.")
    first_image = video.isel(frame=0).values
    binarized_first = binarize(first_image)
    contoured = draw_contours(first_image, contours)
    save_roi(roi, roi_path)

    lines_, lsd = find_line_segments(maximum)
    lined = lsd.drawSegments(maximum, lines_)
    lines = build_lines_da(line_segments=lines_)

    def get_midpoint(line):
        (y1, x1, y2, x2) = line
        return [(y1 + y2) / 2, (x1 + x2) / 2]

    midpoints = build_points_da([get_midpoint(line) for line in lines])
    masked = mask(binarized_first, [roi])

    ds = assign_roi_ds(ds, roi)
    ds = assign_other_roi_ds(ds, contours)

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


if __name__ == "__main__":
    main()
