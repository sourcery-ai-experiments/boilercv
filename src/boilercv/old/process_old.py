"""Bits and pieces I'm not using anymore."""

import numpy as np
import pandas as pd

from boilercv.data import YX_PX, apply_to_img_da
from boilercv.data.frames import df_points
from boilercv.examples.stage2 import find_boiling_surface
from boilercv.gui import view_images
from boilercv.images.cv import find_contours
from boilercv.types import DA, ArrInt


def find_boiling_surface2(image: DA, preview: bool = False) -> ArrInt:
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
