"""Track bubbles."""

from boilercv_pipeline.models.params import PARAMS


def main():
    (PARAMS.paths.tracks / "tracks").touch()


if __name__ == "__main__":
    main()
