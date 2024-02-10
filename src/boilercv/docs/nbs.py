"""Documentation utilities."""

import io
import os
import re
from collections.abc import Callable
from contextlib import contextmanager, nullcontext, redirect_stdout
from os import chdir
from pathlib import Path
from tempfile import NamedTemporaryFile
from textwrap import dedent
from typing import Any
from warnings import catch_warnings, filterwarnings

import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import HTML, display
from IPython.utils.capture import capture_output
from matplotlib import pyplot as plt
from myst_parser.parsers.docutils_ import cli_html
from nbformat import NotebookNode

from boilercv.types import DfOrS

FONT_SCALE = 1.3
"""Plot font scale."""
PRECISION = 4
"""The desired precision."""
FLOAT_SPEC = f"#.{PRECISION}g"
"""The desired float specification for formatted output."""
HIDE = display()
"""Hide unsuppressed output. Can't use semicolon due to black autoformatter."""
DISPLAY_ROWS = 20
"""The number of rows to display in a dataframe."""


def init(font_scale: float = FONT_SCALE):
    """Initialize a documentation notebook."""
    path = Path().cwd()
    root = Path(path.root).resolve()
    while not (path / "data").exists():
        path = path.parent
    if path == root:
        raise RuntimeError("Data missing.")
    chdir(path)
    # The triple curly braces in the f-string allows the format function to be
    # dynamically specified by a given float specification. The intent is clearer this
    # way, and may be extended in the future by making `float_spec` a parameter.
    pd.options.display.float_format = f"{{:{FLOAT_SPEC}}}".format
    pd.options.display.min_rows = pd.options.display.max_rows = DISPLAY_ROWS
    np.set_printoptions(precision=PRECISION)
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette="deep",
        font="sans-serif",
        font_scale=font_scale,
    )
    plt.style.use("data/plotting/base.mplstyle")


@contextmanager
def nowarn(capture: bool = False):
    """Don't raise any warnings. Optionally capture output for pesky warnings."""
    with catch_warnings(), capture_output() if capture else nullcontext():
        filterwarnings("ignore")
        yield


def keep_viewer_in_scope():
    """Keep the image viewer in scope so it doesn't get garbage collected."""

    from boilercv.captivate.previews import image_viewer  # noqa: PLC0415

    with image_viewer([]) as viewer:
        return viewer


PATCH = "from boilercv.docs.nbs import init\n\ninit()"


def foo(notebook: NotebookNode) -> NotebookNode:
    """..."""
    first_code_cell = next(cell for cell in notebook.cells if cell.cell_type == "code")
    content = first_code_cell.get("source", "")
    if content and not content.startswith(PATCH):
        first_code_cell["source"] = "\n\n".join((PATCH, content))
    return notebook


def insert_tags(notebook: NotebookNode, tags_to_insert: list[str]) -> NotebookNode:
    """Insert tags to all code cells in a notebook.

    See: https://jupyterbook.org/en/stable/content/metadata.html?highlight=python#add-tags-using-python-code
    """
    for cell in [cell for cell in notebook.cells if cell.cell_type == "code"]:  # type: ignore  # pyright 1.1.333
        tags = cell.get("metadata", {}).get("tags", [])
        cell["metadata"]["tags"] = tags_to_insert + list(
            set(tags) - set(tags_to_insert)
        )
    return notebook


def remove_tags(notebook: NotebookNode, tags_to_remove: list[str]) -> NotebookNode:
    """Remove tags to all code cells in a notebook.

    See: https://jupyterbook.org/en/stable/content/metadata.html?highlight=python#add-tags-using-python-code
    """
    for cell in [cell for cell in notebook.cells if cell.cell_type == "code"]:  # type: ignore  # pyright 1.1.333
        tags = cell.get("metadata", {}).get("tags", [])
        cell["metadata"]["tags"] = list(set(tags) - set(tags_to_remove))
    return notebook


# * -------------------------------------------------------------------------------- * #
# * Render Math in DataFrames locally and in generated docs
# * https://github.com/executablebooks/jupyter-book/issues/1501#issuecomment-1721378476


def display_dataframe_with_math(df, raw=False):
    """Display a dataframe with MathJax-rendered math."""
    html = df.to_html()
    raw_html = re.sub(r"\$.*?\$", lambda m: convert_tex_to_html(m[0], raw=True), html)  # type: ignore
    return raw_html if raw else HTML(raw_html)


def convert_tex_to_html(html, raw=False):
    """Manually apply the MyST parser to convert $-$ into MathJax's HTML code."""
    frontmatter = """
    ---
    myst:
      enable_extensions: [dollarmath, amsmath]
    ---
    """
    with NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
        f.write(dedent(frontmatter).strip())
        f.write("\n\n")
        f.write(html)
    with redirect_stdout(io.StringIO()) as sf:
        cli_html([f.name])
    fullhtml = sf.getvalue()  # Returns a large-ish HTML with the full styling header
    os.remove(f.name)  # noqa: PTH107
    # Strip HTML headers to keep only the body with converted math
    m = re.search(r'<body>\n<div class="document">([\s\S]*)</div>\n</body>', fullhtml)
    raw_html = m[1].strip()  # type: ignore
    # Special case: if we provided a snippet with no HTML markup at all, don't wrap the result
    # in <p> tags
    if (
        "\n" not in html
        and "<" not in html
        and (m := re.match(r"<p>(.*)</p>", raw_html))
    ):
        raw_html = m[1]
    # Manually display the result as HTML
    return raw_html if raw else HTML(raw_html)


# * -------------------------------------------------------------------------------- * #
# * Make styled dataframes resepct precision
# * https://gist.github.com/blakeNaccarato/3c751f0a9f0f5143f3cffc525e5dd577


@contextmanager
def style_df(df: DfOrS, head: bool = False):
    """Style a dataframe."""
    df, truncated = truncate(df, head)
    styler = df.style
    yield styler
    display(styler.format(get_df_formatter(df, truncated)))  # type: ignore  # pyright 1.1.333


def display_dfs(*dfs: DfOrS, head: bool = False):
    """Display formatted DataFrames.

    When a mapping of column names to callables is given to the Pandas styler, the
    callable will be used internally by Pandas to produce formatted strings. This
    differs from elementwise formatting, in which Pandas expects the callable to
    actually process the value and return the formatted string.
    """
    for df in dfs:
        df, truncated = truncate(df, head)
        display(df.style.format(get_df_formatter(df, truncated)))  # type: ignore  # pyright 1.1.333


def get_df_formatter(
    df: pd.DataFrame, truncated: bool
) -> Callable[..., str] | dict[str, Callable[..., str]]:
    """Get formatter for the dataframe."""
    if truncated:
        return format_cell
    cols = df.columns
    types = {col: dtype.type for col, dtype in zip(cols, df.dtypes, strict=True)}
    return {col: get_formatter(types[col]()) for col in cols}


def format_cell(cell) -> str:
    """Format individual cells."""
    return get_formatter(cell)(cell)


def get_formatter(instance: Any) -> Callable[..., str]:
    """Get the formatter depending on the type of the instance."""
    match instance:
        case float():
            return lambda cell: f"{cell:{FLOAT_SPEC}}"
        case _:
            return lambda cell: f"{cell}"


def truncate(df: DfOrS, head: bool = False) -> tuple[pd.DataFrame, bool]:
    """Truncate long dataframes, showing only the head and tail."""
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if len(df) <= pd.options.display.max_rows:
        return df, False
    if head:
        return df.head(pd.options.display.min_rows), True
    df = df.copy()
    # Resolves case when column names are not strings for latter assignment, e.g. when
    # the column axis is a RangeIndex.
    df.columns = [str(col) for col in df.columns]
    # Resolves ValueError: Length of names must match number of levels in MultiIndex.
    ellipsis_index = ("...",) * df.index.nlevels
    df = pd.concat([
        df.head(pd.options.display.min_rows // 2),
        df.iloc[[0]]  # Resolves ValueError: cannot handle a non-unique multi-index!
        .reindex(
            pd.MultiIndex.from_tuples([ellipsis_index], names=df.index.names)
            if isinstance(df.index, pd.MultiIndex)
            else pd.Index(ellipsis_index, name=df.index.name)
        )
        .assign(**dict.fromkeys(df.columns, "...")),
        df.tail(pd.options.display.min_rows // 2),
    ])
    return df, True
