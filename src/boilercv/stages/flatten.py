"""Flatten a directory structure of CINE files.

The directory structure looks like

    C:/Users/Blake/Desktop/Results
    └───YYYY-MM-DD
        └───video
            └───*.cine

"""

from itertools import chain
from pathlib import Path


def main():
    source = Path("C:/Users/Blake/Desktop/Results")
    destination = Path("C:/Users/Blake/Desktop/Video")
    trials = [trial / "video" for trial in source.iterdir() if trial.is_dir()]
    videos = chain.from_iterable(trial.glob("*.cine") for trial in trials)
    for video in videos:
        video.rename(destination / video.name)


if __name__ == "__main__":
    main()
