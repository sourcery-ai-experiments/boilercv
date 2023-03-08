"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from os import environ
from pathlib import Path

from loguru import logger

__version__ = "0.0.0"


def init():
    """Initialize the package."""
    check_samples_env_var()
    logger.configure()


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
