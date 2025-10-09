from __future__ import annotations

from pathlib import Path
from typing import Any
from collections.abc import Callable
from logging import Logger, getLogger

from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComSubsystem, GeoComResponse, GeoComCode
from geocompy.gsi.dna import GsiOnlineDNA
from geocompy.gsi.gsitypes import GsiOnlineResponse
from geocompy.gsi.dna.settings import GsiOnlineDNASettings

from ..utils import print_error, print_warning, print_success
from .io import read_settings, SettingsDict
from .validate import validate_settings


def set_setting_geocom(
    logger: Logger,
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
        print_warning(f"Could not find '{name}' to set '{setting}'")
        logger.error(f"Could not find '{name}' to set '{setting}'")
        return

    if isinstance(value, list):
        response = method(*value)
    else:
        response = method(value)

    if response.error != GeoComCode.OK:
        print_warning(f"Could not set '{setting}'")
        logger.error(f"Could not set '{setting}' ({response})")
        return


def set_setting_gsidna(
    logger: Logger,
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
        print_warning(f"Could not find '{name}' to set '{setting}'")
        logger.error(f"Could not find '{name}' to set '{setting}'")
        return

    response = method(value)

    if response.value is None or not response.value:
        print_warning(f"Could not set '{setting}'")
        logger.error(f"Could not set '{setting}' ({response.response})")
        return


def upload_settings_geocom(
    protocol: GeoCom,
    logger: Logger,
    settings: SettingsDict
) -> None:
    logger.info("Starting GeoCOM settings upload")
    for item in settings["settings"]:
        sysname = item["subsystem"]
        subsystem: Any = getattr(protocol, sysname)
        if subsystem is None:
            print_error(f"Could not find '{sysname}' subsystem")
            logger.critical(f"Could not find '{sysname}' subsystem")
            exit(1)

        for option, value in item["options"].items():
            if value is None:
                logger.debug(f"Skipping {option}")
                continue

            set_setting_geocom(logger, subsystem, option, value)

    logger.info("Settings uploaded")


def upload_settings_gsidna(
    protocol: GsiOnlineDNA,
    logger: Logger,
    settings: SettingsDict
) -> None:
    logger.info("Starting GSI Online DNA settings upload")
    for item in settings["settings"]:
        sysname = item["subsystem"]
        subsystem: Any = getattr(protocol, sysname)
        if subsystem is None:
            print_error(f"Could not find '{sysname}' subsystem")
            logger.critical(f"Could not find '{sysname}' subsystem")
            exit(1)

        for option, value in item["options"].items():
            if value is None:
                logger.debug(f"Skipping {option}")
                continue

            set_setting_gsidna(logger, subsystem, option, value)

    logger.info("Settings uploaded")


def main(
    port: str,
    settings: Path,
    baud: int = 9600,
    timeout: int = 15,
    attempts: int = 1,
    sync_after_timeout: bool = False,
    format: str = "auto"
) -> None:
    logger = getLogger("iman.settings.load")
    data = read_settings(settings, format)
    if not validate_settings(data):
        print_error("Settings file does not follow schema")
        logger.critical("Settings file does not follow schema")
        exit(1)

    with open_serial(
        port,
        attempts=attempts,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        match data["protocol"]:
            case "geocom":
                tps = GeoCom(
                    com,
                    logger=logger.getChild("instrument")
                )
                upload_settings_geocom(tps, logger, data)
            case "gsidna":
                dna = GsiOnlineDNA(
                    com,
                    logger=logger.getChild("instrument")
                )
                upload_settings_gsidna(dna, logger, data)

    print_success(f"Settings loaded from {settings}")
