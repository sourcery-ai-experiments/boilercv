"""Theoretical correlations for bubble lifetimes."""


import numpy as np

from boilercv.types import Float as F  # noqa: N817


def thermal_diffusivity(thermal_conductivity: F, density: F, isobaric_specific_heat: F):
    """Thermal diffusivity."""
    return thermal_conductivity / (density * isobaric_specific_heat)


def kinematic_viscosity(dynamic_viscosity: F, density: F):
    """Kinematic viscosity."""
    return dynamic_viscosity / density


def reynolds(velocity: F, characteristic_length: F, kinematic_viscosity: F) -> F:
    """Reynolds number."""
    return velocity * characteristic_length / kinematic_viscosity


def prandtl(
    dynamic_viscosity: F, isobaric_specific_heat: F, thermal_conductivity: F
) -> F:
    """Prandtl number."""
    return (isobaric_specific_heat * dynamic_viscosity) / thermal_conductivity


def jakob(
    liquid_density: F,
    vapor_density: F,
    liquid_isobaric_specific_heat: F,
    subcooling: F,
    latent_heat_of_vaporization: F,
) -> F:
    """Jakob number."""
    return (liquid_density * liquid_isobaric_specific_heat * subcooling) / (
        vapor_density * latent_heat_of_vaporization
    )


def fourier(liquid_thermal_diffusivity: F, initial_bubble_diameter: F, time: F) -> F:
    """Fourier number."""
    return liquid_thermal_diffusivity * time / initial_bubble_diameter**2


def dimensionless_bubble_diameter_florschuetz_chao_1965(jakob: F, fourier: F) -> F:
    """Bubble history correlation for condensation of a stagnant bubble.

    Reference: <https://doi.org/10.1115/1.3689075>
    """
    return 1 - 4 * jakob * np.sqrt(fourier) / np.pi


def dimensionless_bubble_diameter_inaba(
    bubble_initial_reynolds: F, liquid_prandtl: F, bubble_jakob: F, bubble_fourier: F
) -> F:
    """Bubble history correlation for condensation of a stagnant bubble.

    Reference: <https://doi.org/10.1115/1.3689075>
    """
    return (
        1
        - 1.1
        * bubble_initial_reynolds**0.86
        * liquid_prandtl ** (2 / 3)
        * bubble_jakob ** (1 / 5)
        * bubble_fourier
    )


def dimensionless_bubble_diameter_yuan(
    bubble_initial_reynolds: F, liquid_prandtl: F, bubble_jakob: F, bubble_fourier: F
) -> F:
    """Bubble history correlation for condensation of a stagnant bubble.

    Reference: <https://doi.org/10.1115/1.3689075>
    """
    return 1 - (
        1.8
        * bubble_initial_reynolds ** (1 / 2)
        * liquid_prandtl ** (1 / 3)
        * bubble_jakob
        * bubble_fourier
        * (1 - 0.5 * bubble_jakob ** (1 / 10) * bubble_fourier)
    ) ** (2 / 3)
