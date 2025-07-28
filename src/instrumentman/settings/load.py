from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComSubsystem, GeoComResponse, GeoComCode
from geocompy.gsi.dna import GsiOnlineDNA
from geocompy.gsi.gsitypes import GsiOnlineResponse
from geocompy.gsi.dna.settings import GsiOnlineDNASettings

from ..utils import echo_red, echo_yellow, echo_green
from .io import read_settings, SettingsDict
from .validate import validate_settings


def set_setting_geocom(
    system: GeoComSubsystem,
    setting: str,
    value: int | float | bool | str | list[int | float | bool | str]
) -> None:
    if isinstance(value, bool):
        name = f"switch_{setting}"
    else:
        name = f"set_{setting}"

    method: Callable[
        ...,
        GeoComResponse[Any]
    ] | None = getattr(system, name, None)
    if method is None:
        echo_yellow(f"Could not find '{name}' to set '{setting}'")
        return

    if isinstance(value, list):
        response = method(*value)
    else:
        response = method(value)

    if response.error != GeoComCode.OK:
        echo_yellow(f"Could not set '{setting}' ({response.error.name})")
        return


def set_setting_gsidna(
    system: GsiOnlineDNASettings,
    setting: str,
    value: int | float | bool | str
) -> None:
    name = f"set_{setting}"
    method: Callable[
        ...,
        GsiOnlineResponse[bool]
    ] | None = getattr(system, name, None)
    if method is None:
        echo_yellow(f"Could not find '{name}' to set '{setting}'")
        return

    response = method(value)

    if response.value is None or not response.value:
        echo_yellow(f"Could not set '{setting}' ({response.response})")
        return


def upload_settings_geocom(
    protocol: GeoCom,
    settings: SettingsDict
) -> None:
    for item in settings["settings"]:
        sysname = item["subsystem"]
        subsystem: Any = getattr(protocol, sysname)
        if subsystem is None:
            echo_red(f"Could not find '{sysname}' subsystem")
            exit(1)

        for option, value in item["options"].items():
            if value is None:
                continue

            set_setting_geocom(subsystem, option, value)


def upload_settings_gsidna(
    protocol: GsiOnlineDNA,
    settings: SettingsDict
) -> None:
    for item in settings["settings"]:
        sysname = item["subsystem"]
        subsystem: Any = getattr(protocol, sysname)
        if subsystem is None:
            echo_red(f"Could not find '{sysname}' subsystem")
            exit(1)

        for option, value in item["options"].items():
            if value is None:
                continue

            set_setting_gsidna(subsystem, option, value)


def main(
    port: str,
    settings: Path,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    format: str = "auto"
) -> None:
    data = read_settings(settings, format)
    if not validate_settings(data):
        echo_red("Settings file does not follow schema")
        exit(1)

    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout
    ) as com:
        match data["protocol"]:
            case "geocom":
                tps = GeoCom(com)
                upload_settings_geocom(tps, data)
            case "gsidna":
                dna = GsiOnlineDNA(com)
                upload_settings_gsidna(dna, data)
            case _:
                echo_red(f"Unknown protocol: {data["protocol"]}")
                exit(1)

        echo_green(f"Settings loaded from {settings}")
