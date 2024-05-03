"""Theoretical correlations for bubble lifetimes."""

from pathlib import Path

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.generated import (
    equations,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.params import args

PNGS = Path("data/dimensionless_bubble_diameter_equation_pngs")
"""Equation PNGs."""


ARGS = {arg.forms.sympy: arg.name for arg in args}
"""Get potential argument set for lambda functions."""

SUBS = {**ARGS, "beta": "dimensionless_bubble_diameter", "pi": "pi"}
"""Substitutions from SymPy symbolic variables to descriptive names."""
KWDS = {arg.name: arg.test for arg in args}
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
    "al_issa_et_al_2014": [1.000000, 0.995927, 0.991852, 0.987776, 0.983698, 0.979618, 0.975536, 0.971452, 0.967366, 0.963278],
    "chen_mayinger_1992": [1.000000, 0.992963, 0.985922, 0.978875, 0.971822, 0.964763, 0.957699, 0.950629, 0.943553, 0.936471],
    "inaba_et_al_2013": [1.000000, 0.967928, 0.935856, 0.903785, 0.871713, 0.839642, 0.807570, 0.775499, 0.743427, 0.711355],
    "kalman_mori_2002": [1.000000, 0.999766, 0.999532, 0.999298, 0.999064, 0.998830, 0.998596, 0.998363, 0.998129, 0.997895],
    "kim_park_2011": [1.000000, 0.992802, 0.985588, 0.978359, 0.971113, 0.963852, 0.956573, 0.949278, 0.941967, 0.934638],
    "lucic_mayinger_2010": [1.000000, 0.973077, 0.946155, 0.919233, 0.892311, 0.865389, 0.838466, 0.811544, 0.784622, 0.757700],
    "tang_et_al_2016": [1.000000, 0.927931, 0.853449, 0.776152, 0.695500, 0.610738, 0.520744, 0.423701, 0.316230, 0.190161],
} | {eq.name: eq.expect for eq in equations.values()}
# fmt: on
