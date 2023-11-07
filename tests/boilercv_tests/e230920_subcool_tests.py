"""Tests against notebook namespaces for experiment `e230920_subcool`.

Note that these are not directly tested, but passed as test parameters.
"""

from types import SimpleNamespace

import pytest


def get_thermal_data(ns: SimpleNamespace):
    """Check mean subcooling."""
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)


def find_collapse(ns: SimpleNamespace):
    """Small bubbles should be found."""
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2
