from io import TextIOWrapper
from time import sleep
from math import tan, atan, degrees
from re import compile
from logging import Logger, getLogger

from rich.progress import track
from rich.table import Table, Column
from geocompy.data import Angle, Coordinate
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.communication import open_serial

from ..calculations import adjust_uniform_single
from ..utils import print_success, print_warning, print_error, console


_LINE = compile(r"^\d+(?:\.\d+)?(?:,\-?\d+\.\d+){2}$")


def run_measure(
    tps: GeoCom,
    logger: Logger,
    output: TextIOWrapper | None = None,
    positions: int = 1,
    zero: bool = False,
    cycles: int = 1
) -> None:
    logger.info("Starting inclination measurement")
    turn = 360 // positions
    v = Angle(90, 'deg')
    start = 0

    if not zero:
        angles = tps.tmc.get_angle()
        if angles.params is not None:
            start = round(angles.params[0].asunit('deg'))
        else:
            logger.error("Could not get current orientation, defaulting to 0")

    logger.debug(
        f"Measuring {cycles:d} cycles(s), {positions:d} position(s)/cycle "
        f", {cycles * positions:d} position(s) total, "
        f"starting at {start:d} degrees"
    )
    values: list[tuple[str, str, str]] = []
    for a in track(
        range(start, start + cycles * 360, turn),
        description="Measuring",
        console=console
    ):
        logger.info(f"Measuring at {a:d} degrees")
        hz = Angle(a, 'deg').normalized()
        resp_move = tps.aut.turn_to(hz, v)
        if not resp_move.error == GeoComCode.OK:
            logger.error(
                f"Could not turn to target orientation ({resp_move})"
            )
            print_warning(
                f"Could not turn to target orientation: {a} degrees"
            )
            continue

        sleep(1)  # giving time for the compensator to settle after the move
        fullangles = tps.tmc.get_angle_inclination('MEASURE')
        if fullangles.error != GeoComCode.OK or fullangles.params is None:
            logger.error(
                f"Could not measure inclination ({fullangles})"
            )
            print_warning("Could not measure inclination")
            continue

        az = fullangles.params[0]
        cross = fullangles.params[4]
        length = fullangles.params[5]

        values.append(
            (
                f"{az.asunit('deg'):.4f}",
                f"{cross.asunit('deg') * 3600:.2f}",
                f"{length.asunit('deg') * 3600:.2f}",
            )
        )

    logger.info("Measurements complete")

    if len(values) == 0:
        logger.error("Could not measure inclination in any positions")
        print_error("Could not measure inclination in any positions")
        return

    if output is not None:
        print(
            "hz_deg,cross_sec,length_sec",
            file=output
        )
        for line in values:
            print(
                ",".join(line),
                file=output
            )
    else:
        table = Table(
            Column(r"Hz \[deg]", justify='right'),
            Column(r"Cross \[sec]", justify='right'),
            Column(r"Length \[sec]", justify='right')
        )
        for line in values:
            table.add_row(*line)

        console.print(table)


def main_measure(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    attempts: int = 1,
    sync_after_timeout: bool = False,
    output: TextIOWrapper | None = None,
    positions: int = 1,
    zero: bool = False,
    cycles: int = 1
) -> None:
    logger = getLogger("iman.inclination.measure")
    logger.info(f"Opening connection on {port}")
    with open_serial(
        port,
        attempts=attempts,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger=logger.getChild("instrument"))
        run_measure(
            tps,
            logger,
            output,
            positions,
            zero,
            cycles
        )


def main_merge(
    inputs: list[TextIOWrapper],
    output: TextIOWrapper
) -> None:
    output.write("hz_deg,cross_sec,length_sec\n")
    for item in inputs:
        for line in item:
            if not _LINE.match(line.strip()):
                continue

            output.write(line)

    print_success(f"Merged measurements from {len(inputs)} files.")


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

        coord = Coordinate(tan(cross), tan(length), 1).normalized()
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
    z, _ = adjust_uniform_single([p.z for p in points])

    inc_x = degrees(atan(x)) * 3600
    inc_y = degrees(atan(y)) * 3600
    inc_x_dev = degrees(atan(x_dev)) * 3600
    inc_y_dev = degrees(atan(y_dev)) * 3600

    direction, inc, _ = Coordinate(x, y, z).to_polar()

    if output is None:
        console.print(
            f"""Axis aligned:
    inclination X: {inc_x:.1f}" ± {inc_x_dev:.1f}"
    inclination Y: {inc_y:.1f}" ± {inc_y_dev:.1f}"
Polar:
    direction: {direction.asunit('deg'):.4f}°
    inclination: {inc.asunit('deg') * 3600:.1f}\""""
        )
        return

    output.write(
        "inc_x_sec,inc_x_dev_sec,inc_y_sec,inc_y_dev_sec,dir_deg,inc_sec\n"
    )
    output.write(
        f"{inc_x:.1f},{inc_x_dev:.1f},{inc_y:.1f},{inc_y_dev:.1f},"
        f"{direction.asunit('deg'):.4f},{inc.asunit('deg') * 3600:.1f}\n"
    )
