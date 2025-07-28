from typing import Any, cast
from pathlib import Path

import json
import yaml
import toml

from ..utils import echo_red


_SettingsDict = dict[str, Any]


def read_settings(
    file: Path,
    format: str = "auto"
) -> _SettingsDict:
    if format == "auto":
        format = file.suffix[1:].lower() if file.suffix else ""

    match format:
        case "json":
            with file.open("rt", encoding="utf8") as settings:
                data = cast(_SettingsDict, json.load(settings))
        case "yaml" | "yml":
            with file.open("rt", encoding="utf8") as settings:
                data = cast(_SettingsDict, yaml.load(settings, yaml.Loader))
        case "toml":
            # The TOML package doesn't support heterogenous arrays, even tho it
            # was added to the language spec in 2019. Therefore the standard
            # lib tomllib/tomli has to be used for parsing.
            import tomllib as toml
            with file.open("rb") as settings:
                data = cast(_SettingsDict, toml.load(settings))
        case _:
            echo_red(f"Unknown file format: {format}")
            exit(1)

    return data


def write_settings(
    data: _SettingsDict,
    file: Path,
    format: str = "auto"
) -> None:
    if format == "auto":
        format = file.suffix[1:].lower() if file.suffix else ""

    with file.open("wt", encoding="utf8") as settings:
        match format:
            case "json":
                json.dump(data, settings)
            case "yaml" | "yml":
                yaml.dump(data, settings, yaml.Dumper)
            case "toml":
                toml.dump(data, settings)
            case _:
                echo_red(f"Unknown file format: {format}")
                exit(1)
