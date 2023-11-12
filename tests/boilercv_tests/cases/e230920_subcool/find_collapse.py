"""Cases for `find_collapse.ipynb`."""

from types import SimpleNamespace

import pytest

parameters = {"TIME": "2023-09-20T17:14:18"}
results = ["nondimensionalized_departing_long_lived_objects"]
marks = [pytest.mark.xfail(raises=AssertionError)]


def case_small_bubbles(ns: SimpleNamespace):
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2
