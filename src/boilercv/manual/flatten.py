"""Flatten a directory structure of CINE files.

The directory structure looks like

    ~/.local/boilercv/data
    └───YYYY-MM-DD
        └───video
            └───*.cine

"""

from itertools import chain

from boilercv.models.params import PARAMS


def main():
    source = PARAMS.paths.local_hierarchical_data
    destination = PARAMS.paths.cines
    trials = [trial / "video" for trial in source.iterdir() if trial.is_dir()]
    videos = chain.from_iterable(trial.glob("*.cine") for trial in trials)
    for video in videos:
        video.rename(destination / video.name.removeprefix("results_"))


if __name__ == "__main__":
    main()
