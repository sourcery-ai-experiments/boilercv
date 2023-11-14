"""Tests for experiment `e230920_subcool`."""

from pathlib import Path

import pytest
from pandas.testing import assert_index_equal

from boilercv_tests import NsArgs, get_nb

pytestmark = pytest.mark.slow

EXP = Path("src/boilercv/stages/experiments/e230920_subcool")


@pytest.mark.parametrize(
    "ns",
    [pytest.param(NsArgs(get_nb(EXP, "custom_features")), id="cols")],
    indirect=True,
)
def test_custom_features(ns):
    assert_index_equal(ns.objects.columns, ns.my_objects.columns)


@pytest.mark.parametrize(
    "ns",
    [
        pytest.param(
            NsArgs(
                get_nb(EXP, "find_collapse"), params={"TIME": "2023-09-20T17:14:18"}
            ),
            marks=[pytest.mark.xfail(raises=AssertionError)],
            id="small_bubbles",
        )
    ],
    indirect=True,
)
def test_find_collapse(ns):
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2


@pytest.mark.parametrize(
    "ns",
    [pytest.param(NsArgs(get_nb(EXP, "get_thermal_data")), id="subcool")],
    indirect=True,
)
def test_get_thermal_data(ns):
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)
