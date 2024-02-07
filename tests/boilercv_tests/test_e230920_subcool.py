"""Tests for experiment `e230920_subcool`."""

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import pytest
from pandas.testing import assert_index_equal

from boilercv_tests import Case, get_nb, parametrize_by_cases

pytestmark = pytest.mark.slow

EXP = Path("src/boilercv/stages/experiments/e230920_subcool")
CASES: list[Case] = []

EMPTY_DICT = {}
EMPTY_LIST = []


def C(  # noqa: N802  # A classy function
    name: str,
    id: str = "_",  # noqa: A002
    params: dict[str, Any] = EMPTY_DICT,
    results: dict[str, Any] | Iterable[Any] = EMPTY_DICT,
    marks: Sequence[pytest.Mark] = EMPTY_LIST,
) -> Case:
    """Shorthand for cases."""
    case = Case(
        get_nb(EXP, name),
        id,
        params,
        results if isinstance(results, dict) else dict.fromkeys(results),
        marks,
    )
    CASES.append(case)
    return case


@parametrize_by_cases(C("find_centers"))
def test_centers_index(ns):
    assert_index_equal(
        ns.trackpy_centers.columns,
        ns.centers.columns,
        check_order=False,  # type: ignore  # pyright: 1.1.336, pandas: 2.1.1
    )


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Radius estimate cannot account for large and small bubbles alike",
)
@parametrize_by_cases(
    C("find_collapse", "small_bubbles", {"TIME": "2023-09-20T17:14:18"})
)
def test_find_collapse(ns, figs):
    figs.extend(ns.figures)
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2


@parametrize_by_cases(C("get_thermal_data"))
def test_get_thermal_data(ns):
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)


@pytest.fixture(scope="module")
def nss(fixtures):
    """Namespaces from the tests in this module."""
    return fixtures.ns.test_e230920_subcool


def test_synthesis(nss, plt):
    _, axes = plt.subplots(1, 3)
    axes = iter(axes)
    nss.test_centers_index._.centers.plot.scatter(ax=next(axes), x="x", y="y")
    nss.test_find_collapse.small_bubbles.nondimensionalized_departing_long_lived_objects.plot.scatter(
        ax=next(axes), x="xpx", y="ypx"
    )
    nss.test_get_thermal_data._.data.plot(ax=next(axes))
