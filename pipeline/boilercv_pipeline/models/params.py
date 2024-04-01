"""Project parameters."""

from pathlib import Path

from boilercore.models import SynchronizedPathsYamlModel
from pydantic.v1 import Field

from boilercv_pipeline import PROJECT_PATH
from boilercv_pipeline.models.paths import Paths


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)

    def __init__(self, data_file: Path = PROJECT_PATH / "params.yaml", **kwargs):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(data_file, **kwargs)


PARAMS = Params()
"""All project parameters, including paths."""
