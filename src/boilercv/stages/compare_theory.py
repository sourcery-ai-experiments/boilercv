"""Bubble lifetimes compared with theoretical correlations."""
from boilercv.models.params import PARAMS


def main():
    (PARAMS.paths.lifetimes / "theory").touch()


if __name__ == "__main__":
    main()
