"""Select the subset of data corresponding to unobstructed bubbles."""

from boilercv_pipeline.models.params import PARAMS


def main():  # noqa: D103
    (PARAMS.paths.unobstructed / "unobstructed").touch()


if __name__ == "__main__":
    main()
