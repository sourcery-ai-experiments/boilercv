"""Paths for this project."""

from pathlib import Path

from pydantic import DirectoryPath, FilePath

from boilercv import DATA_DIR, LOCAL_DATA, PROJECT_DIR
from boilercv.models import CreatePathsModel


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class ProjectPaths(CreatePathsModel):
    """Paths associated with project requirements and code."""

    project: DirectoryPath = PROJECT_DIR

    # ! REQUIREMENTS
    requirements: FilePath = project / "requirements.txt"
    dev_requirements: DirectoryPath = project / ".tools/requirements"

    # ! PACKAGE
    package: DirectoryPath = project / "src/boilercv"
    stages: DirectoryPath = package / "stages"
    models: DirectoryPath = package / "models"
    paths_module: FilePath = models / "paths.py"

    # ! PLOT CONFIG
    plot_config: DirectoryPath = project / "plotting"
    mpl_base: FilePath = plot_config / "base.mplstyle"
    mpl_hide_title: FilePath = plot_config / "hide_title.mplstyle"

    # ! SCRIPTS
    scripts: DirectoryPath = project / "scripts"
    zotero: FilePath = scripts / "zotero.lua"
    csl: FilePath = scripts / "international-journal-of-heat-and-mass-transfer.csl"
    template: FilePath = scripts / "template.dotx"

    # ! STAGES
    stage_find_contours: FilePath = stages / "find_contours.py"
    stage_fill: FilePath = stages / "fill.py"
    stage_find_tracks: FilePath = stages / "find_tracks.py"
    stage_find_unobstructed: FilePath = stages / "find_unobstructed.py"
    stage_compare_theory: FilePath = stages / "compare_theory.py"

    # ! PREVIEW STAGES
    preview: DirectoryPath = stages / "preview"
    stage_preview_binarized: FilePath = preview / "preview_binarized.py"
    stage_preview_gray: FilePath = preview / "preview_gray.py"
    stage_preview_filled: FilePath = preview / "preview_filled.py"

    # ! STAGE DEPENDENCIES
    correlations: FilePath = package / "correlations.py"


class Paths(CreatePathsModel):
    """Paths associated with project data."""

    data: DirectoryPath = DATA_DIR

    # ! STAGE DATA
    contours: DirectoryPath = data / "contours"
    examples: DirectoryPath = data / "examples"
    filled: DirectoryPath = data / "filled"
    lifetimes: DirectoryPath = data / "lifetimes"
    rois: DirectoryPath = data / "rois"
    samples: DirectoryPath = data / "samples"
    sources: DirectoryPath = data / "sources"
    tracks: DirectoryPath = data / "tracks"
    unobstructed: DirectoryPath = data / "unobstructed"

    # ! PREVIEW DATA
    previews: DirectoryPath = data / "previews"
    binarized_preview: Path = previews / "binarized.nc"
    gray_preview: Path = previews / "gray.nc"
    filled_preview: Path = previews / "filled.nc"

    # ! PROJECT DOCUMENTATION
    docs: DirectoryPath = data / "docs"
    docx: DirectoryPath = data / "docx"
    md: DirectoryPath = data / "md"


class LocalPaths(CreatePathsModel):
    """Local paths for larger files not stored in the cloud."""

    data: DirectoryPath = LOCAL_DATA
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

    media: Path = Path("G:/My Drive/Blake/School/Grad/Reports/Content/boilercv")
    html: Path = Path(
        "~/code/mine/notes/data/local/vaults/grad/_imports/boilercv"
    ).expanduser()
