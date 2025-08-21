from datetime import datetime
from logging import Logger, getLogger
from typing import Iterator, Literal
from itertools import chain
import pathlib

from rich.progress import (
    Progress,
    TextColumn,
    TimeElapsedColumn,
    BarColumn,
    TaskProgressColumn
)
from geocompy.data import Angle, Coordinate
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.geo.gcdata import Face

from ..targets import (
    TargetPoint,
    TargetList,
    load_targets_from_json
)
from .sessions import (
    Session,
    Cycle
)


def iter_targets(
    points: TargetList,
    order: str
) -> Iterator[tuple[Face, TargetPoint]]:
    match order:
        case "AaBb":
            return ((f, t) for t in points for f in (Face.F1, Face.F2))
        case "AabB":
            return (
                (f, t) for i, t in enumerate(points)
                for f in (
                    (Face.F1, Face.F2)
                    if i % 2 == 0 else
                    (Face.F2, Face.F1)
                )
            )
        case "ABab":
            return chain(
                ((Face.F1, t) for t in points),
                ((Face.F2, t) for t in points)
            )
        case "ABba":
            return chain(
                ((Face.F1, t) for t in points),
                ((Face.F2, t) for t in reversed(points))
            )
        case "ABCD":
            return ((Face.F1, t) for t in points)

    exit(1200)


def measure_set(
    tps: GeoCom,
    logger: Logger,
    filepath: str,
    order_spec: Literal['AaBb', 'AabB', 'ABab', 'ABba', 'ABCD'],
    count: int = 1,
    pointnames: tuple[str, ...] = ()
) -> Session:
    logger.info("Starting set measurements")
    points = load_targets_from_json(filepath)
    if len(pointnames) > 0:
        use_points = set(pointnames)
        loaded_points = set(points.get_target_names())
        excluded_points = loaded_points - use_points
        logger.debug(f"Excluding points: {excluded_points}")
        for pt in excluded_points:
            points.pop_target(pt)

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TextColumn("{task.fields[label]}")
    )
    progress.start()
    labelformat = "Cycle {}, target {} in {}"
    task = progress.add_task(
        "Measuring set",
        total=count * len(points) * (1 if order_spec == 'ABCD' else 2),
        label=""
    )

    logger.info("Measuring inclination, temperature and battery level")
    tps.aut.turn_to(0, Angle(180, 'deg'))
    incline = tps.tmc.get_angle_inclination('MEASURE').params
    temp = tps.csv.get_internal_temperature().params
    battery = tps.csv.check_power().params
    logger.info("Retrieving station setup")
    resp_station = tps.tmc.get_station().params
    if resp_station is None:
        station = Coordinate(0, 0, 0)
        iheight = 0.0
        logger.error(
            "Could not retrieve station and instrument height, defaulting to 0"
        )
    else:
        station, iheight = resp_station

    session = Session(station, iheight)
    for i in range(count):
        logger.info(f"Starting set cycle {i + 1}")
        output = Cycle(
            datetime.now(),
            battery[0] if battery is not None else None,
            temp,
            (incline[4], incline[5]) if incline is not None else None
        )

        for f, t in iter_targets(points, order_spec):
            progress.update(
                task,
                label=labelformat.format(i + 1, t.name, f.name)
            )
            logger.info(f"Measuring {t.name} ({f.name})")
            rel_coords = (
                (t.coords + Coordinate(0, 0, t.height))
                - (station + Coordinate(0, 0, iheight))
            )
            hz, v, _ = rel_coords.to_polar()
            if f == Face.F2:
                hz = (hz + Angle(180, 'deg')).normalized()
                v = Angle(360, 'deg') - v

            tps.aut.turn_to(hz, v)
            resp_atr = tps.aut.fine_adjust(0.5, 0.5)
            if resp_atr.error != GeoComCode.OK:
                logger.error(
                    f"ATR fine adjustment failed ({resp_atr.error.name}), "
                    "skipping point"
                )
                progress.update(task, advance=1)
                continue

            tps.bap.set_prism_type(t.prism)
            tps.tmc.do_measurement()
            resp_angle = tps.tmc.get_simple_measurement(10)
            if resp_angle.params is None:
                logger.error(
                    f"Error during measurement ({resp_angle.error.name}), "
                    "skipping point"
                )
                progress.update(task, advance=1)
                continue

            output.add_measurement(
                t.name,
                f,
                t.height,
                resp_angle.params
            )
            progress.update(task, advance=1)

        session.cycles.append(output)

    logger.info("Finished set measurements")
    progress.stop()
    logger.info("Returning to face-down position")
    tps.aut.turn_to(0, Angle(180, 'deg'))

    return session


def main(
    port: str,
    targets: pathlib.Path,
    output: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    dateformat: str = "%Y%m%d",
    timeformat: str = "%H%M%S",
    cycles: int = 1,
    order: Literal['AaBb', 'AabB', 'ABab', 'ABba', 'ABCD'] = "ABba",
    sync_time: bool = True,
    points: tuple[str, ...] = ()
) -> None:
    logger = getLogger("iman.sets.measure")
    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger.getChild("instrument"))
        if sync_time:
            tps.csv.set_datetime(datetime.now())
            logger.info("Synced instrument date-time to computer")

        session = measure_set(
            tps,
            logger,
            str(targets),
            order,
            cycles,
            points
        )

    epoch = session.cycles[0].time
    date = epoch.strftime(dateformat)
    time = epoch.strftime(timeformat)
    filename = output.format(
        date=date,
        time=time,
        order=order,
        cycles=cycles
    )
    session.export_to_json(filename)
    logger.info(f"Saved measurement results to '{filename}'")
