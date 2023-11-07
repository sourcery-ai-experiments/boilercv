"""Subcooled bubble collapse experiment."""

from collections.abc import Iterable
from datetime import datetime

from boilercore.paths import ISOLIKE, dt_fromisolike, get_module_name

from boilercv.models.params import PARAMS

EXP = get_module_name(__spec__ or __file__)
"""Name of this experiment."""
DAY = "2023-09-20"
"""Day of the experiment"""
ALL_THERMAL_DATA = PARAMS.paths.experiments / EXP / f"{DAY}_all_thermal_data.csv"
"""All thermal data for this experiment."""
THERMAL_DATA = PARAMS.paths.experiments / EXP / f"{DAY}_thermal.h5"
"""Reduced thermal data for this experiment."""


def get_times(strings: Iterable[str]) -> Iterable[datetime]:
    for string in strings:
        if match := ISOLIKE.search(string):
            yield dt_fromisolike(match)
