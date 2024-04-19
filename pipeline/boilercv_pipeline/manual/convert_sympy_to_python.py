"""Convert SymPy equations to Python functions."""

from loguru import logger
from sympy import parse_expr, symbols
from sympy.utilities.lambdify import lambdastr
from tomlkit import dumps, parse
from tqdm import tqdm

from boilercv_pipeline.manual import EQUATIONS, SYMPY, TABLE

PYTHON = "python"
"""Key for Python functions in the equations TOML file."""
ARGS = {
    "Fo_{o}": "bubble_fourier",
    "Re_{bo}": "bubble_initial_reynolds",
    "Ja": "bubble_jakob",
    "Pr": "liquid_prandtl",
}
"""Potential argument set for lambda functions."""
SUBS = {**ARGS, "beta": "dimensionless_bubble_diameter", "pi": "pi"}
"""Substitutions from SymPy symbolic variables to descriptive names."""
syms = tuple(SUBS.values())
local_dict = dict(zip(syms, symbols(syms), strict=True))


def main():  # noqa: D103
    toml = parse(EQUATIONS.read_text("utf-8"))
    equations = toml[TABLE]
    for i, expression in enumerate(tqdm(equations)):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        eq = expression.get(SYMPY).replace("\n", "")
        if not eq or expression.get(PYTHON):
            continue
        for symbol, sub in SUBS.items():
            eq = eq.replace(symbol, sub)
        eq = parse_expr(eq, local_dict=local_dict, evaluate=False)
        toml[TABLE][i][PYTHON] = (  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
            lambdastr(
                expr=eq.rhs,
                args=[s for s in eq.rhs.free_symbols if s.name in ARGS.values()],
            )
            .split(":")[-1]
            .strip()
            .removeprefix("(")
            .removesuffix(")")
        )
    EQUATIONS.write_text(encoding="utf-8", data=dumps(toml))


if __name__ == "__main__":
    logger.info("Start converting SymPy expressions to Python functions")
    main()
    logger.info("Finish converting SymPy expressions to Python functions")
