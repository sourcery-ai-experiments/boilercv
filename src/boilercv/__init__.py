"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from collections.abc import Iterable, Iterator
from os import environ
from pathlib import Path
from textwrap import dedent

import cv2 as cv
import pyqtgraph as pg
from cv2 import version
from pytz import timezone

from boilercv.types import Img, Img8, NBit, NBit_T

__version__ = "0.0.0"

SAMPLE_DIAMETER_UM = 9_525_000
TIMEZONE = timezone("US/Pacific")
PACKAGE_DIR = Path("src") / "boilercv"
DATA_DIR = Path("data")
CINE_SOURCES = Path("W:/selections")
FRAMES_PER_SOURCE = 300

NO_CONTRIB_MSG = dedent(
    """\
    OpenCV is not installed with extras. A dependent package may have pinned
    `opencv-pyhon` and clobbered your installed version.
    """
)
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

# * -------------------------------------------------------------------------------- * #


def convert_image(image: Img[NBit_T], code: int | None = None) -> Img[NBit_T]:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)  # type: ignore


def get_8bit_images(images: Iterable[Img[NBit]]) -> Iterator[Img8]:
    """Assume images are 8-bit."""
    return (_8_bit(image) for image in images)


def _8_bit(image: Img[NBit]) -> Img8:
    """Assume an image is 8-bit."""
    return image  # type: ignore
