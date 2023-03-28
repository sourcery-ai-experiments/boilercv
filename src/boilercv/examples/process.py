"""Prepare the video for saving to disk.

Computing the median is a costly operation, so don't do it if we don't have to. Padding
with OpenCV is faster than numpy padding.
"""
from pathlib import Path
from warnings import warn

import cv2 as cv
import numpy as np
import pandas as pd

from boilercv import EXAMPLE_BIG_CINE, EXAMPLE_CINE, EXAMPLE_CINE_ZOOMED
from boilercv.data import PRIMARY_LENGTH_DIMS, apply_to_frames
from boilercv.data.dataset import (
    VIDEO,
    prepare_dataset,
)
from boilercv.data.frames import df_points, frame_lines
from boilercv.gui import compare_images, save_roi
from boilercv.images import (
    apply_mask,
    binarize,
    build_mask_from_polygons,
    find_contours,
    find_line_segments,
    flood,
    morph,
)
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt, Img

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

    # Get the ROI
    maximum: ArrInt = video.max("frames").values
    (height, width) = maximum.shape
    flooded_max = apply_to_frames(flood, video.max("frames"))
    flooded_closed, roi, dilated = apply_to_frames(morph, flooded_max, returns=3)  # type: ignore
    boundary_roi = roi.values ^ dilated.values

    # Mask the first image
    first_image = video.isel(frames=0).values
    first_image_roi_only = apply_mask(first_image, roi.values)

    # Find the surface
    # Find corners and set index to contour points for later concatenation
    corns_ = apply_to_frames(get_corners, flooded_closed)
    corns = df_points(np.nonzero(corns_.values))
    corns = (
        corns.set_index(pd.MultiIndex.from_frame(corns))
        .drop(axis="columns", labels=PRIMARY_LENGTH_DIMS)
        .assign(**dict(corner=True))
    )
    # Find the contour angles
    contours = find_contours(flooded_closed.values)
    roi_poly_ = contours.pop()
    roi_poly = df_points(roi_poly_)
    distances = roi_poly.diff()
    angles = (
        pd.Series(np.degrees(np.arctan2(distances.ypx, distances.xpx)))
        .rolling(window=2)
        .mean()
        .bfill()
    ).rename("deg")
    # Concatenate contour points with their angles
    roi_poly = (
        pd.concat(
            axis="columns",
            keys=["dim", "angle"],
            objs=[roi_poly, angles],
        )
        .set_index(pd.MultiIndex.from_frame(roi_poly))
        .drop(axis="columns", labels="dim")
    )
    # Set the index to the contour points and concatenate with corners
    # Compute distance from midplanes for candidate corner selection
    roi_poly = roi_poly.set_axis(axis="columns", labels=roi_poly.columns.droplevel(1))
    corns = (
        pd.concat(axis="columns", objs=[roi_poly, corns])
        .dropna()
        .drop(axis="columns", labels="corner")
        .sort_index()
        .reset_index()
        .assign(
            **dict(
                xpx_mid_abs=lambda df: (df.xpx - width / 2).abs(),
                ypx_mid=lambda df: df.ypx - height / 2,
            )
        )
        .sort_values(axis="index", by="xpx_mid_abs")
    )
    # Consider the boiling surface to be described by the two corners with a low enough
    # angle, below the horizontal midplane, and closest to the vertical midplane
    max_angle = 30
    candidates = (
        corns[
            (corns.angle > -max_angle) & (corns.angle < max_angle) & (corns.ypx_mid > 0)
        ]
        .reset_index(drop=True)
        .loc[0:1, ["ypx", "xpx"]]
    )
    # TODO: Save to disk, draw on an image for previewing
    detected_surface = candidates.values.flatten()

    # Save and reconstruct the ROI
    # TODO: Let find contours use CHAIN_APPROX_SIMPLE here, save the ROI to disk from DF
    # TODO: Combine this ROI bounded by the surface ROI extended to the left/right edge
    # contours = find_contours(roi.values)
    # roi_poly_ = contours.pop()
    # roi_poly = df_points(roi_poly_)
    if contours:
        warn("More than one contour found when searching for the ROI.")
    save_roi(roi_poly_, roi_path)
    binarized_first = binarize(first_image)
    roi2 = build_mask_from_polygons(binarized_first, [roi_poly_])
    roi_diff = roi.values ^ roi2

    compare_images(
        dict(
            # Get the ROI
            maximum=maximum,
            flooded_max=flooded_max.values,
            roi=roi,
            dilated_roi=dilated.values,
            boundary_roi=boundary_roi,
            corn=corns_.values,
            # Mask the first image
            first_image=first_image,
            first_image_roi_only=first_image_roi_only,
            # Find the surface
            # Save and reconstruct the ROI
            roi_diff=roi_diff,
        )
    )


def get_corners(img: Img) -> Img:
    corners = cv.cornerHarris(img, 2, 3, 0.04)
    return (corners > 0.03 * corners.max()).astype(img.dtype) * np.iinfo(img.dtype).max


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
