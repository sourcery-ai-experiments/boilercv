"""Test the pipeline."""

import pytest


@pytest.mark.slow()
@pytest.mark.parametrize(
    "module",
    [
        "binarize",
        "binarized",
        "contours",
        "convert",
        "fill",
        "filled",
        "gray",
    ],
)
def test_boilercv(module, patched_modules):
    patched_modules[module].main()
