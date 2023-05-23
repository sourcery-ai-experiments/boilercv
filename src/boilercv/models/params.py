"""Parameters for the data pipeline."""


from pydantic import Field

from boilercv import PARAMS_FILE
from boilercv.models import SynchronizedPathsYamlModel
from boilercv.models.paths import LocalPaths, Paths

YAML_INDENT = 2


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)
    local_paths: LocalPaths = Field(default_factory=LocalPaths, exclude=True)

    def __init__(self):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(PARAMS_FILE)


PARAMS = Params()
"""All project parameters, including paths."""

# Monkeypatch this when testing. When testing straight-through, sources as yet exist.
SOURCES_TO_ENUMERATE = PARAMS.paths.sources
"""Directory from which to enumerate all project datasets."""
