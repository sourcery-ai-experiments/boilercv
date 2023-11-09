"""Cases for `find_collapse.ipynb`."""

from types import SimpleNamespace


def small_bubbles(ns: SimpleNamespace):
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2


class case_small_bubbles:
    parameters = {"TIME": "2023-09-20T17:14:18"}

    @staticmethod
    def _(ns: SimpleNamespace):
        small_bubbles(ns)


cases = {small_bubbles: [{"TIME": "2023-09-20T17:14:18"}]}
