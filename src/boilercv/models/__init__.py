from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, Extra, MissingError, ValidationError

PARAMS_FILE = Path("params.yaml")

BaseModel_T = TypeVar("BaseModel_T", bound=BaseModel)


class MyBaseModel(BaseModel):
    """Base model and configuration for all models used in this project."""

    class Config:
        """Model configuration. Allow arbitrary types. Enables Numpy types in fields."""

        # Don't specify as class kwargs for easier overriding, and "extra" acted weird.
        extra = Extra.forbid  # To forbid extra fields


# Can't type annotate `model` for some reason
def load_config(path: Path, model: type[BaseModel_T]) -> BaseModel_T:
    """Load a YAML file into a Pydantic model.

    Given a path to a YAML file, automatically unpack its fields into the provided
    Pydantic model.

    Args:
        path: The path to a YAML file.
        model: The model class to pass the contents of the YAML file.

    Returns:
        An instance of the model after validation.

    Raises:
        ValueError: If an improper path is passed.
        ValidationError: If a field is undefined in the configuration file.
    """
    if path.suffix != ".yaml":
        raise ValueError(f"The path '{path}' does not refer to a YAML file.")
    raw_config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not raw_config:
        raise ValueError("The configuration file is empty.")
    try:
        config = model(**{key: raw_config.get(key) for key in raw_config})
    except ValidationError as exception:
        addendum = "\n  The field may be undefined in the configuration file."
        for error in exception.errors():
            if error["msg"] == MissingError.msg_template:
                error["msg"] += addendum
        raise
    return config


def dump_model(path: Path, model: BaseModel):
    """Dump a Pydantic model to a YAML file.

    Given a path to a YAML file, write a Pydantic model to the file. Optionally add a
    schema directive at the top of the file. Create the file if it doesn't exist.

    Args:
        path: The path to a YAML file. Will create it if it doesn't exist.
        model: An instance of the Pydantic model to dump.
    """
    path = Path(path)
    # ensure one \n and no leading \n, Pydantic sometimes does more
    path.write_text(
        encoding="utf-8",
        data=yaml.safe_dump(model.dict(exclude_none=True), sort_keys=False),
    )


def write_schema(path: Path, model: type[BaseModel]):
    """Write a Pydantic model schema to a JSON file.

    Given a path to a JSON file, write a Pydantic model schema to the file. Create the
    file if it doesn't exist.

    Args:
        path: The path to a JSON file. Will create it if it doesn't exist.
        model: The Pydantic model class to get the schema from.
    """
    if path.suffix != ".json":
        raise ValueError(f"The path '{path}' does not refer to a JSON file.")
    path.write_text(model.schema_json(indent=2) + "\n", encoding="utf-8")
