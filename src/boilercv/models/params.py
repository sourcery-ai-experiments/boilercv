"""Parameters for the data pipeline."""

from typing import Self

from pydantic import Field

from boilercv import DEBUG, NUM_FRAMES
from boilercv.models import PARAMS_FILE, MyBaseModel, load_config
from boilercv.models.paths import Paths


class Params(MyBaseModel):
    """Project parameters."""

    debug: bool = DEBUG
    """Whether to run in debug mode. Log to `boilercv.log` and grab fewer frames."""
    paths: Paths = Field(default_factory=Paths)
    num_frames: int = NUM_FRAMES
    """The number of frames to read for a given video."""

    @classmethod
    def get_params(cls: type[Self]) -> Self:
        return load_config(PARAMS_FILE, cls)


PARAMS = Params.get_params()
