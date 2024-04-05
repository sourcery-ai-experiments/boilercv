"""Track bubbles."""

from boilercv_pipeline.models.params import PARAMS


def main():  # noqa: D103
    (PARAMS.paths.tracks / "tracks").touch()


if __name__ == "__main__":
    main()
