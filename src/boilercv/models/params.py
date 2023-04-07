"""Parameters for the data pipeline."""

from typing import Self

from pydantic import Field

from boilercv.models import PARAMS_FILE, MyBaseModel, load_config
from boilercv.models.paths import LocalPaths, Paths


class Params(MyBaseModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)

    @classmethod
    def get_params(cls: type[Self]) -> Self:
        return load_config(PARAMS_FILE, cls)


PARAMS = Params.get_params()
LOCAL_PATHS = LocalPaths()
