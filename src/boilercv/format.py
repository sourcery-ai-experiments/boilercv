# type: ignore pyright 1.1.308, local/CI differences, below
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any, Literal

import matplotlib as mpl
import numpy as np
import pandas as pd
from IPython.core.display import Markdown, Math  # type: ignore
from IPython.display import display  # type: ignore
from matplotlib import pyplot as plt
from matplotlib.axis import XAxis, YAxis
from matplotlib.ticker import MaxNLocator
from sympy import FiniteSet
from sympy.printing.latex import latex

# * -------------------------------------------------------------------------------- * #
# * DISPLAY


def disp_named(*args: tuple[Any, str]):
    """Display objects with names above them."""
    for elem, name in args:
        display(Markdown(f"##### {name}"))
        display(elem)


def disp_free(title, eqn, **kwargs):
    disp(title, eqn, **kwargs)
    disp("Free symbols", FiniteSet(*eqn.rhs.free_symbols), **kwargs)


def disp(title, *exprs, **kwargs):
    print(f"{title}:")
    display(*(math_mod(expr, **kwargs) for expr in exprs))


def math_mod(expr, long_frac_ratio=3, **kwargs):
    return Math(latex(expr, long_frac_ratio=long_frac_ratio, **kwargs))


# * -------------------------------------------------------------------------------- * #
# * PLOTTING


def smart_set_lim(
    ax: plt.Axes,
    axis: Literal["x", "y", "z"],
    limit: tuple[float, float],
    prec: int = 0,
):
    """Set axis limits with smart precision and tick handling.

    If axis limits exceed one, simply set the limits. Otherwise, set limits and
    automatically choose the minimum necessary label format precision to represent the
    limits. Limit the number of major ticks so as not to repeat tick labels given the
    format precision.

    Args:
        ax: The axes object to operate on.
        axis: The axis (e.g. "x" or "y") to operate on.
        limit: The axes limits to apply.
        prec: The maximum precision for the major ticks. Default is 0.
    """
    getattr(ax, f"set_{axis}lim")(*limit)
    if np.max(limit) > 1:
        return
    if prec == 0:
        prec = int(np.min(np.floor(np.log10(np.array(limit)[np.array(limit) != 0]))))
    axis_to_set: XAxis | YAxis = getattr(ax, f"{axis}axis")
    axis_to_set.set_major_formatter(f"{{:#.{-prec}f}}".format)
    axis_to_set.set_major_locator(
        MaxNLocator(int(np.squeeze(np.diff(limit)) * 10**-prec))
    )


@contextmanager
def manual_subplot_spacing():
    """Context manager that allows custom spacing of subplots."""
    with mpl.rc_context({"figure.autolayout": False}):
        try:
            yield
        finally:
            ...


def tex_wrap(df: pd.DataFrame) -> tuple[pd.DataFrame, Mapping[str, str]]:
    """Wrap column titles in LaTeX flags if they contain underscores ($)."""
    mapper: dict[str, str] = {}
    for src_col in df.columns:
        col = f"${handle_subscript(src_col)}$" if "_" in src_col else src_col
        mapper[src_col] = col
    return df.rename(axis="columns", mapper=mapper), mapper
