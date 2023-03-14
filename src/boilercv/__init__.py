"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from os import environ
from pathlib import Path
from textwrap import dedent

from cv2 import version

__version__ = "0.0.0"


def init():
    """Initialize the package."""
    check_contrib()
    check_samples_env_var()


NO_CONTRIB_MSG = dedent(
    """\
    OpenCV is not installed with extras. A dependent package may have pinned
    `opencv-pyhon` and clobbered your installed version.
    """
)
WHITE = (255, 255, 255)
MARKER_COLOR = (0, 0, 255)
ESC_KEY = ord("\x1b")


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
