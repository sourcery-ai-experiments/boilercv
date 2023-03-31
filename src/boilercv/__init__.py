"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from os import environ
from pathlib import Path
from textwrap import dedent

import pyqtgraph as pg
from cv2 import version
from loguru import logger
from ruamel.yaml import YAML

__version__ = "0.0.0"

# Debugging
DEBUG = False
if DEBUG:
    logger.add(sink="boilercv.log")
    FRAMES_PER_SOURCE = 800
else:
    FRAMES_PER_SOURCE = 0

# Internal paths
PACKAGE_DIR = Path("src") / "boilercv"
DATA_DIR = Path("data")
SOURCES = DATA_DIR / "sources"
EXAMPLE_CINE = Path("2022-11-30T13-41-00_short.cine")
EXAMPLE_CINE_ZOOMED = Path("2022-01-06T16-57-31_short.cine")

# External paths
DESKTOP = Path("~").expanduser() / "Desktop"
LARGE_SOURCES = DESKTOP / "large_sources"
LARGE_EXAMPLES = DESKTOP / "large_examples"
EXAMPLE_FULL_CINE = LARGE_SOURCES / "2022-01-06T16-57-31.cine"


def init():
    """Initialize the package."""
    check_contrib()
    check_samples_env_var()
    synchronize_paths()
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


def synchronize_paths():
    """Synchronize project paths."""

    from boilercv.models.paths import Paths

    yaml = YAML()
    yaml.indent(offset=2)
    paths = Paths()
    params = yaml.load(paths.file_params) or {}
    params["paths"] = repl_path(paths.dict(exclude_none=True))
    yaml.dump(params, paths.file_params)


def repl_path(dirs_dict: dict[str, Path]):
    """Replace Windows path separator with POSIX separator."""
    return {k: str(v).replace("\\", "/") for k, v in dirs_dict.items()}


init()
