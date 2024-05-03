"""Convert a LaTeX expression to a Python lambda function.

Use `pipx` to isolate this script's dependencies from the rest of the project:

    ```Shell
    pipx run scripts/parse_latex.py
    ```

Use of `sympy.parsing.latex.parse_latex` requires `antlr4-python3-runtime==4.11`, but
`dvc>=3.33.3` requires `hydra-core` and `omegaconf` which have incompatible dependency
specifications for `antlr4-python3-runtime`. This issue is resolved if installing
`hydra-core` from `https://github.com/facebookresearch/hydra/tree/2e682d8` and
`omegaconf==2.4.0.dev2`, but the local build fails. Use `pipx` for now to isolate this
dependency conflict.

See Also
--------
- <https://github.com/facebookresearch/hydra>
- <https://github.com/facebookresearch/hydra/issues/2699>
- <https://github.com/facebookresearch/hydra/pull/2733>
- <https://github.com/facebookresearch/hydra/pull/2881>
"""

# /// script
# requires-python = "==3.11"
# dependencies = [
#     "antlr4-python3-runtime==4.11",
#     "cyclopts==2.6.1",
#     "sympy==1.12",
# ]
# ///

from cyclopts import App
from sympy.parsing.latex import parse_latex

APP = App(help_format="markdown")
"""CLI."""


def main():
    """Invoke the CLI."""
    APP()


@APP.default
def parse(latex: str):
    """Parse LaTeX."""
    print(parse_latex(latex))  # noqa: T201


if __name__ == "__main__":
    main()
