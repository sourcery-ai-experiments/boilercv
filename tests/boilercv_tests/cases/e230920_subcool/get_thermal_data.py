"""Cases for `get_thermal_data`."""

from types import SimpleNamespace

import pytest

results = ["data"]


def case_subcool(ns: SimpleNamespace):
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)
