"""Cases for `find_collapse.ipynb`."""

from types import SimpleNamespace

import pytest


class case_small_bubbles:
    parameters = {"TIME": "2023-09-20T17:14:18"}
    marks = [pytest.mark.xfail(raises=AssertionError)]

    @staticmethod
    def _(ns: SimpleNamespace):
        objects = ns.nondimensionalized_departing_long_lived_objects
        assert objects["Dimensionless bubble diameter"].min() < 0.2
