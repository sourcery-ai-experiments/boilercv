"""Select the subset of data corresponding to unobstructed bubbles."""

from boilercv_pipeline.models.params import PARAMS


def main():
    (PARAMS.paths.unobstructed / "unobstructed").touch()


if __name__ == "__main__":
    main()
