"""Subcooled bubble collapse experiment."""

from collections.abc import Iterable
from datetime import datetime

from boilercore.paths import ISOLIKE, dt_fromisolike, get_module_name

EXP = get_module_name(__spec__ or __file__)
"""Name of this experiment."""


def get_times(strings: Iterable[str]) -> Iterable[datetime]:
    for string in strings:
        if match := ISOLIKE.search(string):
            yield dt_fromisolike(match)
