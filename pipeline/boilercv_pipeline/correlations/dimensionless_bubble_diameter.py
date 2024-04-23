"""Dimensionless bubble diameter correlations."""

from numpy import pi, sqrt


def flourschuetz_chao_1965(bubble_fourier, bubble_jakob):
    """Florschuetz and Chao (1965) dimensionless bubble diameter {cite}`florschuetzMechanicsVaporBubble1965,tangReviewDirectContact2022`.

    Parameters
    ----------
    bubble_fourier
        Bubble Fourier number.
    bubble_jakob
        Bubble Jakob number.
    """
    return 1 - 4 * bubble_jakob * sqrt(bubble_fourier / pi)
