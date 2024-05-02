"""Symbolic dimensionless bubble diameter correlations for bubble collapse."""

from numpy import pi, sqrt


def florschuetz_chao_1965(bubble_fourier, bubble_jakob):
    """Florschuetz and Chao (1965) dimensionless bubble diameter {cite}`florschuetzMechanicsVaporBubble1965,tangReviewDirectContact2022`.

    Parameters
    ----------
    bubble_fourier
        Bubble Fourier number.
    bubble_jakob
        Bubble Jakob number.
    """
    return 1 - 4 * bubble_jakob * sqrt(bubble_fourier / pi)


def isenberg_sideman_1970(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
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


def akiyama_1973(bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 1.036
        * bubble_fourier
        * bubble_initial_reynolds ** (1 / 2)
        * bubble_jakob
        * liquid_prandtl ** (1 / 3)
    ) ** 0.714


def chen_mayinger_1992(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
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


def kalman_mori_2002(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
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


def lucic_mayinger_2010(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 2.92
        * bubble_initial_reynolds**0.61
        * liquid_prandtl**0.33
        * bubble_jakob**0.69
        * bubble_fourier
    )


def kim_park_2011(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
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


def al_issa_et_al_2014(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
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


def tang_et_al_2016(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
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


def yuan_et_al_2009(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
):
    """Bubble history correlation for condensation of a stagnant bubble {cite}`yuandewenCondensationHeatTransfer2009,tangReviewDirectContact2022`."""
    return (
        1
        - 1.8
        * bubble_initial_reynolds**0.5
        * liquid_prandtl ** (1 / 3)
        * bubble_jakob
        * bubble_fourier
        * (1 - 0.5 * bubble_jakob**0.1 * bubble_fourier)
    ) ** (2 / 3)


def inaba_et_al_2013(
    bubble_fourier, bubble_initial_reynolds, liquid_prandtl, bubble_jakob
):
    """Bubble history correlation for condensation of a stagnant bubble. {cite}`tangReviewDirectContact2022`."""
    return (
        1
        - 1.1
        * bubble_initial_reynolds**0.86
        * liquid_prandtl ** (2 / 3)
        * bubble_jakob**0.2
        * bubble_fourier
    )
