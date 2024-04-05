"""Bubble lifetimes compared with theoretical correlations."""

from boilercv_pipeline.models.params import PARAMS


def main():  # noqa: D103
    (PARAMS.paths.lifetimes / "theory").touch()


if __name__ == "__main__":
    main()
