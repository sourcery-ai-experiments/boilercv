from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import DirectoryPath, FilePath, validator

from boilercv.models.common import DATA_DIR, PACKAGE_DIR, PARAMS_FILE, MyBaseModel


class Paths(MyBaseModel):
    """Directories relevant to the project."""

    class Config(MyBaseModel.Config):
        @staticmethod
        def schema_extra(schema: dict[str, Any], model: type[Paths]):
            for prop in schema.get("properties", {}).values():
                default = prop.get("default")
                if isinstance(default, str):
                    prop["default"] = default.replace("\\", "/")

    # ! PARAMS FILE
    file_params: FilePath = PARAMS_FILE

    # ! PACKAGE
    package: DirectoryPath = PACKAGE_DIR
    stages: DirectoryPath = package / "stages"

    # ! DATA
    data: DirectoryPath = DATA_DIR

    # ! SCHEMA
    # Can't be "schema", which is a special member of BaseClass
    project_schema: DirectoryPath = data / "schema"

    # ! STAGES
    stage_setup: FilePath = stages / "setup.py"
    stage_schema: FilePath = stages / "schema.py"

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator(
        "project_schema",
        always=True,
        pre=True,
    )
    def validate_output_directories(cls, directory: Path):
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
