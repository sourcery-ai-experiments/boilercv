"""Utilities for root and DVC-tracked documentation."""

from os import chdir
from pathlib import Path

import nbformat as nbf
import seaborn as sns
from IPython.display import display
from matplotlib import pyplot as plt

from boilercv.format import set_format

# * -------------------------------------------------------------------------------- * #
# * COMMON TO ROOT AND DVC-TRACKED DOCUMENTATION


_ = display()


def init():
    """Initialize notebook formats."""

    from boilercv.models.params import PARAMS

    set_format()
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette="bright",
        font="sans-serif",
    )
    plt.style.use(style=PARAMS.project_paths.mpl_base)


def keep_viewer_in_scope():
    """Keep the image viewer in scope so it doesn't get garbage collected."""

    from boilercv.captivate.previews import image_viewer

    with image_viewer([]) as viewer:
        return viewer


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
