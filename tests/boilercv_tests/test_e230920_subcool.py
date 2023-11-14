"""Tests for experiment `e230920_subcool`."""

from pathlib import Path
from typing import NamedTuple

import pytest
from boilercore.testing import NO_MARKS, NO_PARAMS, Params
from pandas.testing import assert_index_equal

from boilercv_tests import NsArgs, get_nb

pytestmark = pytest.mark.slow


class P(NamedTuple):
    """Local test parameter shorthand."""

    nb: str
    id: str  # noqa: A003
    params: Params = NO_PARAMS
    all_results: bool = False
    marks: list[pytest.Mark] = NO_MARKS


def _parametrize(*params: P):
    """Local test parametrization shorthand."""
    return pytest.mark.parametrize(
        "ns",
        [
            pytest.param(
                NsArgs(
                    nb=get_nb(
                        Path("src/boilercv/stages/experiments/e230920_subcool"), p.nb
                    ),
                    params=p.params,
                    all_results=p.all_results,
                ),
                marks=p.marks,
                id=p.id,
            )
            for p in params
        ],
        indirect=["ns"],
    )


@_parametrize(P("custom_features", "cols"))
def test_custom_features(ns):
    assert_index_equal(ns.objects.columns, ns.my_objects.columns)


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Radius estimate cannot account for large and small bubbles alike",
)
@_parametrize(P("find_collapse", "small_bubbles", {"TIME": "2023-09-20T17:14:18"}))
def test_find_collapse(ns):
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2


@_parametrize(P("get_thermal_data", "subcool"))
def test_get_thermal_data(ns):
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)
