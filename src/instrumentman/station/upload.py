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
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        tps = GeoCom(com)
        if coordinates is not None and instrumentheight is not None:
            resp_stn = tps.tmc.set_station(
                Coordinate(*coordinates),
                instrumentheight
            )
            if resp_stn.error != GeoComCode.OK:
                echo_red("Cannot set station")
                exit(1)
            else:
                echo_green("Station set")

        if azimuth is not None:
            hz = Angle.from_dms(azimuth)
        elif orientation is not None:
            resp_angle = tps.tmc.get_angle()
            if resp_angle.error != GeoComCode.OK or resp_angle.params is None:
                echo_red("Could not set orientation")
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
            exit(1)

        echo_green("Orientation/azimuth set")
