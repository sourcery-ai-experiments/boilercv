"""Pack the bits of a NetCDF file."""

from boilercv.data.packing import pack
from boilercv.examples.large import example_dataset


def main():
    with example_dataset(source="binarized", destination="packed") as ds:
        ds = pack(ds)


if __name__ == "__main__":
    main()
