from pathlib import Path
from typing import Callable, Any
from enum import Enum

from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.gsi.dna import GsiOnlineDNA
from geocompy.gsi.gsitypes import GsiOnlineResponse

from ..utils import echo_red, echo_green
from .io import write_settings, SettingsDict, SubsystemSettingsDict


def download_settings_geocom(
    tps: GeoCom,
    add_defaults: bool = False
) -> SettingsDict:
    data: SettingsDict = {
        "protocol": "geocom",
        "settings": []
    }

    return data


def download_settings_gsidna(
    dna: GsiOnlineDNA,
    add_defaults: bool = False
) -> SettingsDict:
    settings: SubsystemSettingsDict = {
        "subsystem": "settings",
        "options": {}
    }

    options = {
        "beep": "MEDIUM",
        "contrast": 50,
        "distance_unit": "METER",
        "temperature_unit": "CELSIUS",
        "decimals": 5,
        "baud": "B9600",
        "parity": "NONE",
        "terminator": "CRLF",
        "protocol": True,
        "recorder": "INTERNAL",
        "delay": 0,
        "autooff": "SLEEP",
        "display_heater": False,
        "curvature_correction": True,
        "staff_mode": False,
        "format": "GSI8",
        "code_recording": "BEFORE"
    }

    for option, default in options.items():
        name = f"get_{option}"
        method: Callable[
            [],
            GsiOnlineResponse[Any]
        ] | None = getattr(dna.settings, name, None)
        if method is None:
            settings["options"][option] = default if add_defaults else None
            continue

        response = method()
        value = response.value
        if value is None:
            settings["options"][option] = default if add_defaults else None
            continue

        if isinstance(value, Enum):
            value = value.name

        settings["options"][option] = value

    return {
        "protocol": "gsidna",
        "settings": [settings]
    }


def clean_settings(
    settings: SettingsDict
) -> SettingsDict:
    for subsystem in settings["settings"]:
        subsystem["options"] = {
            k: v for k, v in subsystem["options"].items() if v is not None
        }

    return settings


def main(
    port: str,
    protocol: str,
    file: Path,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    format: str = "auto",
    add_defaults: bool = False,
    save_all: bool = False
) -> None:
    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout
    ) as com:
        match protocol:
            case "geocom":
                tps = GeoCom(com)
                data = download_settings_geocom(tps, add_defaults)
            case "gsidna":
                dna = GsiOnlineDNA(com)
                data = download_settings_gsidna(dna, add_defaults)
            case _:
                echo_red(f"Unknown protocol: '{protocol}'")
                exit(1)

    if not save_all:
        data = clean_settings(data)

    write_settings(data, file, format)
    echo_green(f"Settings saved at {file}")
