# type: ignore pyright 1.1.308, local/CI differences, below
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any

import matplotlib as mpl
import pandas as pd
from IPython.core.display import Markdown, Math  # type: ignore
from IPython.display import display  # type: ignore
from sympy import FiniteSet
from sympy.printing.latex import latex

# * -------------------------------------------------------------------------------- * #
# * DISPLAY


def set_format():
    """Set up formatting for interactive notebook sessions.
    The triple curly braces in the f-string allows the format function to be dynamically
    specified by a given float specification. The intent is clearer this way, and may be
    extended in the future by making `float_spec` a parameter.
    """
    float_spec = ":#.4g"
    pd.options.display.min_rows = pd.options.display.max_rows = 50
    pd.options.display.float_format = f"{{{float_spec}}}".format


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
