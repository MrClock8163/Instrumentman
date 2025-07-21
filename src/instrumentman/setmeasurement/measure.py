import os
from datetime import datetime
from logging import getLogger
from typing import Iterator, Literal
from itertools import chain
import pathlib

from geocompy.data import Angle, Coordinate
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.geo.gcdata import Face

from ..utils import make_logger
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
    filepath: str,
    order_spec: Literal['AaBb', 'AabB', 'ABab', 'ABba', 'ABCD'],
    count: int = 1,
    pointnames: str = ""
) -> Session:
    applog = getLogger("APP")
    points = load_targets_from_json(filepath)
    if pointnames != "":
        use_points = set(pointnames.split(","))
        loaded_points = set(points.get_target_names())
        excluded_points = loaded_points - use_points
        applog.debug(f"Excluding points: {excluded_points}")
        for pt in excluded_points:
            points.pop_target(pt)

    tps.aut.turn_to(0, Angle(180, 'deg'))
    incline = tps.tmc.get_angle_inclination('MEASURE').params
    temp = tps.csv.get_internal_temperature().params
    battery = tps.csv.check_power().params
    resp_station = tps.tmc.get_station().params
    if resp_station is None:
        station = Coordinate(0, 0, 0)
        iheight = 0.0
        applog.warning(
            "Could not retrieve station and instrument height, using default"
        )
    else:
        station, iheight = resp_station

    session = Session(station, iheight)
    for i in range(count):
        applog.info(f"Starting set cycle {i + 1}")
        output = Cycle(
            datetime.now(),
            battery[0] if battery is not None else None,
            temp,
            (incline[4], incline[5]) if incline is not None else None
        )

        for f, t in iter_targets(points, order_spec):
            applog.info(f"Measuring {t.name} ({f.name})")
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
                applog.error(
                    f"ATR fine adjustment failed ({resp_atr.error.name}), "
                    "skipping point"
                )
                continue

            tps.bap.set_prism_type(t.prism)
            tps.tmc.do_measurement()
            resp_angle = tps.tmc.get_simple_measurement(10)
            if resp_angle.params is None:
                applog.error(
                    f"Error during measurement ({resp_angle.error.name}), "
                    "skipping point"
                )
                continue

            output.add_measurement(
                t.name,
                f,
                t.height,
                resp_angle.params
            )
            applog.info("Done")

        session.cycles.append(output)

    tps.aut.turn_to(0, Angle(180, 'deg'))

    return session


def main(
    port: str,
    targets: pathlib.Path,
    directory: pathlib.Path,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    format: str = "setmeasurement_{time}.json",
    cycles: int = 1,
    order: Literal['AaBb', 'AabB', 'ABab', 'ABba', 'ABCD'] = "ABba",
    sync_time: bool = True,
    points: str = "",
    debug: bool = False,
    info: bool = False,
    warning: bool = False,
    error: bool = False,
) -> None:
    log = make_logger("TPS", debug, info, warning, error)
    applog = make_logger("APP", debug, info, warning, error)
    applog.info("Starting measurement session")

    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout
    ) as com:
        tps = GeoCom(com, log)
        if sync_time:
            tps.csv.set_datetime(datetime.now())

        session = measure_set(
            tps,
            str(targets),
            order,
            cycles,
            points
        )

    applog.info("Finished measurement session")

    timestamp = session.cycles[0].time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(
        directory,
        format.format(time=timestamp, order=order, cycle=cycles)
    )
    session.export_to_json(filename)
    applog.info(f"Saved measurement results at '{filename}'")
