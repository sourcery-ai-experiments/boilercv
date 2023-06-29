from os import chdir
from pathlib import Path

import seaborn as sns
from IPython.display import display
from matplotlib import pyplot as plt

from boilercv.captivate.previews import image_viewer
from boilercv.format import set_format
from boilercv.models.params import PARAMS


def init():
    """Initialization steps common to all examples."""
    set_format()
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette="bright",
        font="sans-serif",
    )
    plt.style.use(style=PARAMS.project_paths.mpl_base)


init()

_ = display()


def patch():
    """Patch the project if we're running notebooks in the documentation directory."""
    if Path().resolve().name == "examples":
        chdir("../..")


def keep_viewer_in_scope():
    """Keep the viewer in scope so that it doesn't get garbage collected."""
    with image_viewer([]) as viewer:
        return viewer
