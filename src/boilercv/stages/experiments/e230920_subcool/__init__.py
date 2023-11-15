"""Subcooled bubble collapse experiment."""

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

import numpy as np
import pandas as pd
from boilercore.paths import ISOLIKE, dt_fromisolike, get_module_name
from boilercore.testing import Params, get_nb_namespace
from cmasher import get_sub_cmap
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Colormap, Normalize
from matplotlib.pyplot import subplots
from sparklines import sparklines

from boilercv.images import scale_bool
from boilercv.images.cv import Op, Transform, transform
from boilercv.models.params import PARAMS
from boilercv.types import DA, Img

EXP = get_module_name(__spec__ or __file__)
"""Name of this experiment."""
DAY = "2023-09-20"
"""Day of the experiment"""
EXP_DATA = PARAMS.paths.experiments / EXP
"""Experimental data."""
ALL_THERMAL_DATA = EXP_DATA / f"{DAY}_all_thermal_data.csv"
"""All thermal data for this experiment."""
THERMAL_DATA = EXP_DATA / f"{DAY}_thermal.h5"
"""Reduced thermal data for this experiment."""


def get_times(strings: Iterable[str]) -> Iterable[datetime]:
    for string in strings:
        if match := ISOLIKE.search(string):
            yield dt_fromisolike(match)


EXP_TIMES = get_times(path.stem for path in (EXP_DATA).iterdir())


def export_centers(params: Params):
    """Export centers."""
    dest = EXP_DATA / "centers"
    ns = get_nb_namespace(
        nb=PARAMS.paths.stages[f"experiments_{EXP}_find_centers"].read_text(
            encoding="utf-8"
        ),
        params=params,
        results=["centers", "PATH_TIME"],
    )
    dest.mkdir(exist_ok=True)
    path = (dest / f"centers_{ns.PATH_TIME}").with_suffix(".h5")
    ns.centers.to_hdf(path, key="centers", complib="zlib", complevel=9)


def export_contours(params: Params):
    """Export contours."""
    dest = EXP_DATA / "contours"
    ns = get_nb_namespace(
        nb=PARAMS.paths.stages[f"experiments_{EXP}_find_contours"].read_text(
            encoding="utf-8"
        ),
        params=params,
        results=["contours", "PATH_TIME"],
    )
    dest.mkdir(exist_ok=True)
    path = (dest / f"contours_{ns.PATH_TIME}").with_suffix(".h5")
    ns.contours.to_hdf(path, key="contours", complib="zlib", complevel=9)


class GroupByCommon(TypedDict):
    as_index: bool
    dropna: bool
    observed: bool
    group_keys: bool
    sort: bool


GBC = GroupByCommon(
    as_index=False, dropna=False, observed=True, group_keys=False, sort=False
)


def gbc(
    as_index: bool = False,
    dropna: bool = False,
    observed: bool = True,
    group_keys: bool = False,
    sort: bool = False,
):
    return GBC | GroupByCommon(**locals())


def plot_composite_da(video: DA) -> Axes:
    """Compose a video-like data array and highlight the first frame."""
    first_frame = video.sel(frame=0).values
    composite_video = video.max("frame").values
    with bounded_ax(composite_video) as ax:
        ax.imshow(~first_frame, alpha=0.6)
        ax.imshow(~composite_video, alpha=0.2)
    return ax


@contextmanager
def bounded_ax(img: Img) -> Iterator[Axes]:
    """Show only the region bounding nonzero elements of the image."""
    ylim, xlim = get_image_boundaries(img)
    _, ax = subplots()
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.invert_yaxis()
    yield ax


def get_image_boundaries(img) -> tuple[tuple[int, int], tuple[int, int]]:
    # https://stackoverflow.com/a/44734377/20430423
    dilated = transform(scale_bool(img), Transform(Op.dilate, 12))
    cols = np.any(dilated, axis=0)
    rows = np.any(dilated, axis=1)
    ylim = tuple(np.where(rows)[0][[0, -1]])
    xlim = tuple(np.where(cols)[0][[0, -1]])
    return ylim, xlim  # type: ignore  # pyright 1.1.333


def crop_image(img, ylim, xlim):
    return img[ylim[0] : ylim[1] + 1, xlim[0] : xlim[1] + 1]


WIDTH = 10


def get_hists(df: pd.DataFrame, groupby: str, cols: list[str]) -> pd.DataFrame:
    df = df.groupby(groupby, **GBC).agg(
        **{
            # type: ignore  # pyright 1.1.333
            col: pd.NamedAgg(column=col, aggfunc=sparkhist)
            for col in cols
        }
    )
    # Can't one-shot this because of the comprehension {...: ... for col in hist_cols}
    return df.assign(**{col: df[col].str.center(WIDTH, "▁") for col in cols})


def sparkhist(grp: pd.DataFrame) -> str:
    """Render a sparkline histogram."""
    num_lines = 1  # Sparklines don't render properly across multiple lines
    bins = min(WIDTH - 2, int(np.sqrt(grp.count())))
    histogram, edges_ = np.histogram(grp, bins=bins)
    return "\n".join(sparklines(histogram, num_lines))


@dataclass
class Col:
    old: str
    new: str = ""
    old_unit: str = ""
    new_unit: str = ""
    scale: float = 1

    def __post_init__(self):
        self.new = self.new or self.old
        self.new_unit = self.new_unit or self.old_unit
        self.new = f"{self.new} ({self.new_unit})" if self.new_unit else self.new


def transform_cols(df: pd.DataFrame, cols: list[Col]) -> pd.DataFrame:
    return df.assign(
        **{
            col.new: df[col.old] if col.scale == 1 else df[col.old] * col.scale
            for col in cols
        }
    )[[col.new for col in cols]]


class Conversion(TypedDict):
    """Scalar conversion between units."""

    old_unit: str
    new_unit: str
    scale: float


M_TO_MM = Conversion(old_unit="m", new_unit="mm", scale=1000)


def get_cat_colorbar(
    ax: Axes, col: str, palette: Colormap, data: pd.DataFrame
) -> tuple[list[tuple[float, float, float]], pd.DataFrame]:
    if isinstance(data[col].dtype, pd.CategoricalDtype):
        data[col] = data[col].cat.remove_unused_categories()
        num_colors = len(data[col].cat.categories)
    else:
        num_colors = data[col].nunique()
    palette = get_first_from_palette(palette, num_colors)
    mappable = ScalarMappable(cmap=palette, norm=Normalize(0, num_colors))
    mappable.set_array([])
    colorbar = ax.figure.colorbar(  # type: ignore  # pyright 1.1.333
        ax=ax, mappable=mappable, label=col
    )
    colorbar.set_ticks([])
    return palette.colors, data  # type: ignore  # pyright 1.1.333


def get_first_from_palette(palette: Colormap, n: int) -> Colormap:
    """Get the first `n` colors from a palette."""
    return get_sub_cmap(palette, start=0, stop=n / palette.N, N=n)  # type: ignore  # pyright 1.1.333
