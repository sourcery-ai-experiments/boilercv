"""Tests for experiment `e230920_subcool`."""

import pytest
from boilercore.paths import get_module_name
from boilercore.testing import get_ns_cases

from boilercv_tests import NB_STAGES
from boilercv_tests.cases.e230920_subcool import find_collapse, get_thermal_data

pytestmark = pytest.mark.slow

E230920_SUBCOOL = "boilercv.stages.experiments.e230920_subcool"
CASES = {
    case: get_ns_cases(NB_STAGES[f"{E230920_SUBCOOL}.{get_module_name(case)}"], case)
    for case in [get_thermal_data, find_collapse]
}


@pytest.mark.parametrize(("ns", "case"), CASES[get_thermal_data], indirect=["ns"])
def test_get_thermal_data(ns, case):
    case(ns)


@pytest.mark.xfail(raises=AssertionError)
@pytest.mark.parametrize(("ns", "case"), CASES[find_collapse], indirect=["ns"])
def test_find_collapse(ns, case):
    case(ns)
