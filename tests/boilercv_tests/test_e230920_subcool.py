"""Tests for experiment `e230920_subcool`."""

import pytest

from boilercv_tests.cases.e230920_subcool import CASES

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("cases", CASES["custom_features"], indirect=True)
def test_custom_features(cases):
    ns, fun = cases
    fun(ns)


@pytest.mark.parametrize("cases", CASES["find_collapse"], indirect=True)
def test_find_collapse(cases):
    ns, fun = cases
    fun(ns)


@pytest.mark.parametrize("cases", CASES["get_thermal_data"], indirect=True)
def test_get_thermal_data(cases):
    ns, fun = cases
    fun(ns)
