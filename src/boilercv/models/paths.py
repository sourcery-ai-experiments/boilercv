"""Paths for this project."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pydantic import DirectoryPath, FilePath, validator
from ruamel.yaml import YAML

from boilercv.models import PARAMS_FILE, MyBaseModel


def init():
    """Synchronize project paths. Run on initial import of this module."""
    yaml = YAML()
    yaml.indent(offset=2)
    paths = Paths()
    params = yaml.load(paths.file_params) or {}
    params["paths"] = repl_path(paths.dict(exclude_none=True))
    yaml.dump(params, paths.file_params)


def repl_path(dirs_dict: dict[str, Path]):
    """Replace Windows path separator with POSIX separator."""
    return {k: str(v).replace("\\", "/") for k, v in dirs_dict.items()}


def iter_sorted(path: Path) -> Iterator[Path]:
    """Iterate over a sorted directory."""
    yield from sorted(path.iterdir())


class Paths(MyBaseModel):
    """Directories relevant to the project."""

    class Config(MyBaseModel.Config):
        @staticmethod
        def schema_extra(schema: dict[str, Any]):
            for prop in schema.get("properties", {}).values():
                default = prop.get("default")
                if isinstance(default, str):
                    prop["default"] = default.replace("\\", "/")

    # ! PARAMS FILE
    file_params: FilePath = PARAMS_FILE

    # ! REQUIREMENTS
    requirements: FilePath = Path("requirements.txt")
    dev_requirements: DirectoryPath = Path(".tools/requirements")

    # ! PACKAGE
    package: DirectoryPath = Path("src") / "boilercv"
    stages: DirectoryPath = package / "stages"
    models: DirectoryPath = package / "models"
    paths_module: FilePath = models / "paths.py"

    # ! DATA
    data: DirectoryPath = Path("data")
    examples: DirectoryPath = data / "examples"

    previews: DirectoryPath = data / "previews"
    binarized_preview: Path = previews / "binarized.nc"

    rois: DirectoryPath = data / "rois"
    samples: DirectoryPath = data / "samples"
    sources: DirectoryPath = data / "sources"

    # ! LOCAL DATA
    local_data: Path = Path("~").expanduser() / ".local/boilercv"
    local_hierarchical_data = local_data / "data"
    cines: Path = local_data / "cines"
    large_examples: Path = local_data / "large_examples"
    large_sources: Path = local_data / "large_sources"
    large_example_cine: Path = cines / "2022-01-06T16-57-31.cine"

    # ! SCHEMA
    # Can't be "schema", which is a special member of BaseClass
    project_schema: DirectoryPath = data / "schema"

    # ! STAGES
    stage_schema: FilePath = stages / "schema.py"
    stage_update_binarized_preview: FilePath = stages / "update_binarized_preview.py"

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator("project_schema", always=True, pre=True)
    def validate_output_directories(cls, directory: Path):
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory


init()
