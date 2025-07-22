from click_extra import (
    echo,
    pause
)
from serial import SerialException
from geocompy.data import Angle
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.gsi.dna import GsiOnlineDNA
from geocompy.communication import open_serial

from ..utils import (
    echo_red,
    echo_green,
    echo_yellow
)


def tests_geocom(tps: GeoCom) -> None:
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


def tests_gsidna(dna: GsiOnlineDNA) -> None:
    echo("GSI Online connection successful")
    echo(
        "Various GSI Online DNA functions will be tested. Certain settings "
        "might be changed on the instrument (staff mode, point number, etc.)."
    )
    pause("Press any key when ready to proceed...")

    echo("Testing settings...")
    staff_get = dna.settings.get_staff_mode()
    if staff_get.value is None:
        echo_red("Settings queries unavailable")
    else:
        echo_green("Settings queries available")

    staff_set = dna.settings.set_staff_mode(False)
    if not staff_set.value:
        echo_red("Settings commands unavailable")
    else:
        echo_green("Settings commands available")

    echo("Testing measurements...")
    point_get = dna.measurements.get_point_id()
    if point_get is None:
        echo_red("Measurement/database queries unavailable")
    else:
        echo_green("Measurement/database queries available")

    point_set = dna.measurements.set_point_id("TEST")
    if not point_set.value:
        echo_red("Measurement/database commands unavailable")
    else:
        echo_green("Measurement/database commands available")


def main(
    port: str,
    protocol: str,
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
            if protocol == "geocom":
                tps = GeoCom(com)
                tests_geocom(tps)
            elif protocol == "gsidna":
                dna = GsiOnlineDNA(com)
                tests_gsidna(dna)
    except (SerialException, ConnectionError) as e:
        echo_red(f"Connection was not successful ({e})")
