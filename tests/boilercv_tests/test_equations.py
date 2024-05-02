"""Equations."""

from inspect import Signature
from tomllib import loads

import numpy
import pytest
from boilercv_pipeline import correlations
from boilercv_pipeline.correlations import symbolic
from boilercv_pipeline.correlations.symbolic import dimensionless_bubble_diameter
from boilercv_pipeline.equations import EQS, EXPECT, KWDS, MANUAL_SYMPY, NAME, TOML
from numpy import allclose
from sympy import lambdify

TOML_EQUATIONS = {eq[NAME]: eq[EXPECT] for eq in loads(TOML.read_text("utf-8"))[EQS]}
"""Expected results for TOML-encoded equations."""
# fmt: off
EXPECTED2 = {f"dimensionless_bubble_diameter_{name}": expected for name, expected in {
    "al_issa_et_al_2014": [1.000000, 0.995927, 0.991852, 0.987776, 0.983698, 0.979618, 0.975536, 0.971452, 0.967366, 0.963278],
    "chen_mayinger_1992": [1.000000, 0.992963, 0.985922, 0.978875, 0.971822, 0.964763, 0.957699, 0.950629, 0.943553, 0.936471],
    "inaba_et_al_2013": [1.000000, 0.967928, 0.935856, 0.903785, 0.871713, 0.839642, 0.807570, 0.775499, 0.743427, 0.711355],
    "kalman_mori_2002": [1.000000, 0.999766, 0.999532, 0.999298, 0.999064, 0.998830, 0.998596, 0.998363, 0.998129, 0.997895],
    "kim_park_2011": [1.000000, 0.992802, 0.985588, 0.978359, 0.971113, 0.963852, 0.956573, 0.949278, 0.941967, 0.934638],
    "lucic_mayinger_2010": [1.000000, 0.973077, 0.946155, 0.919233, 0.892311, 0.865389, 0.838466, 0.811544, 0.784622, 0.757700],
    "tang_et_al_2016": [1.000000, 0.927931, 0.853449, 0.776152, 0.695500, 0.610738, 0.520744, 0.423701, 0.316230, 0.190161],
}.items()} | TOML_EQUATIONS
"""Expected results for each correlation.

Made by running `python -m boilercv_tests.generate` and copying `EXPECTED` from
`tests/plots/applied_correlations.py`.
"""
# fmt: on


@pytest.mark.parametrize(("name", "expected"), EXPECTED2.items())
def test_python(name, expected):
    """Equations evaluate as expected."""
    equation = getattr(correlations, name)
    result = equation(**{
        kwd: value
        for kwd, value in KWDS.items()
        if kwd in Signature.from_callable(equation).parameters
    })
    assert allclose(result, expected)


@pytest.mark.parametrize("symbol_group_name", ["SYMS", "LONG_SYMS"])
def test_syms(symbol_group_name: str):
    """Declared symbolic variables assigned to correct symbols."""
    mod = symbolic
    symbols = [
        group_sym.name
        for group_sym in getattr(mod.dimensionless_bubble_diameter, symbol_group_name)
    ]
    variables = [
        name for name in symbols if getattr(mod.dimensionless_bubble_diameter, name)
    ]
    assert symbols == variables


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        (name.removeprefix("dimensionless_bubble_diameter_"), expected)
        for name, expected in EXPECTED2.items()
        if name.removeprefix("dimensionless_bubble_diameter_") in MANUAL_SYMPY
    ),
)
def test_sympy(name, expected):
    """Symbolic equations evaluate as expected."""
    mod = dimensionless_bubble_diameter
    correlation = lambdify(
        expr=(expr := getattr(mod, name).rhs.subs(mod.SUBS)),
        modules=numpy,
        args=[s for s in expr.free_symbols if s.name in mod.SUBS.values()],  # type: ignore
    )
    result = correlation(**{
        kwd: value
        for kwd, value in KWDS.items()
        if kwd in Signature.from_callable(correlation).parameters
    })
    assert allclose(result, expected)
