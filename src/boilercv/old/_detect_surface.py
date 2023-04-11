"""Old approach to detecting the boiling surface."""

import numpy as np
import pandas as pd

from boilercv import DEBUG
from boilercv.captivate.previews import view_images
from boilercv.data import YX_PX, apply_to_img_da
from boilercv.data.frames import df_points, frame_lines
from boilercv.examples.detect_surface import find_boiling_surface
from boilercv.images.cv import find_contours, find_line_segments
from boilercv.types import DA, ArrInt


def _find_boiling_surface(image: DA, preview: bool = DEBUG) -> ArrInt:
    """Find the boiling surface."""
    # Find corners and set index to contour points for later concatenation
    (height, width) = image.shape
    corns_ = apply_to_img_da(find_boiling_surface, image)
    corns = df_points(np.nonzero(corns_.values))
    corns = (
        corns.set_index(pd.MultiIndex.from_frame(corns))
        .drop(axis="columns", labels=YX_PX)
        .assign(**dict(corner=True))
    )
    # Find the contour angles
    contours = find_contours(image.values)
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
    if preview:
        view_images(dict(corn=corns_.values))
    # TODO: Save to disk, draw on an image for previewing
    return candidates.values.flatten()[:2]


def _find_boiling_surface2(image):
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
