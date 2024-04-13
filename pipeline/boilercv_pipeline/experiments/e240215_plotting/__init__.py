"""Palettes."""

from colorcet import colormaps  # pyright: ignore[reportAttributeAccessIssue] 1.1.356
from seaborn import color_palette

WARM_INDICES = [1, 3, 6, 16, 19, 31, 33, 37, 42, 46, 49, 69]
"""Indices of the palette that are warm."""
COOL_INDICES = [0, 2, 9, 11, 12, 14, 23, 24, 25, 35, 41, 50]
"""Indices of the not-warm palette that are cool."""

warm = colormaps["cet_glasbey_warm"]
cool = colormaps["cet_glasbey_cool"]
cat10 = colormaps["cet_glasbey_category10"]
warm12 = color_palette([c for i, c in enumerate(cat10.colors) if i in WARM_INDICES])
cool12 = color_palette([c for i, c in enumerate(cat10.colors) if i in COOL_INDICES])
