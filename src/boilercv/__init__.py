"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from os import environ
from pathlib import Path
from textwrap import dedent

import pyqtgraph as pg
from cv2 import version
from pytz import timezone

__version__ = "0.0.0"

# Dataset constants

# TODO: Migrate long names and units to data module

PRIMARY_LENGTH_UNITS = "px"

VIDEO = "video"
VIDEO_LONG_NAME = "High-speed video data"
VIDEO_UNITS = "Pixel intensity"

HEADER = "header"

ROI = "roi"
ROI_LONG_NAME = "Region of interest"
ROI_UNITS = PRIMARY_LENGTH_UNITS

OTHER_ROI = "roi_other"
OTHER_ROI_LONG_NAME = "Excess detected regions of interest"
OTHER_ROI_UNITS = PRIMARY_LENGTH_UNITS

FRAMES_PER_SOURCE = 300
LENGTH_UNITS = "um"
SAMPLE_DIAMETER_UM = 9_525_000
TIMEZONE = timezone("US/Pacific")

# Paths
PACKAGE_DIR = Path("src") / "boilercv"
DATA_DIR = Path("data")
CINE_SOURCES = Path("W:/selections")
EXAMPLE_CINE = Path("2022-11-30T13-41-00_short.cine")
EXAMPLE_CINE_ZOOMED = Path("2022-01-06T16-57-31_short.cine")
EXAMPLE_BIG_CINE = Path("~").expanduser() / "Desktop/2022-11-30T13-41-00.cine"

# GUI
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MARKER_COLOR = BLUE


def init():
    """Initialize the package."""
    check_contrib()
    check_samples_env_var()
    pg.setConfigOption("imageAxisOrder", "row-major")


NO_CONTRIB_MSG = dedent(
    """\
    OpenCV is not installed with extras. A dependent package may have pinned
    `opencv-pyhon` and clobbered your installed version.
    """
)


def check_contrib():
    """Ensure the installed version of OpenCV has extras.

    Dependencies can specify a different version of OpenCV than the one required in this
    project, unintentionally clobbering the installed version of OpenCV. Detect whether
    a non-`contrib` version is installed by a dependency.
    """
    if not version.contrib:
        raise ImportError(NO_CONTRIB_MSG)


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
