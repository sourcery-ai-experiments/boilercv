"""Data pipeline."""

from collections.abc import Callable
from os import environ
from pathlib import Path
from typing import Any

from loguru import logger
from pandas import set_option

PROJECT_PATH = Path()
"""Path to the project root, where `params.yaml` will go."""

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
    set_option("mode.copy_on_write", True)
    set_option("mode.chained_assignment", "raise")
    set_option("mode.string_storage", "pyarrow")


def run_example(func: Callable[..., Any], preview: bool = False) -> tuple[str, Any]:
    """Run an example file, logging the module name containing the function.

    Args:
        func: The example function to run.
        preview: Preview results from the function. Default: False.
    """
    module_name = func.__module__
    logger.info(f'Running example "{module_name}"')
    result = func(preview=preview)
    return module_name, result


init()
