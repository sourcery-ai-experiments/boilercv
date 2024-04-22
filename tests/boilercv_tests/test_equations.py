"""Equations."""

from inspect import Signature

import pytest
from boilercv_pipeline.correlations import (
    dimensionless_bubble_diameter_akiyama_1973,
    dimensionless_bubble_diameter_al_issa_et_al_2014,
    dimensionless_bubble_diameter_chen_mayinger_1992,
    dimensionless_bubble_diameter_florschuetz_chao_1965,
    dimensionless_bubble_diameter_inaba_et_al_2013,
    dimensionless_bubble_diameter_isenberg_sideman_1970,
    dimensionless_bubble_diameter_kalman_mori_2002,
    dimensionless_bubble_diameter_kim_park_2011,
    dimensionless_bubble_diameter_lucic_mayinger_2010,
    dimensionless_bubble_diameter_tang_et_al_2016,
    dimensionless_bubble_diameter_yuan_et_al_2009,
)
from numpy import allclose, linspace

KWDS = {
    "bubble_initial_reynolds": 100.0,
    "liquid_prandtl": 1.0,
    "bubble_jakob": 1.0,
    "bubble_fourier": linspace(0.0, 5e-3, 10),
}
"""Common keyword arguments applied to correlations.

A single test condition has been chosen to exercise each correlation across as wide of a
range as possible without returning `np.nan` values. This is done as follows:

- Let `bubble_initial_reynolds`,
`liquid_prandtl`, and `bubble_jakob` be 100.0, 1.0, and 1.0, respectively.
- Apply the correlation `dimensionless_bubble_diameter_tang_et_al_2016` with
`bubble_fourier` such that the `dimensionless_bubble_diameter` is very close to zero.
This is the correlation with the most rapidly vanishing value of
`dimensionless_bubble_diameter`.
- Choose ten linearly-spaced points for `bubble_fourier` between `0` and the maximum
`bubble_fourier` just found.
"""

# fmt: off
EXPECTED = {
    dimensionless_bubble_diameter_akiyama_1973: [1.000000, 0.995887, 0.991767, 0.987640, 0.983507, 0.979367, 0.975219, 0.971065, 0.966903, 0.962734],
    dimensionless_bubble_diameter_al_issa_et_al_2014: [1.000000, 0.995927, 0.991852, 0.987776, 0.983698, 0.979618, 0.975536, 0.971452, 0.967366, 0.963278],
    dimensionless_bubble_diameter_chen_mayinger_1992: [1.000000, 0.992963, 0.985922, 0.978875, 0.971822, 0.964763, 0.957699, 0.950629, 0.943553, 0.936471],
    dimensionless_bubble_diameter_florschuetz_chao_1965: [1.000000, 0.946807, 0.924774, 0.907868, 0.893615, 0.881058, 0.869705, 0.859266, 0.849549, 0.840423],
    dimensionless_bubble_diameter_inaba_et_al_2013: [1.000000, 0.967928, 0.935856, 0.903785, 0.871713, 0.839642, 0.807570, 0.775499, 0.743427, 0.711355],
    dimensionless_bubble_diameter_isenberg_sideman_1970: [1.000000, 0.993721, 0.987422, 0.981104, 0.974765, 0.968405, 0.962024, 0.955622, 0.949199, 0.942753],
    dimensionless_bubble_diameter_kalman_mori_2002: [1.000000, 0.999766, 0.999532, 0.999298, 0.999064, 0.998830, 0.998596, 0.998363, 0.998129, 0.997895],
    dimensionless_bubble_diameter_kim_park_2011: [1.000000, 0.992802, 0.985588, 0.978359, 0.971113, 0.963852, 0.956573, 0.949278, 0.941967, 0.934638],
    dimensionless_bubble_diameter_lucic_mayinger_2010: [1.000000, 0.973077, 0.946155, 0.919233, 0.892311, 0.865389, 0.838466, 0.811544, 0.784622, 0.757700],
    dimensionless_bubble_diameter_tang_et_al_2016: [1.000000, 0.927931, 0.853449, 0.776152, 0.695500, 0.610738, 0.520744, 0.423701, 0.316230, 0.190161],
    dimensionless_bubble_diameter_yuan_et_al_2009: [1.000000, 0.993324, 0.986629, 0.979915, 0.973182, 0.966429, 0.959656, 0.952864, 0.946050, 0.939216],
}
"""Expected results for each correlation.

Made by running `python -m boilercv_tests.generate` and copying `EXPECTED` from
`tests/plots/applied_correlations.py`.
"""
# fmt: on


@pytest.mark.parametrize(("correlation", "expected"), EXPECTED.items())
def test_correlations(correlation, expected):
    """Test bubble collapse correlations."""
    result = correlation(**{
        kwd: value
        for kwd, value in KWDS.items()
        if kwd in Signature.from_callable(correlation).parameters
    })
    assert allclose(result, expected)
