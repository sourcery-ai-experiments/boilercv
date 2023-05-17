"""Parameters for the data pipeline."""

from typing import Self

from pydantic import Field

from boilercv import PARAMS_FILE
from boilercv.models import MyBaseModel, load_config
from boilercv.models.paths import LocalPaths, Paths


class Params(MyBaseModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)
    local_paths: LocalPaths = Field(default_factory=LocalPaths)

    @classmethod
    def get_params(cls: type[Self]) -> Self:
        return load_config(PARAMS_FILE, cls)


PARAMS = Params.get_params()
"""All project parameters, including paths."""

# Monkeypatch this when testing. When testing straight-through, sources as yet exist.
SOURCES_TO_ENUMERATE = PARAMS.paths.sources
"""Directory from which to enumerate all project datasets."""
