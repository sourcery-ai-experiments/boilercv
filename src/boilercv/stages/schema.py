"""Generate schema for the project."""

import re

from boilercv.models.common import write_schema
from boilercv.models.params import Params


def main(params: Params):
    models = [Params]
    for model in models:
        write_schema(
            params.paths.project_schema
            / f"{to_snake_case(model.__name__)}_schema.json",
            model,
        )


# https://github.com/samuelcolvin/pydantic/blob/4f4e22ef47ab04b289976bb4ba4904e3c701e72d/pydantic/utils.py#L127-L131
def to_snake_case(v: str) -> str:
    v = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", v)
    v = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", v)

    return v.replace("-", "_").lower()


if __name__ == "__main__":
    main(Params.get_params())
