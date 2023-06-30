"""Documentation setup."""

from os import chdir
from pathlib import Path

import nbformat as nbf
import seaborn as sns
from IPython.display import display
from matplotlib import pyplot as plt

from boilercv.captivate.previews import image_viewer
from boilercv.format import set_format
from boilercv.models.params import PARAMS


def main():
    """Insert `hide-input` tag to all notebooks in `docs/examples`."""
    for notebook in Path("docs/examples").glob("*.ipynb"):
        insert_tags(notebook, ["hide-input"])


_ = display()


def keep_viewer_in_scope():
    """Keep the viewer in scope so that it doesn't get garbage collected."""
    with image_viewer([]) as viewer:
        return viewer


def init():
    """Initialization steps common to all examples."""
    patch()
    set_format()
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette="bright",
        font="sans-serif",
    )
    plt.style.use(style=PARAMS.project_paths.mpl_base)


def patch():
    """Patch the project if we're running notebooks in the documentation directory."""
    if Path().resolve().name == "examples":
        chdir("../..")


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
