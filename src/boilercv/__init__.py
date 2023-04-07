"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from os import environ

import pandas as pd
from cv2 import version
from loguru import logger

__version__ = "0.0.0"

_debug = environ.get("BOILERCV_DEBUG")
_preview = environ.get("BOILERCV_PREVIEW")
_write = environ.get("BOILERCV_WRITE")
DEBUG = str(_debug).casefold() == "true" if _debug else False
"""Whether to run in debug mode. Log to `boilercv.log`."""
PREVIEW = str(_preview).casefold() == "true" if _preview else False
"""Whether to run interactive previews."""
WRITE = str(_write).casefold() == "true" if _write else False
"""Whether to write to the local media folder."""


def init():
    """Initialize `boilercv`."""
    if DEBUG:
        logger.add(sink="boilercv.log")
    check_contrib()
    pd.set_option("mode.copy_on_write", True)
    pd.set_option("mode.chained_assignment", "raise")
    pd.set_option("mode.string_storage", "pyarrow")


_CONTRIB_MSG = """\
OpenCV is not installed with extras. A dependent package may have pinned `opencv-pyhon`
and clobbered your installed version.
"""


def check_contrib():
    """Ensure the installed version of OpenCV has extras.

    Dependencies can specify a different version of OpenCV than the one required in this
    project, unintentionally clobbering the installed version of OpenCV. Detect whether
    a non-`contrib` version is installed by a dependency.
    """
    if not version.contrib:
        raise ImportError(_CONTRIB_MSG)


init()
