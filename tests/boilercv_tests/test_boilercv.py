"""Tests."""

from importlib import import_module
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
    fourier,
    jakob,
    prandtl,
    reynolds,
)
from numpy import allclose, array, linspace, nan

from boilercv_tests import STAGES

EQUAL_NAN = True

KWDS = {
    "bubble_initial_reynolds": reynolds(
        velocity=0.1,  # m/s
        characteristic_length=0.001,  # m
        kinematic_viscosity=1e-6,  # m^2/s
    ),
    "liquid_prandtl": prandtl(
        dynamic_viscosity=1e-3,  # Pa-s
        isobaric_specific_heat=4180,  # J/kg-K
        thermal_conductivity=0.6,  # W/m-K
    ),
    "bubble_jakob": jakob(
        liquid_density=1000,  # kg/m^3
        vapor_density=0.804,  # kg/m^3
        liquid_isobaric_specific_heat=4180,  # J/kg-K
        subcooling=2,  # K
        latent_heat_of_vaporization=2.23e6,  # J/kg
    ),
    "bubble_fourier": fourier(
        liquid_thermal_diffusivity=1.43e-7,  # m^2/s
        initial_bubble_diameter=0.001,  # m
        time=linspace(0, 0.2, 10),  # s
    ),
}


EXPECTED = {
    dimensionless_bubble_diameter_akiyama_1973: array([
        1.0,
        0.78055897,
        0.53243403,
        0.22065206,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
    ]),
    dimensionless_bubble_diameter_al_issa_et_al_2014: array([
        1.0,
        0.79136882,
        0.57642113,
        0.35199827,
        0.10863999,
        nan,
        nan,
        nan,
        nan,
        nan,
    ]),
    dimensionless_bubble_diameter_chen_mayinger_1992: array([
        1.0,
        0.48727464,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
    ]),
    dimensionless_bubble_diameter_florschuetz_chao_1965: array([
        1.00000000,
        0.40681224,
        0.16110582,
        -0.02743134,
        -0.18637552,
        -0.32640816,
        -0.45300734,
        -0.5694273,
        -0.67778836,
        -0.77956329,
    ]),
    dimensionless_bubble_diameter_inaba_et_al_2013: array([
        1.0,
        0.0895377,
        -0.82092461,
        -1.73138691,
        -2.64184922,
        -3.55231152,
        -4.46277383,
        -5.37323613,
        -6.28369844,
        -7.19416074,
    ]),
    dimensionless_bubble_diameter_isenberg_sideman_1970: array([
        1.0,
        0.64748913,
        0.12087821,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
    ]),
    dimensionless_bubble_diameter_kalman_mori_2002: array([
        1.0,
        0.96713401,
        0.93410469,
        0.90090455,
        0.86752541,
        0.83395833,
        0.80019348,
        0.76622,
        0.73202587,
        0.69759769,
    ]),
    dimensionless_bubble_diameter_kim_park_2011: array([
        1.0,
        0.94173421,
        0.88236392,
        0.82176745,
        0.75979638,
        0.69626612,
        0.63094155,
        0.5635141,
        0.49356299,
        0.4204842,
    ]),
    dimensionless_bubble_diameter_lucic_mayinger_2010: array([
        1.0,
        0.15458502,
        -0.69082996,
        -1.53624493,
        -2.38165991,
        -3.22707489,
        -4.07248987,
        -4.91790485,
        -5.76331982,
        -6.6087348,
    ]),
    dimensionless_bubble_diameter_tang_et_al_2016: array([
        1.0,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
    ]),
    dimensionless_bubble_diameter_yuan_et_al_2009: array([
        1.0,
        0.62284694,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
        nan,
    ]),
}


@pytest.mark.parametrize(("correlation", "expected"), EXPECTED.items())
def test_correlations(correlation, expected):
    """Test bubble collapse correlations."""
    result = correlation(**{
        kwd: value
        for kwd, value in KWDS.items()
        if kwd in Signature.from_callable(correlation).parameters
    })
    assert allclose(result, expected, equal_nan=EQUAL_NAN)


@pytest.mark.slow()
@pytest.mark.parametrize("stage", STAGES)
def test_stages(stage: str):
    """Test that stages can run."""
    import_module(stage).main()
