"""Generate SymPy equations."""

from cyclopts import App
from loguru import logger
from sympy import sympify
from sympy.solvers import solve
from tqdm import tqdm

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.equations import (
    EQUATIONS,
    LOCALS,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.morphs import Solns

APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(_overwrite: bool = False):  # noqa: D103
    for name, eq in tqdm(
        (
            (name, sympify(eq.get("sympy"), locals=LOCALS, evaluate=False))
            for name, eq in EQUATIONS.items()
        )
    ):
        _solns = Solns({param: solve(eq, sym) for param, sym in LOCALS.items()})
        f"""
        def {name}():
        """


if __name__ == "__main__":
    logger.info("Start generating symbolic equations.")
    main()
    logger.info("Finish generating symbolic equations.")
