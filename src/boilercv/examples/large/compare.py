"""Compare the original binarized dataset with the round-tripped dataset."""

from boilercv import DEBUG
from boilercv.examples.large import example_dataset as ex_ds

KW = dict(preview=DEBUG, save=False)


def main():
    with ex_ds("binarized", **KW) as original, ex_ds("unpacked", **KW) as unpacked:
        assert unpacked.identical(original)


if __name__ == "__main__":
    main()
