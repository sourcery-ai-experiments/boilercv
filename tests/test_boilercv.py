"""Test individual parts."""

import numpy as np

from boilercv.correlations import (
    dimensionless_bubble_diameter_florschuetz_chao_1965,
    fourier,
    jakob,
)


def test_correlations():
    """Test bubble collapse correlations."""
    result = dimensionless_bubble_diameter_florschuetz_chao_1965(
        jakob(
            liquid_density=1000,  # kg/m^3
            vapor_density=0.804,  # kg/m^3
            liquid_specific_heat=4180,  # J/kg-K
            subcooling=2,  # K
            latent_heat_of_vaporization=2.23e6,  # J/kg
        ),
        fourier(
            thermal_diffusivity=1.43e-7,  # m^2/s
            time=np.linspace(0, 0.2, 10),  # s
            initial_bubble_diameter=0.001,  # m
        ),
    )
    expected = np.array(  # m/m
        [
            1.0,
            0.66532964,
            0.52670464,
            0.42033394,
            0.33065929,
            0.25165433,
            0.18022839,
            0.11454547,
            0.05340929,
            -0.00401107,
        ]
    )
    assert np.allclose(result, expected)
