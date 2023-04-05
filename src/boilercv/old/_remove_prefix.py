"""Remove the "results" prefix from files."""

from pathlib import Path


def main():
    folder = Path("C:/Users/Blake/Desktop/Video")
    videos = sorted(folder.iterdir())
    for video in videos:
        new_name = video.name.removeprefix("results_")
        video.rename(folder / new_name)


if __name__ == "__main__":
    main()
