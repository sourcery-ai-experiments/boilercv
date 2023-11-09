"""Cases for `get_thermal_data`."""

from types import SimpleNamespace

import pytest


class case_boil:
    parameters = {"BOILING": 95}

    @staticmethod
    def case_95(ns: SimpleNamespace):
        assert ns.BOILING == 95


def case_subcool(ns: SimpleNamespace):
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)
