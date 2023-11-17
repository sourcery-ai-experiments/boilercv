"""Tests for experiment `e230920_subcool`."""

from pathlib import Path
from typing import NamedTuple

import pytest
from boilercore.testing import Params
from pandas.testing import assert_index_equal

from boilercv_tests import NsArgs, get_nb

EXP = "e230920_subcool"

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def nss(fixtures):
    return fixtures.ns.test_e230920_subcool


NO_PARAMS = {}
NO_MARKS = []


class P(NamedTuple):
    """Local test parameter shorthand."""

    nb: str
    id: str  # noqa: A003
    params: Params = NO_PARAMS
    marks: list[pytest.Mark] = NO_MARKS


def _parametrize(*params: P):
    """Local test parametrization shorthand."""
    return pytest.mark.parametrize(
        "ns",
        [
            pytest.param(
                NsArgs(
                    nb=get_nb(Path(f"src/boilercv/stages/experiments/{EXP}"), p.nb),
                    params=p.params,
                ),
                marks=p.marks,
                id=p.id,
            )
            for p in params
        ],
        indirect=["ns"],
    )


@_parametrize(P("custom_features", "cols"))
def test_custom_features(ns, ax):
    ns.objects.plot(ax=ax)
    assert_index_equal(ns.objects.columns, ns.my_objects.columns, check_order=False)  # type: ignore


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


def test_synthesis(nss, plt):
    _, axes = plt.subplots(1, 3)
    axes = iter(axes)
    nss.test_custom_features.cols.objects.plot(ax=next(axes))
    nss.test_find_collapse.small_bubbles.nondimensionalized_departing_long_lived_objects.plot(
        ax=next(axes)
    )
    nss.test_get_thermal_data.subcool.data.plot(ax=next(axes))
