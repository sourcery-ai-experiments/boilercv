"""Theoretical correlations for bubble lifetimes."""

from numpy import pi, sqrt


def thermal_diffusivity(thermal_conductivity, density, isobaric_specific_heat):
    """Thermal diffusivity."""
    return thermal_conductivity / (density * isobaric_specific_heat)


def kinematic_viscosity(dynamic_viscosity, density):
    """Kinematic viscosity."""
    return dynamic_viscosity / density


def reynolds(velocity, characteristic_length, kinematic_viscosity):
    """Reynolds number."""
    return velocity * characteristic_length / kinematic_viscosity


def prandtl(dynamic_viscosity, isobaric_specific_heat, thermal_conductivity):
    """Prandtl number."""
    return (isobaric_specific_heat * dynamic_viscosity) / thermal_conductivity


def jakob(
    liquid_density,
    vapor_density,
    liquid_isobaric_specific_heat,
    subcooling,
    latent_heat_of_vaporization,
):
    """Jakob number."""
    return (liquid_density * liquid_isobaric_specific_heat * subcooling) / (
        vapor_density * latent_heat_of_vaporization
    )


def fourier(liquid_thermal_diffusivity, initial_bubble_diameter, time):
    """Fourier number."""
    return liquid_thermal_diffusivity * time / initial_bubble_diameter**2


def dimensionless_bubble_diameter_florschuetz_chao_1965(bubble_jakob, bubble_fourier):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`florschuetzMechanicsVaporBubble1965,tangReviewDirectContact2022`."""
    return 1 - 4 * bubble_jakob * sqrt(bubble_fourier / pi)


def dimensionless_bubble_diameter_isenberg_sideman_1970(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - (3 / sqrt(pi))
        * bubble_initial_reynolds ** (1 / 2)
        * liquid_prandtl ** (1 / 3)
        * bubble_jakob
        * bubble_fourier
    ) ** (2 / 3)


def dimensionless_bubble_diameter_akiyama_1973(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 1.036
        * bubble_initial_reynolds ** (1 / 2)
        * liquid_prandtl ** (1 / 3)
        * bubble_jakob
        * bubble_fourier
    ) ** 0.714


def dimensionless_bubble_diameter_chen_mayinger_1992(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 0.56
        * bubble_initial_reynolds**0.7
        * liquid_prandtl**0.5
        * bubble_jakob
        * bubble_fourier
    ) ** 0.9


def dimensionless_bubble_diameter_kalman_mori_2002(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 0.0094
        * bubble_initial_reynolds**0.855
        * liquid_prandtl**0.855
        * bubble_jakob
        * bubble_fourier
    ) ** 0.873


def dimensionless_bubble_diameter_lucic_mayinger_2010(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    # assert 1_000 < bubble_initial_reynolds < 30_000
    # assert 45 < bubble_jakob < 80
    # assert 2.1 < liquid_prandtl < 4.3
    return (
        1
        - 2.92
        * bubble_initial_reynolds**0.61
        * liquid_prandtl**0.33
        * bubble_jakob**0.69
        * bubble_fourier
    )


def dimensionless_bubble_diameter_kim_park_2011(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 0.67
        * bubble_initial_reynolds**0.7
        * liquid_prandtl ** (-0.4564)
        * bubble_jakob**0.7959
        * bubble_fourier
    ) ** 0.769


def dimensionless_bubble_diameter_al_issa_et_al_2014(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 0.135
        * bubble_initial_reynolds**0.89
        * liquid_prandtl**0.33
        * bubble_jakob
        * bubble_fourier
    ) ** 0.901


def dimensionless_bubble_diameter_tang_et_al_2016(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 12.29
        * bubble_initial_reynolds**0.584
        * liquid_prandtl**0.333
        * bubble_jakob**0.581
        * bubble_fourier
    ) ** 0.706


def dimensionless_bubble_diameter_yuan_et_al_2009(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
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


def dimensionless_bubble_diameter_inaba_et_al_2013(
    bubble_initial_reynolds, liquid_prandtl, bubble_jakob, bubble_fourier
):
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
