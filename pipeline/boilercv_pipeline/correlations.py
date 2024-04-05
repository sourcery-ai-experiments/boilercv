"""Theoretical correlations for bubble lifetimes."""

from typing import Any

from numpy import pi, sqrt

T = Any
"""Can't figure out typing of these for now, will revisit later."""


def thermal_diffusivity(
    thermal_conductivity: T, density: T, isobaric_specific_heat: T
) -> T:
    """Thermal diffusivity."""
    return thermal_conductivity / (density * isobaric_specific_heat)


def kinematic_viscosity(dynamic_viscosity: T, density: T) -> T:
    """Kinematic viscosity."""
    return dynamic_viscosity / density


def reynolds(velocity: T, characteristic_length: T, kinematic_viscosity: T) -> T:
    """Reynolds number."""
    return velocity * characteristic_length / kinematic_viscosity


def prandtl(
    dynamic_viscosity: T, isobaric_specific_heat: T, thermal_conductivity: T
) -> T:
    """Prandtl number."""
    return (isobaric_specific_heat * dynamic_viscosity) / thermal_conductivity


def jakob(
    liquid_density: T,
    vapor_density: T,
    liquid_isobaric_specific_heat: T,
    subcooling: T,
    latent_heat_of_vaporization: T,
) -> T:
    """Jakob number."""
    return (liquid_density * liquid_isobaric_specific_heat * subcooling) / (
        vapor_density * latent_heat_of_vaporization
    )


def fourier(liquid_thermal_diffusivity: T, initial_bubble_diameter: T, time: T) -> T:
    """Fourier number."""
    return liquid_thermal_diffusivity * time / initial_bubble_diameter**2


def dimensionless_bubble_diameter_florschuetz(jakob: T, fourier: T) -> T:
    """Bubble history correlation for condensation of a stagnant bubble {cite}`florschuetzMechanicsVaporBubble1965,tangReviewDirectContact2022`."""
    return 1 - 4 * jakob * sqrt(fourier / pi)


def dimensionless_bubble_diameter_tang(
    bubble_initial_reynolds: T, liquid_prandtl: T, bubble_jakob: T, bubble_fourier: T
) -> T:
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    # assert 1_000 < bubble_initial_reynolds < 30_000
    # assert 45 < bubble_jakob < 80
    # assert 2.1 < liquid_prandtl < 4.3
    return (
        1
        - 12.29
        * bubble_initial_reynolds**0.584
        * liquid_prandtl**0.333
        * bubble_jakob**0.581
        * bubble_fourier
    ) ** 0.706


def dimensionless_bubble_diameter_yuan(
    bubble_initial_reynolds: T, liquid_prandtl: T, bubble_jakob: T, bubble_fourier: T
) -> T:
    """Bubble history correlation for condensation of a stagnant bubble {cite}`yuandewenCondensationHeatTransfer2009,tangReviewDirectContact2022`."""
    # assert 335 < bubble_initial_reynolds < 1770
    # assert 0 < bubble_jakob < 60
    # assert 1.71 < liquid_prandtl < 1.75
    return (
        1
        - 1.8
        * bubble_initial_reynolds**0.5
        * liquid_prandtl ** (1 / 3)
        * bubble_jakob
        * bubble_fourier
        * (1 - 0.5 * bubble_jakob**0.1 * bubble_fourier)
    ) ** (2 / 3)


def dimensionless_bubble_diameter_inaba(
    bubble_initial_reynolds: T, liquid_prandtl: T, bubble_jakob: T, bubble_fourier: T
) -> T:
    """Bubble history correlation for condensation of a stagnant bubble. {cite}`tangReviewDirectContact2022`."""
    # assert 7_000 < bubble_initial_reynolds < 70_000
    # assert 0.24 < bubble_jakob < 27
    return (
        1
        - 1.1
        * bubble_initial_reynolds**0.86
        * liquid_prandtl ** (2 / 3)
        * bubble_jakob**0.2
        * bubble_fourier
    )
