from pathlib import Path
import json
import os

from jsonschema import validate, ValidationError

from ..utils import print_success, print_error
from .io import read_settings, SettingsDict


def validate_settings(
    settings: SettingsDict,
    print_error_message: bool = False
) -> bool:
    with open(
        os.path.join(
            os.path.dirname(__file__),
            "schema_settings.json"
        ),
        "rt",
        encoding="utf8"
    ) as schema:
        try:
            validate(settings, json.load(schema))
        except ValidationError as e:
            if print_error_message:
                print_error(e.message)
            return False

    return True


def main(
    file: Path,
    format: str = "auto"
) -> None:
    settings = read_settings(file, format)
    is_valid = validate_settings(settings, print_error_message=True)
    if not is_valid:
        print_error("Settings file is not valid")
        return

    print_success("Settings file is valid")
