from io import TextIOWrapper
from time import sleep
from pathlib import Path
from math import tan, atan, degrees

from click_extra import echo
from geocompy.data import Angle, Coordinate
from geocompy.geo import GeoCom
from geocompy.communication import open_serial

from ..calculations import adjust_uniform_single
from ..utils import echo_green


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

    for a in range(start, start + cycles * 360, turn):
        hz = Angle(a, 'deg').normalized()
        tps.aut.turn_to(hz, v)

        sleep(1)
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
    inputs: list[Path],
    output: Path
) -> None:
    with output.open("wt", encoding="utf8") as outfile:
        echo("hz_deg,cross_sec,length_sec", outfile)
        for item in inputs:
            with item.open("rt", encoding="utf8") as infile:
                next(infile)
                echo(infile.read(), outfile, False)

    echo_green(f"Merged measurements from {len(inputs)} files.")


def main_calc(
    input: Path
) -> None:
    points: list[Coordinate] = []
    with input.open("rt", encoding="utf8") as file:
        next(file)
        for line in file:
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

    direction, inc, _ = Coordinate(x, y, 1).to_polar()

    echo(
        f"""Direction: {direction.to_dms()}
Inclination: {inc.asunit('deg') * 3600:.1f} seconds
Deviation easting: {degrees(atan(x_dev)) * 3600:.1f} seconds
Deviation northing: {degrees(atan(y_dev)) * 3600:.1f} seconds
        """
    )
