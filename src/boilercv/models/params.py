"""Project parameters."""

from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field

from boilercv import PARAMS_FILE
from boilercv.models.paths import LocalPaths, Paths, ProjectPaths


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    project_paths: ProjectPaths = Field(default_factory=ProjectPaths)
    paths: Paths = Field(default_factory=Paths)
    local_paths: LocalPaths = Field(default_factory=LocalPaths, exclude=True)

    def __init__(self):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(PARAMS_FILE)


PARAMS = Params()
"""All project parameters, including paths."""
