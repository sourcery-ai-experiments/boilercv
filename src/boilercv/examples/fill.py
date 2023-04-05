"""Fill bubble contours."""


import pandas as pd

from boilercv.examples import EXAMPLE_CONTOURS


def main():
    df = pd.read_hdf(EXAMPLE_CONTOURS)
    ...


if __name__ == "__main__":
    main()
