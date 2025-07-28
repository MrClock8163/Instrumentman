from pathlib import Path
import json
import os

from jsonschema import validate, ValidationError
from click_extra import echo

from ..utils import echo_green, echo_red
from .io import read_settings, SettingsDict


def validate_settings(
    settings: SettingsDict,
    print_error: bool = False
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
            if print_error:
                echo(e.message)
            return False

    return True


def main(
    file: Path,
    format: str = "auto"
) -> None:
    settings = read_settings(file, format)
    is_valid = validate_settings(settings, print_error=True)
    if not is_valid:
        echo_red("Settings file is not valid")
        return

    echo_green("Settings file is valid")
