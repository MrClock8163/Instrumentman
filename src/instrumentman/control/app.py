from logging import getLogger

from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode

from ..utils import print_error


def main_shutdown_geocom(
    component: str,
    port: str,
    timeout: int = 15,
    retry: int = 1,
    baud: int = 9600,
    sync_after_timeout: bool = False
) -> None:
    logger = getLogger("iman.files.list")
    with open_serial(
        port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        logger=logger.getChild("com")
    ) as com:
        instrument = GeoCom(com, logger.getChild("instrument"))

        match component:
            case "protocol":
                resp = instrument.com.switch_to_local()
            case "edm":
                resp = instrument.edm.switch_edm(False)
            case "pointer":
                resp = instrument.edm.switch_laserpointer(False)
            case "telescopic-camera":
                resp = instrument.cam.switch_camera_power(False, "TELESCOPIC")
            case "overview-camera":
                resp = instrument.cam.switch_camera_power(False, "OVERVIEW")
            case "instrument":
                resp = instrument.com.switch_off()
            case _:
                raise ValueError(
                    f"Unknown component '{component}'"
                )

        if resp.error != GeoComCode.OK:
            print_error(
                f"Could not deactivate '{component}' ({resp.error.name})"
            )
            exit(1)


def main_startup_geocom(
    component: str,
    port: str,
    timeout: int = 15,
    retry: int = 1,
    baud: int = 9600,
    sync_after_timeout: bool = False
) -> None:
    logger = getLogger("iman.files.list")
    with open_serial(
        port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        logger=logger.getChild("com")
    ) as com:
        instrument = GeoCom(com, logger.getChild("instrument"))

        match component:
            case "instrument":
                resp = instrument.com.switch_on()
            case "edm":
                resp = instrument.edm.switch_edm(True)
            case "pointer":
                resp = instrument.edm.switch_laserpointer(True)
            case "telescopic-camera":
                resp = instrument.cam.switch_camera_power(True, "TELESCOPIC")
            case "overview-camera":
                resp = instrument.cam.switch_camera_power(True, "OVERVIEW")
            case _:
                raise ValueError(
                    f"Unknown component '{component}'"
                )

        if resp.error != GeoComCode.OK:
            print_error(
                f"Could not activate '{component}'  ({resp.error.name})"
            )
            exit(1)
