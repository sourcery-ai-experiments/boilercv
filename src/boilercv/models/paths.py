"""Paths for this project."""

from pathlib import Path
from typing import Any

from pydantic import DirectoryPath, FilePath, validator
from ruamel.yaml import YAML

from boilercv.models import PARAMS_FILE, MyBaseModel

LOCAL_MEDIA = "G:/My Drive/Blake/School/Grad/Reports/Content/boilercv"


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


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class LocalPaths(MyBaseModel):
    """Local paths for larger files not stored in the cloud."""

    data: DirectoryPath = Path("~").expanduser() / ".local/boilercv"
    hierarchical_data: DirectoryPath = data / "data"

    large_examples: DirectoryPath = data / "large_examples"
    large_sources: DirectoryPath = data / "large_sources"
    notes: DirectoryPath = data / "notes"
    sheets: DirectoryPath = data / "sheets"
    uncompressed_contours: DirectoryPath = data / "uncompressed_contours"
    uncompressed_filled: DirectoryPath = data / "uncompressed_filled"
    uncompressed_sources: DirectoryPath = data / "uncompressed_sources"

    cines: DirectoryPath = data / "cines"
    large_example_cine: Path = cines / "2022-01-06T16-57-31.cine"

    media: Path = Path(LOCAL_MEDIA)

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator(
        "hierarchical_data",
        "large_examples",
        "large_sources",
        "notes",
        "sheets",
        "uncompressed_contours",
        "uncompressed_filled",
        "uncompressed_sources",
        "cines",
        always=True,
        pre=True,
    )
    def validate_output_directories(cls, directory: Path) -> Path:
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory


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

    # ! STAGES
    stage_contours: FilePath = stages / "contours.py"
    stage_fill: FilePath = stages / "fill.py"
    stage_schema: FilePath = stages / "schema.py"

    # ! PREVIEW STAGES
    update_previews: DirectoryPath = stages / "update_previews"
    stage_binarized_preview: FilePath = update_previews / "binarized.py"
    stage_gray_preview: FilePath = update_previews / "gray.py"
    stage_filled_preview: FilePath = update_previews / "filled.py"

    # ! DATA
    data: DirectoryPath = Path("data")
    contours: DirectoryPath = data / "contours"
    examples: DirectoryPath = data / "examples"
    filled: DirectoryPath = data / "filled"
    rois: DirectoryPath = data / "rois"
    samples: DirectoryPath = data / "samples"
    sources: DirectoryPath = data / "sources"

    # ! PREVIEW DATA
    previews: DirectoryPath = data / "previews"
    binarized_preview: Path = previews / "binarized.nc"
    gray_preview: Path = previews / "gray.nc"
    filled_preview: Path = previews / "filled.nc"

    # ! SCHEMA
    # Can't be "schema", which is a special member of BaseClass
    project_schema: DirectoryPath = data / "schema"

    # "always" so it'll run even if not in YAML
    # "pre" because dir must exist pre-validation
    @validator(
        "contours",
        "examples",
        "filled",
        "rois",
        "samples",
        "sources",
        "previews",
        "project_schema",
        always=True,
        pre=True,
    )
    def validate_output_directories(cls, directory: Path) -> Path:
        """Re-create designated output directories each run, for reproducibility."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory


# * -------------------------------------------------------------------------------- * #

init()
