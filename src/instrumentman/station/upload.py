from logging import getLogger

from geocompy.data import Angle, Coordinate
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode

from ..utils import echo_red, echo_green


def main(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    coordinates: tuple[float, float, float] | None = None,
    instrumentheight: float | None = None,
    orientation: str | None = None,
    azimuth: str | None = None
) -> None:
    logger = getLogger("iman.station.upload")
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger.getChild("instrument"))
        if coordinates is not None and instrumentheight is not None:
            resp_stn = tps.tmc.set_station(
                Coordinate(*coordinates),
                instrumentheight
            )
            if resp_stn.error != GeoComCode.OK:
                echo_red("Cannot set station")
                logger.critical(f"Cannot set station ({resp_stn})")
                exit(1)
            else:
                echo_green("Station set")
                logger.info(f"Station set to {coordinates}")

        if azimuth is not None:
            hz = Angle.from_dms(azimuth)
            logger.info(f"Setting azimuth to {azimuth}")
        elif orientation is not None:
            logger.info(f"Setting orientation to {orientation}")
            resp_angle = tps.tmc.get_angle()
            if resp_angle.error != GeoComCode.OK or resp_angle.params is None:
                echo_red("Could not get current orientation")
                logger.critical(
                    f"Could not get current orientation ({resp_angle})"
                )
                exit(1)

            hz = (
                resp_angle.params[0]
                + Angle.from_dms(orientation)
            ).normalized()
        else:
            exit()

        resp_ori = tps.tmc.set_azimuth(hz)
        if resp_ori.error != GeoComCode.OK:
            echo_red("Could not set orientation/azimuth")
            logger.critical(f"Could not set orientation/azimuth ({resp_ori})")
            exit(1)

        echo_green("Orientation/azimuth set")
        logger.info("Orientation/azimuth set")
