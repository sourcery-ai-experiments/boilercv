"""Data arrays."""

from boilercv.data import build_da
from boilercv.data.dataset import LINE_COORDS, POINT_COORDS, PRIMARY_LENGTH_UNITS
from boilercv.data.models import Dimension
from boilercv.types import DA, ArrLike


def build_lines_da(line_segments: ArrLike) -> DA:
    """Build data array of line segments."""
    return build_2d_da("line", "Line segment", line_segments, LINE_COORDS)


def build_points_da(points: ArrLike) -> DA:
    """Build data array of points."""
    return build_2d_da("point", "Point", points, POINT_COORDS)


def build_2d_da(name: str, long_name: str, data: ArrLike, coords: list[str]) -> DA:
    """Build a two-dimensional data array."""
    return build_da(
        name=name,
        long_name=long_name,
        units=PRIMARY_LENGTH_UNITS,
        dims=(
            Dimension(
                dim=f"{name}s",
                long_name=f"{long_name}s",
            ),
            Dimension(
                dim=name,
                long_name=long_name,
                coords=coords,
            ),
        ),
        data=data,
    )
