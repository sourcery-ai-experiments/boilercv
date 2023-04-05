"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from os import environ
from pathlib import Path
from textwrap import dedent

import pandas as pd
import pyqtgraph as pg
from cv2 import version
from loguru import logger

__version__ = "0.0.0"

_debug = environ.get("BOILERCV_DEBUG")
DEBUG = str(_debug).casefold() == "true" if _debug else False
"""Whether to run in debug mode. Log to `boilercv.log` and grab fewer frames."""

if DEBUG:
    logger.add(sink="boilercv.log")
    NUM_FRAMES = 1000
else:
    NUM_FRAMES = 0


def init():
    """Initialize `boilercv`."""
    check_contrib()
    check_samples_env_var()
    pg.setConfigOption("imageAxisOrder", "row-major")
    pd.set_option("mode.copy_on_write", True)
    pd.set_option("mode.chained_assignment", "raise")
    pd.set_option("mode.string_storage", "pyarrow")


def check_contrib():
    """Ensure the installed version of OpenCV has extras.

    Dependencies can specify a different version of OpenCV than the one required in this
    project, unintentionally clobbering the installed version of OpenCV. Detect whether
    a non-`contrib` version is installed by a dependency.
    """
    if not version.contrib:
        raise ImportError(
            dedent(
                """OpenCV is not installed with extras. A dependent package may have pinned
    `opencv-pyhon` and clobbered your installed version.
    """
            )
        )


def check_samples_env_var():
    """Check that the OpenCV samples environment variable is set and is a folder."""
    samples_env_var = "OPENCV_SAMPLES_DATA_PATH"
    if (
        not (samples_dir := environ.get(samples_env_var))
        or not Path(samples_dir).is_dir()
    ):
        raise RuntimeError(
            f"{samples_env_var} not set or specified directory does not exist."
        )


init()
