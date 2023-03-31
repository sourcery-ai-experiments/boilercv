"""Paths for this project."""

from __future__ import annotations

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

    # ! DATA
    data: DirectoryPath = Path("data")
    examples: DirectoryPath = data / "examples"
    samples: DirectoryPath = data / "samples"
    sources: DirectoryPath = data / "sources"

    # ! LOCAL DATA
    local_data: Path = Path("~").expanduser() / ".local/boilercv"
    large_examples: Path = local_data / "large_examples"
    large_sources: Path = local_data / "large_sources"
    large_example_cine: Path = large_sources / "2022-01-06T16-57-31.cine"

    # ! SCHEMA
    # Can't be "schema", which is a special member of BaseClass
    project_schema: DirectoryPath = data / "schema"

    # ! STAGES
    stage_schema: FilePath = stages / "schema.py"

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator("project_schema", always=True, pre=True)
    def validate_output_directories(cls, directory: Path):
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory


init()
