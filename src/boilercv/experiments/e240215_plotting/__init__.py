from colorcet import colormaps
from seaborn import color_palette

WARM_INDICES = {1, 3, 6, 16, 19, 31, 33, 37, 42, 46, 49, 69}
"""Indices of the palette that are warm."""
COOL_INDICES = {0, 1, 6, 8, 9, 11, 18, 19, 20, 28, 33, 39}
"""Indices of the not-warm palette that are cool."""
cat10 = colormaps["cet_glasbey_category10"]
warm12 = color_palette([
    c
    for i, c in enumerate(cat10.colors)  # pyright: ignore[reportAttributeAccessIssue]  # pyright: 1.1.348, seaborn: 0.13.1
    if i in WARM_INDICES
])
cool = colormaps["cet_glasbey_cool"]
warm = colormaps["cet_glasbey_warm"]
not_warm = [
    c
    for i, c in enumerate(cat10.colors)  # pyright: ignore[reportAttributeAccessIssue]  # pyright: 1.1.348, seaborn: 0.13.1
    if i not in WARM_INDICES
]
cool12 = color_palette([c for i, c in enumerate(not_warm) if i in COOL_INDICES])
