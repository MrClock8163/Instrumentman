from click_extra import (
    echo,
    pause
)
from serial import SerialException
from geocompy.data import Angle
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.communication import open_serial

from ..utils import (
    echo_red,
    echo_green,
    echo_yellow
)


def tests(tps: GeoCom) -> None:
    echo("GeoCom connection successful")
    echo(
        "Various GeoCom functions will be tested. Certain settings will be "
        "changed on the instrument (ATR off, prism target off, etc.)."
    )
    echo(
        "The program will attempt to use motorized functions. Give "
        "appropriate clearance for the instrument!"
    )
    pause("Press any key when ready to proceed...")

    echo("(Switching ATR off...)")
    tps.aut.switch_atr(False)
    tps.aus.switch_user_atr(False)
    echo("(Switching to reflectorless EDM mode...)")
    tps.bap.set_target_type('DIRECT')
    resp_measure = tps.tmc.do_measurement()
    resp_angles = tps.tmc.get_simple_measurement()
    if (
        resp_measure.error == GeoComCode.OK
        and resp_angles.error == GeoComCode.OK
    ):
        echo_green("Measurements available")
    else:
        echo_yellow(f"Measurements unavailable ({resp_measure.response})")

    resp_focus = tps.cam.set_focus_to_infinity()
    if resp_focus.error == GeoComCode.OK:
        echo_green("Imaging available")
    else:
        echo_yellow(f"Imaging unavailable ({resp_focus.response})")

    resp_changeface = tps.aut.turn_to(0, Angle(180, 'deg'))
    if resp_changeface.error == GeoComCode.OK:
        echo_green("Motorization available")
    else:
        echo_yellow(f"Mororization unavailable ({resp_changeface.response})")


def main(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False
) -> None:
    try:
        with open_serial(
            port,
            speed=baud,
            timeout=timeout,
            retry=retry,
            sync_after_timeout=sync_after_timeout
        ) as com:
            tps = GeoCom(com)
            tests(tps)
    except (SerialException, ConnectionError) as e:
        echo_red(f"GeoCom connection was not successful ({e})")
