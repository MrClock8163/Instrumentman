from io import TextIOWrapper

from click_extra import echo
from geocompy.data import Angle
from geocompy.geo import GeoCom
from geocompy.communication import open_serial


def run_measure(
    tps: GeoCom,
    output: TextIOWrapper | None = None,
    positions: int = 1,
    zero: bool = False,
    cycles: int = 1
) -> None:
    turn = 360 // positions
    v = Angle(90, 'deg')
    start = 0

    if not zero:
        angles = tps.tmc.get_angle()
        if angles.params is not None:
            start = round(angles.params[0].asunit('deg'))

    echo(
        "hz,cross,length",
        output
    )

    for a in range(start, start + cycles * 360, turn):
        hz = Angle(a, 'deg').normalized()
        tps.aut.turn_to(hz, v)

        fullangles = tps.tmc.get_angle_inclination('MEASURE')
        if fullangles.params is None:
            continue

        cross = fullangles.params[4]
        length = fullangles.params[5]

        echo(
            f"{a % 360:d},{cross.asunit('deg') * 3600:.2f},"
            f"{length.asunit('deg') * 3600:.2f}",
            output
        )


def main_measure(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    output: TextIOWrapper | None = None,
    positions: int = 1,
    zero: bool = False,
    cycles: int = 1
) -> None:

    with open_serial(
        port,
        retry=2,
        sync_after_timeout=True,
        speed=baud,
        timeout=timeout
    ) as com:
        tps = GeoCom(com)
        run_measure(tps, output, positions, zero, cycles)
