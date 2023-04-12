"""Dataframes."""

import numpy as np
import pandas as pd

from boilercv.data import YX_PX
from boilercv.types import DF, ArrLike


def df_points(points: ArrLike, dims=YX_PX) -> DF:
    """Build a dataframe from an array of points."""
    return (
        pd.DataFrame(
            columns=dims,
            data=points,  # type: ignore
        )
        .rename_axis(axis="index", mapper="point")
        .rename_axis(axis="columns", mapper="dim")
    )


def frame_lines(lines: ArrLike) -> DF:
    """Build a dataframe from an array of line segments."""
    ordered_pairs = [df_points(point) for point in np.split(lines, 2, axis=1)]
    return (
        pd.concat(axis="columns", keys=[0, 1], objs=ordered_pairs)
        .rename_axis(axis="index", mapper="line")
        .rename_axis(axis="columns", mapper=["coord", "dim"])
        .reorder_levels(axis="columns", order=["dim", "coord"])
    )
