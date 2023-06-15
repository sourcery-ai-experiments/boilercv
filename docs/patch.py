from os import chdir
from pathlib import Path


def patch():
    """Patch the project if we're running notebooks in the documentation directory."""
    if Path().resolve().name == "docs":
        chdir("..")
