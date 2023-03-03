from pydantic import Field

from boilercv.models.common import PARAMS_FILE, MyBaseModel, load_config
from boilercv.models.paths import Paths


class Params(MyBaseModel):
    """The global project configuration."""

    paths: Paths = Field(default_factory=Paths)

    @classmethod
    def get_params(cls):
        return load_config(PARAMS_FILE, cls)
