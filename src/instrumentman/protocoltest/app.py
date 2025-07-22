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

    echo("Testing subsystems...")
    resp_aus = tps.aus.switch_user_atr(False)
    if resp_aus.error == GeoComCode.OK:
        echo_green("Alt User available")
    else:
        echo_yellow(f"Alt User unavailable ({resp_aus.response})")

    tps.aut.switch_atr(False)
    resp_aut = tps.aut.turn_to(0, Angle(180, 'deg'))
    if resp_aut.error == GeoComCode.OK:
        echo_green("Automation available")
    else:
        echo_yellow(f"Automation unavailable ({resp_aut.response})")

    resp_bap = tps.bap.get_measurement_program()
    if resp_bap.error == GeoComCode.OK:
        echo_green("Basic Applications available")
    else:
        echo_yellow(f"Basic Applications unavailable ({resp_bap.response})")

    resp_bmm = tps.bmm.beep_normal()
    if resp_bmm.error == GeoComCode.OK:
        echo_green("Basic Man-Machine interface available")
    else:
        echo_yellow(
            "Basic Man-Machine interface unavailable "
            f"({resp_bmm.response})"
        )

    resp_cam = tps.cam.set_focus_to_infinity()
    if resp_cam.error == GeoComCode.OK:
        echo_green("Camera available")
    else:
        echo_yellow(f"Camera unavailable ({resp_cam.response})")

    echo_green("Communcation available")

    resp_csv = tps.csv.get_instrument_name()
    if resp_csv.error == GeoComCode.OK:
        echo_green("Central Services available")
    else:
        echo_yellow(f"Central Services unavailable ({resp_csv.response})")

    resp_ctl = tps.ctl.get_wakeup_counter()
    if resp_ctl.error == GeoComCode.OK:
        echo_green("Control Task available")
    else:
        echo_yellow(f"Control Task unavailable ({resp_ctl.response})")

    resp_dna = tps.dna.switch_staffmode(False)
    if resp_dna.error == GeoComCode.OK:
        echo_green("Digital Level available")
    else:
        echo_yellow(f"Digital Level unavailable ({resp_dna.response})")

    resp_edm = tps.edm.switch_laserpointer(False)
    if resp_edm.error == GeoComCode.OK:
        echo_green("Electronic Distance Measurement available")
    else:
        echo_yellow(
            "Electronic Distance Measurement unavailable "
            f"({resp_edm.response})"
        )

    resp_ftr = tps.ftr.setup_listing()
    if resp_ftr.error == GeoComCode.OK:
        echo_green("File Transfer available")
        tps.ftr.abort_list()
    else:
        echo_yellow(f"File Transfer unavailable ({resp_ftr.response})")

    resp_img = tps.img.get_telescopic_configuration()
    if resp_img.error == GeoComCode.OK:
        echo_green("Imaging available")
    else:
        echo_yellow(f"Imaging unavailable ({resp_img.response})")

    resp_kdm = tps.kdm.get_display_power_status()
    if resp_kdm.error == GeoComCode.OK:
        echo_green("Keyboard Display Unit available")
    else:
        echo_yellow(f"Keyboard Display Unit unavailable ({resp_kdm.response})")

    tps.mot.stop_controller()
    resp_mot = tps.mot.start_controller()
    if resp_mot.error == GeoComCode.OK:
        echo_green("Motorization available")
    else:
        echo_yellow(f"Motorization unavailable ({resp_mot.response})")

    resp_sup = tps.sup.get_poweroff_configuration()
    if resp_sup.error == GeoComCode.OK:
        echo_green("Supervisor available")
    else:
        echo_yellow(f"Supervisor unavailable ({resp_sup.response})")

    resp_tmc = tps.tmc.get_station()
    if resp_tmc.error == GeoComCode.OK:
        echo_green("Theodolite Measurement and Calculation available")
    else:
        echo_yellow(
            "Theodolite Measurement and Calculation unavailable "
            f"({resp_tmc.response})"
        )

    resp_wir = tps.wir.get_recording_format()
    if resp_wir.error == GeoComCode.OK:
        echo_green("Word Index Registration available")
    else:
        echo_yellow(
            "Word Index Registration unavailable "
            f"({resp_wir.response})"
        )


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
        echo_yellow(f"Settings queries unavailable ({staff_get.response})")
    else:
        echo_green("Settings queries available")

    staff_set = dna.settings.set_staff_mode(False)
    if not staff_set.value:
        echo_yellow(f"Settings commands unavailable ({staff_set.response})")
    else:
        echo_green("Settings commands available")

    echo("Testing measurements...")
    point_get = dna.measurements.get_point_id()
    if point_get.value is None:
        echo_yellow(
            f"Measurement/database queries unavailable ({point_get.response})"
        )
    else:
        echo_green("Measurement/database queries available")

    point_set = dna.measurements.set_point_id("TEST")
    if not point_set.value:
        echo_yellow(
            f"Measurement/database commands unavailable ({point_set.response})"
        )
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
            try:
                if protocol == "geocom":
                    tps = GeoCom(com)
                    tests_geocom(tps)
                elif protocol == "gsidna":
                    dna = GsiOnlineDNA(com)
                    tests_gsidna(dna)
            except Exception as e:
                echo_red("An exception occured while running the tests")
                echo_red(e)

    except (SerialException, ConnectionError) as e:
        echo_red(f"Connection was not successful ({e})")
