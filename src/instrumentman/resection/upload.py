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
    coordinates: tuple[float, float, float] = (0, 0, 0),
    instrumentheight: float = 0,
    orientation: str = "0-00-00"
) -> None:
    station = Coordinate(*coordinates)
    ori = Angle.from_dms(orientation)
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        tps = GeoCom(com)
        resp_stn = tps.tmc.set_station(station, instrumentheight)
        if resp_stn.error != GeoComCode.OK:
            echo_red("Cannot set station")
            exit(1)

        resp_angle = tps.tmc.get_angle()
        if resp_angle.error != GeoComCode.OK or resp_angle.params is None:
            echo_red("Cannot set orientation")
            exit(1)

        resp_ori = tps.tmc.set_azimuth(
            (resp_angle.params[0] + ori).normalized()
        )
        if resp_ori.error != GeoComCode.OK:
            echo_red("Cannot set orientation")
            exit(1)

        echo_green("Station and orientation set")
