"""Experimental stages, not yet integrated into the full pipeline."""

from pathlib import Path

EXPERIMENTS = Path("docs/experiments")


def get_exp(exp: str) -> Path:
    """Get the experiment name."""
    return EXPERIMENTS / exp
