"""Utilities for root and DVC-tracked documentation."""

from collections.abc import Callable
from contextlib import contextmanager
from os import chdir
from pathlib import Path
from typing import Any
from warnings import catch_warnings, filterwarnings

import nbformat as nbf
import pandas as pd
import seaborn as sns
from IPython.display import display
from matplotlib import pyplot as plt

from boilercv.types import DfOrS

# * -------------------------------------------------------------------------------- * #
# * COMMON TO ROOT AND DVC-TRACKED DOCUMENTATION

FLOAT_SPEC = "#.4g"
"""The desired float specification for formatted output."""

HIDE = display()
"""Hide unsuppressed output. Can't use semicolon due to black autoformatter."""


def init():
    """Initialize notebook formats."""

    from boilercv.models.params import PARAMS

    # The triple curly braces in the f-string allows the format function to be
    # dynamically specified by a given float specification. The intent is clearer this
    # way, and may be extended in the future by making `float_spec` a parameter.
    pd.options.display.float_format = f"{{:{FLOAT_SPEC}}}".format

    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette="bright",
        font="sans-serif",
    )
    sns.color_palette("deep")
    plt.style.use(style=PARAMS.project_paths.mpl_base)


@contextmanager
def nowarn():
    """Don't warn at all."""
    with catch_warnings():
        filterwarnings("ignore")
        yield


def keep_viewer_in_scope():
    """Keep the image viewer in scope so it doesn't get garbage collected."""

    from boilercv.captivate.previews import image_viewer

    with image_viewer([]) as viewer:
        return viewer


# * -------------------------------------------------------------------------------- * #
# * MAKE STYLED DATAFRAMES RESPECT PRECISION
# *
# * See: https://gist.github.com/blakeNaccarato/3c751f0a9f0f5143f3cffc525e5dd577


@contextmanager
def style_df(df: DfOrS):
    """Apply default styles to styled dataframes."""
    if isinstance(df, pd.Series):
        df = df.to_frame()
    styler = df.style
    formatter = get_df_formatter(df)
    yield styler
    display(styler.format(formatter))  # type: ignore  # pyright 1.1.311


def display_dfs(*dfs: DfOrS):
    """Display formatted DataFrames.

    When a mapping of column names to callables is given to the Pandas styler, the
    callable will be used internally by Pandas to produce formatted strings. This
    differs from elementwise formatting, in which Pandas expects the callable to
    actually process the value and return the formatted string.
    """
    for df in dfs:
        if isinstance(df, pd.Series):
            df = df.to_frame()
        formatter = get_df_formatter(df)
        display(df.style.format(formatter))  # type: ignore  # pyright 1.1.311


def get_df_formatter(df: pd.DataFrame) -> dict[str, Callable[..., str]]:
    """Get formatter for the dataframe."""
    cols = df.columns
    types = {col: dtype.type for col, dtype in zip(cols, df.dtypes, strict=True)}
    return {col: get_formatter(types[col]()) for col in cols}


def get_formatter(instance: Any) -> Callable[..., str]:
    """Get the formatter depending on the type of the instance."""
    match instance:
        case float():
            return lambda cell: f"{cell:{FLOAT_SPEC}}"
        case _:
            return lambda cell: f"{cell}"


# * -------------------------------------------------------------------------------- * #
# * ROOT DOCUMENTATION


def main():
    """Insert `hide-input` tag to all notebooks in `docs/examples`."""
    for notebook in Path("docs/examples").glob("*.ipynb"):
        insert_tags(notebook, ["hide-input"])


def patch():
    """Set the appropriate working directory if in documentation."""
    path = Path().cwd()
    while not (path / "conf.py").exists():
        path = path.parent
    chdir(path.parent)


def insert_tags(notebook: Path, tags_to_insert: list[str]):
    """Insert tags to all cells in a notebook.

    See: https://jupyterbook.org/en/stable/content/metadata.html?highlight=python#add-tags-using-python-code
    """
    contents = nbf.read(notebook, nbf.NO_CONVERT)
    for cell in contents.cells:  # type: ignore
        tags = cell.get("metadata", {}).get("tags", [])
        cell["metadata"]["tags"] = tags_to_insert + list(
            set(tags) - set(tags_to_insert)
        )
    nbf.write(contents, notebook)


if __name__ == "__main__":
    main()
