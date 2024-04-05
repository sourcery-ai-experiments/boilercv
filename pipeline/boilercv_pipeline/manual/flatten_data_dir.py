"""Flatten the data directory structure.

Directory structure looks like

    data
    └───YYYY-MM-DD
        ├───data
        ├───notes
        └───video
"""

from itertools import chain
from pathlib import Path

from boilercv_pipeline.models.params import PARAMS


def main():  # noqa: D103
    source = PARAMS.paths.hierarchical_data
    rename_notes(source)
    rename_cines(source)
    rename_sheets(source)


def rename_notes(source: Path):
    """Rename nested notes."""
    notes_dest = PARAMS.paths.notes
    notes_dirs = {
        trial.stem: trial / "notes"
        for trial in sorted(source.iterdir())
        if trial.is_dir()
    }
    for trial, note_dir in notes_dirs.items():
        if not note_dir.exists():
            continue
        note_dir.rename(notes_dest / trial)


def rename_cines(source: Path):
    """Rename nested cines."""
    destination = PARAMS.paths.cines
    trials = [trial / "video" for trial in source.iterdir() if trial.is_dir()]
    videos = sorted(chain.from_iterable(trial.glob("*.cine") for trial in trials))
    for video in videos:
        video.rename(destination / video.name.removeprefix("results_"))


def rename_sheets(source: Path):
    """Rename nested sheets."""
    sheets_dest = PARAMS.paths.sheets
    data = [trial / "data" for trial in sorted(source.iterdir()) if trial.is_dir()]
    sheets = sorted(chain.from_iterable(trial.glob("*.csv") for trial in data))
    for sheet in sheets:
        sheet.rename(sheets_dest / sheet.name.removeprefix("results_"))


if __name__ == "__main__":
    main()
