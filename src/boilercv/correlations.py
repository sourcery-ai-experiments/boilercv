"""Theoretical correlations for bubble lifetimes."""


import numpy as np

from boilercv.types import Float


def jakob(
    liquid_density: Float,
    vapor_density: Float,
    liquid_specific_heat: Float,
    subcooling: Float,
    latent_heat_of_vaporization: Float,
) -> Float:
    """Jakob number."""
    return (liquid_density * liquid_specific_heat * subcooling) / (
        vapor_density * latent_heat_of_vaporization
    )


def fourier(
    thermal_diffusivity: Float, time: Float, initial_bubble_diameter: Float
) -> Float:
    """Fourier number."""
    return thermal_diffusivity * time / initial_bubble_diameter**2


def dimensionless_bubble_diameter_florschuetz_chao_1965(
    jakob: Float, fourier: Float
) -> Float:
    """Bubble history correlation for condensation of a stagnant bubble.

    Reference: <https://doi.org/10.1115/1.3689075>
    """
    return 1 - 4 * jakob * np.sqrt(fourier) / np.pi
