from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Extra, MissingError, ValidationError

PARAMS_FILE = Path("params.yaml")


class MyBaseModel(BaseModel):
    """Base model for all Pydantic models used in this project."""

    class Config:
        """Model configuration.

        Accessing enums yields their values, and allowing arbitrary types enables
        using Numpy types in fields.
        """

        # Don't specify as class kwargs for easier overriding, and "extra" acted weird.
        extra = Extra.forbid  # To forbid extra fields


# * -------------------------------------------------------------------------------- * #
# * COMMON


# Can't type annotate `model` for some reason
def load_config(path: Path, model):
    """Load a YAML file into a Pydantic model.

    Given a path to a YAML file, automatically unpack its fields into the provided
    Pydantic model.

    Parameters
    ----------
    path: Path
        The path to a YAML file.
    model: type[pydantic.BaseModel]
        The Pydantic model class to which the contents of the YAML file will be passed.

    Returns
    -------
    pydantic.BaseModel
        An instance of the Pydantic model after validation.

    Raises
    ------
    ValueError
        If the path does not refer to a YAML file, or the YAML file is empty.
    ValidationError
        If the configuration file is missing a required field.
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


# Can't type annotate `model` for some reason
def dump_model(path: Path, model):
    """Dump a Pydantic model to a YAML file.

    Given a path to a YAML file, write a Pydantic model to the file. Optionally add a
    schema directive at the top of the file. Create the file if it doesn't exist.

    Parameters
    ----------
    path: Path
        The path to a YAML file. Will create it if it doesn't exist.
    model: type[pydantic.BaseModel]
        An instance of the Pydantic model to dump.
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

    Parameters
    ----------
    path: Path
        The path to a JSON file. Will create it if it doesn't exist.
    model: type[pydantic.BaseModel]
        The Pydantic model class to get the schema from.
    """
    if path.suffix != ".json":
        raise ValueError(f"The path '{path}' does not refer to a JSON file.")
    path.write_text(model.schema_json(indent=2) + "\n", encoding="utf-8")
