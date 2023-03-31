"""Unpack the bits of a NetCDF file."""


from boilercv.data.packing import unpack
from boilercv.examples.large import example_dataset


def main():
    with example_dataset(source="packed_compressed", destination="unpacked") as ds:
        ds = unpack(ds)


if __name__ == "__main__":
    main()
