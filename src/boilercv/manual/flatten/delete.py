"""Delete nested CINEs from already processed data.

The directory structure looks like

    data
    └───YYYY-MM-DD
        └───video
            └───*.cine
"""

from pathlib import Path
from shutil import rmtree

from loguru import logger

ENABLE = False
"""Enable this flag when it is time to delete these files."""

PROMPT = "Are you sure you want to delete video directories on Google Drive? [n]"
"""Second line of defense."""

SOURCE = "G:/My Drive/Blake/School/Grad/Projects/18.09 Nucleate Pool Boiling/Data/Boiling Curves"
"""Contains the hierarchical folder structure with videos to be deleted."""


def main():
    source = Path(SOURCE)
    trials = sorted([trial / "video" for trial in source.iterdir() if trial.is_dir()])
    for trial in trials:
        logger.info(f"Will delete {trial.relative_to(source)}")
        if ENABLE:
            response = input(PROMPT).casefold() or "n"
            if response == "y":
                rmtree(trial)


if __name__ == "__main__":
    main()
