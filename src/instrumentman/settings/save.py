from pathlib import Path
from typing import Callable, Any
from enum import Enum
from logging import Logger, getLogger

from geocompy.data import Angle
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComResponse, GeoComSubsystem, GeoComCode
from geocompy.gsi.dna import GsiOnlineDNA
from geocompy.gsi.gsitypes import GsiOnlineResponse

from ..utils import echo_green
from .io import write_settings, SettingsDict, SubsystemSettingsDict


def download_settings_geocom(
    tps: GeoCom,
    logger: Logger,
    defaults: bool = False
) -> SettingsDict:
    options: list[SubsystemSettingsDict] = [
        {
            "subsystem": "aut",
            "options": {
                "atr": True,
                "lock": False,
                "tolerance": [1, 1],
                "timeout": [15, 15],
                "fine_adjust_mode": "NORMAL",
                "search_area": [0, 0, 0.1, 0.1, True],
                "spiral": [0.1, 0.1],
                "lock_onthefly": True
            }
        },
        {
            "subsystem": "bap",
            "options": {
                "target_type": "REFLECTOR",
                "prism_type": "MINI",
                "measurement_program": "SINGLE_REF_STANDARD",
                "atr_setting": "NORMAL",
                "reduced_atr_fov": False,
                "precise_atr": True
            }
        },
        {
            "subsystem": "csv",
            "options": {
                "laserplummet": True,
                "laserplummet_intensity": 100,
                "charging": False,
                "preferred_powersource": "INTERNAL"
            }
        },
        {
            "subsystem": "dna",
            "options": {
                "staffmode": False,
                "curvature_correction": False,
                "staff_type": "GPCL2"
            }
        },
        {
            "subsystem": "edm",
            "options": {
                "laserpointer": False,
                "edm": True,
                "boomerang_filter": True,
                "tracklight_brightness": "MID",
                "tracklight": False,
                "guidelight_intensity": "OFF",
                "boomerang_filter_new": True
            }
        },
        {
            "subsystem": "img",
            "options": {
                "telescopic_configuration": [0, 50, 6, "INTERNAL"],
                "telescopic_exposure_time": 20
            }
        },
        {
            "subsystem": "kdm",
            "options": {
                "display_power": False
            }
        },
        {
            "subsystem": "sup",
            "options": {
                "poweroff_configuration": [False, "SLEEP", 600000],
                "low_temperature_control": False,
                "autorestart": True
            }
        },
        {
            "subsystem": "tmc",
            "options": {
                "compensator": True,
                "edm_mode_v1": "SINGLE_STANDARD",
                "edm_mode_v2": "SINGLE_STANDARD",
                "angle_correction": [True, True, True, True]
            }
        }
    ]
    output_options: list[SubsystemSettingsDict] = []
    for group in options:
        settings: SubsystemSettingsDict = {
            "subsystem": group["subsystem"],
            "options": {}
        }

        subsystem: GeoComSubsystem = getattr(
            tps,
            group["subsystem"]
        )

        for option, default in group["options"].items():
            if isinstance(default, bool):
                name = f"get_{option}_status"
            else:
                name = f"get_{option}"

            method: Callable[
                [],
                GeoComResponse[Any]
            ] | None = getattr(subsystem, name, None)
            if method is None:
                if defaults:
                    settings["options"][option] = default
                else:
                    settings["options"][option] = None
                continue

            response = method()
            value = response.params
            if response.error != GeoComCode.OK or value is None:
                if defaults:
                    logger.debug(
                        f"Could not get value of {option}, "
                        "falling back to default"
                    )
                    settings["options"][option] = default
                else:
                    logger.debug(f"Could not get value of {option}")
                    settings["options"][option] = None

                continue

            if isinstance(value, tuple):
                raw = value
                value = []
                for v in raw:
                    if isinstance(v, Enum):
                        value.append(v.name)
                    elif isinstance(v, Angle):
                        value.append(float(v))
                    else:
                        value.append(v)
            elif isinstance(value, Enum):
                value = value.name

            settings["options"][option] = value

        output_options.append(settings)

    return {
        "protocol": "geocom",
        "settings": output_options
    }


def download_settings_gsidna(
    dna: GsiOnlineDNA,
    logger: Logger,
    defaults: bool = False
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
        "curvature_correction": False,
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
            if defaults:
                settings["options"][option] = default
            else:
                settings["options"][option] = None

            continue

        response = method()
        value = response.value
        if value is None:
            if defaults:
                logger.debug(
                    f"Could not get value of {option}, "
                    "falling back to default"
                )
                settings["options"][option] = default
            else:
                logger.debug(f"Could not get value of {option}")
                settings["options"][option] = None

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

    settings["settings"] = [
        s
        for s in settings["settings"]
        if len(s["options"]) > 0
    ]

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
    defaults: bool = False
) -> None:
    logger = getLogger("iman.settings.save")
    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        match protocol:
            case "geocom":
                tps = GeoCom(com, logger.getChild("instrument"))
                data = download_settings_geocom(tps, logger, defaults)
            case "gsidna":
                dna = GsiOnlineDNA(com, logger.getChild("instrument"))
                data = download_settings_gsidna(dna, logger, defaults)

    data = clean_settings(data)
    logger.info("Removed empty options")

    write_settings(data, file, format)
    echo_green(f"Saved settings to {file}")
    logger.info(f"Saved settings to {file}")
