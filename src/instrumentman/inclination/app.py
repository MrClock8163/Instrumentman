from io import TextIOWrapper
from time import sleep
from math import tan, atan, degrees
from re import compile

from click_extra import echo, progressbar
from geocompy.data import Angle, Coordinate
from geocompy.geo import GeoCom
from geocompy.communication import open_serial

from ..calculations import adjust_uniform_single
from ..utils import echo_green


_LINE = compile(r"^\d+(?:\.\d+)?(?:,\-?\d+\.\d+){2}$")


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
        "hz_deg,cross_sec,length_sec",
        output
    )

    with progressbar(
        range(start, start + cycles * 360, turn),
        label="Measuring",
        hidden=output is None
    ) as bar:
        for a in bar:
            hz = Angle(a, 'deg').normalized()
            tps.aut.turn_to(hz, v)

            sleep(1)
            fullangles = tps.tmc.get_angle_inclination('MEASURE')
            if fullangles.params is None:
                continue

            az = fullangles.params[0]
            cross = fullangles.params[4]
            length = fullangles.params[5]

            echo(
                f"{az.asunit('deg'):.4f},"
                f"{cross.asunit('deg') * 3600:.2f},"
                f"{length.asunit('deg') * 3600:.2f}",
                output
            )


def main_measure(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    output: TextIOWrapper | None = None,
    positions: int = 1,
    zero: bool = False,
    cycles: int = 1
) -> None:
    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout
    ) as com:
        tps = GeoCom(com)
        run_measure(tps, output, positions, zero, cycles)


def main_merge(
    inputs: list[TextIOWrapper],
    output: TextIOWrapper
) -> None:
    echo("hz_deg,cross_sec,length_sec", output)
    for item in inputs:
        for line in item:
            if not _LINE.match(line.strip()):
                continue

            echo(line, output, False)

    echo_green(f"Merged measurements from {len(inputs)} files.")


def main_calc(
    input: TextIOWrapper,
    output: TextIOWrapper | None = None
) -> None:
    points: list[Coordinate] = []

    for line in input:
        if not _LINE.match(line.strip()):
            continue

        fields = line.strip().split(",")
        azimut = Angle(float(fields[0]), 'deg')
        cross = Angle(float(fields[1]) / 3600, 'deg')
        length = Angle(float(fields[2]) / 3600, 'deg')

        coord = Coordinate(tan(cross), tan(length), 1)
        bearing, inclination, s = coord.to_polar()

        points.append(
            Coordinate.from_polar(
                (bearing + azimut).normalized(),
                inclination,
                s
            )
        )

    x, x_dev = adjust_uniform_single([p.x for p in points])
    y, y_dev = adjust_uniform_single([p.y for p in points])

    inc_x = degrees(atan(x)) * 3600
    inc_y = degrees(atan(y)) * 3600
    inc_x_dev = degrees(atan(x_dev)) * 3600
    inc_y_dev = degrees(atan(y_dev)) * 3600

    direction, inc, _ = Coordinate(x, y, 1).to_polar()

    if output is None:
        echo(f"""Axis aligned:
    inclination X: {inc_x:.1f}" +/- {inc_x_dev:.1f}"
    inclination Y: {inc_y:.1f}" +/- {inc_y_dev:.1f}"
Polar:
    direction: {direction.asunit('deg'):.4f}°
    inclination: {inc.asunit('deg') * 3600:.1f}\""""
             )
        return

    echo(
        "inc_x_sec,inc_x_dev_sec,inc_y_sec,inc_y_dev_sec,dir_deg,inc_sec",
        output
    )

    echo(
        (
            f"{inc_x:.1f},{inc_x_dev:.1f},{inc_y:.1f},{inc_y_dev:.1f},"
            f"{direction.asunit('deg'):.4f},{inc.asunit('deg') * 3600:.1f}"
        ),
        output
    )
