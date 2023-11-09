"""Tests."""

from importlib import import_module

import numpy as np
import pytest

from boilercv_tests import STAGES


def test_correlations():
    """Test bubble collapse correlations."""

    from boilercv.correlations import (
        dimensionless_bubble_diameter_florschuetz,
        fourier,
        jakob,
    )

    result = dimensionless_bubble_diameter_florschuetz(
        jakob(
            liquid_density=1000,  # kg/m^3
            vapor_density=0.804,  # kg/m^3
            liquid_isobaric_specific_heat=4180,  # J/kg-K
            subcooling=2,  # K
            latent_heat_of_vaporization=2.23e6,  # J/kg
        ),
        fourier(
            liquid_thermal_diffusivity=1.43e-7,  # m^2/s
            time=np.linspace(0, 0.2, 10),  # s
            initial_bubble_diameter=0.001,  # m
        ),
    )
    expected = np.array(  # m/m
        [
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
        ]
    )
    assert np.allclose(result, expected)


@pytest.mark.slow()
@pytest.mark.parametrize("stage", STAGES)
def test_stages(stage: str):
    """Test that stages can run."""
    import_module(stage).main()
