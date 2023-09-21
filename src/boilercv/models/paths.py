"""Project paths."""

from pathlib import Path

from boilercore.models import CreatePathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic import DirectoryPath, FilePath

import boilercv
from boilercv import PROJECT_PATH


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class Paths(CreatePathsModel):
    """Paths associated with project requirements and code."""

    # * Roots
    # ! Project
    project: DirectoryPath = PROJECT_PATH
    # ! Package
    package: DirectoryPath = get_package_dir(boilercv)
    correlations: FilePath = package / "correlations.py"
    models: DirectoryPath = package / "models"
    paths_module: FilePath = models / "paths.py"
    stages: dict[str, FilePath] = map_stages(package / "stages", package)
    # ! Data
    data: DirectoryPath = project / "data"

    # * Git-tracked inputs
    # ! Plotting config
    plot_config: DirectoryPath = data / "plotting"
    mpl_base: FilePath = plot_config / "base.mplstyle"
    mpl_hide_title: FilePath = plot_config / "hide_title.mplstyle"
    # ! Scripts
    scripts: DirectoryPath = data / "scripts"
    # ? Files
    zotero: FilePath = scripts / "zotero.lua"
    filt: FilePath = scripts / "filt.py"
    csl: FilePath = scripts / "international-journal-of-heat-and-mass-transfer.csl"
    template: FilePath = scripts / "template.dotx"

    # * Local inputs
    cines: DirectoryPath = data / "cines"
    example_cines: DirectoryPath = data / "example_cines"
    hierarchical_data: DirectoryPath = data / "hierarchical_data"
    large_examples: DirectoryPath = data / "large_examples"
    large_sources: DirectoryPath = data / "large_sources"
    notes: DirectoryPath = data / "notes"
    profiles: DirectoryPath = data / "profiles"
    sheets: DirectoryPath = data / "sheets"
    uncompressed_contours: DirectoryPath = data / "uncompressed_contours"
    uncompressed_filled: DirectoryPath = data / "uncompressed_filled"
    uncompressed_sources: DirectoryPath = data / "uncompressed_sources"
    # ! Files
    large_example_cine: Path = example_cines / "2022-01-06T16-57-31.cine"

    # * Local results
    docx: DirectoryPath = data / "docx"
    html: DirectoryPath = data / "html"
    md: DirectoryPath = data / "md"
    media: DirectoryPath = data / "media"

    # * DVC-tracked inputs
    docs: DirectoryPath = data / "docs"
    rois: DirectoryPath = data / "rois"
    samples: DirectoryPath = data / "samples"
    sources: DirectoryPath = data / "sources"

    # * DVC-tracked results
    contours: DirectoryPath = data / "contours"
    examples: DirectoryPath = data / "examples"
    filled: DirectoryPath = data / "filled"
    lifetimes: DirectoryPath = data / "lifetimes"
    previews: DirectoryPath = data / "previews"
    tracks: DirectoryPath = data / "tracks"
    unobstructed: DirectoryPath = data / "unobstructed"
    # ! Files
    binarized_preview: Path = previews / "binarized.nc"
    filled_preview: Path = previews / "filled.nc"
    gray_preview: Path = previews / "gray.nc"
