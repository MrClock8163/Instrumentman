from typing import TextIO, Generator
import math
from logging import getLogger, Logger

from rich.console import Console
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn
)
from click_extra import pause, confirm
from geocompy.data import Coordinate, Angle
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gcdata import Zoom
from geocompy.geo.gctypes import GeoComCode

from ..utils import echo_red, echo_yellow


def image_positions(
    from_hz: Angle,
    from_v: Angle,
    delta_hz: Angle,
    delta_v: Angle,
    cols: int,
    rows: int
) -> Generator[tuple[int, Angle, Angle], None, None]:
    if cols < 1 or rows < 1:
        raise ValueError(
            "Cannot generate positions for less than "
            f"1 ({rows})row and/or 1 ({cols}) column"
        )

    to_hz = from_hz + delta_hz
    if rows == 1:
        from_v = from_v + delta_v / 2
    if cols == 1:
        from_hz = (from_hz + delta_hz / 2).normalized()

    colstep = (delta_hz / (cols - 1)) if cols > 1 else Angle(0)
    rowstep = (delta_v / (rows - 1)) if rows > 1 else Angle(0)

    counter = 0
    for i in range(rows):
        for j in range(cols):
            counter += 1
            yield (
                counter,
                (
                    (from_hz + colstep * j)
                    if i % 2 == 0
                    else (to_hz - colstep * j)
                ).normalized(),
                (from_v + rowstep * i).normalized()
            )


def run_panorama(
    tps: GeoCom,
    file: TextIO,
    zoom: Zoom,
    overlap: tuple[int, int],
    prefix: str,
    logger: Logger
) -> None:
    pause(
        "Aim the instrument at the left starting corner, then press any key..."
    )
    resp_start = tps.tmc.get_angle()
    if resp_start.error != GeoComCode.OK or resp_start.params is None:
        echo_red("Could not retrieve starting corner angles")
        logger.critical("Could not retrieve starting corner angles")
        exit(1)

    pause(
        "Aim the instrument at the right finish corner, then press any key..."
    )
    resp_end = tps.tmc.get_angle()
    if resp_end.error != GeoComCode.OK or resp_end.params is None:
        echo_red("Could not retrieve finishing corner angles")
        logger.critical("Could not retrieve finishing corner angles")
        exit(1)

    from_hz, from_v = resp_start.params
    to_hz, to_v = resp_end.params
    if to_v == from_v or to_hz == from_hz:
        echo_red("Cannot capture panorama in a single row/column")
        logger.critical("Cannot capture panorama in a single row/column")
        exit(1)
    elif (
        not (0 < from_v < math.pi)
        or not (0 < to_v < math.pi)
    ):
        echo_red("Cannot capture panorama in face 2")
        logger.critical("Cannot capture panorama in face 2")
        exit(1)

    if to_v < from_v:
        to_v, from_v = from_v, to_v

    # If the pointer is left active by accident, it will show up on every
    # image.
    tps.edm.switch_laserpointer(False)

    resp_zoom = tps.cam.set_zoom(zoom)
    if resp_zoom.error != GeoComCode.OK:
        echo_red("Could set retrieve camera zoom factor")
        logger.critical("Could set retrieve camera zoom factor")
        exit(1)

    resp_fov = tps.cam.get_camera_fov(zoom=zoom)
    if resp_fov.params is None:
        echo_red("Could not retrieve camera FOV")
        logger.critical("Could not retrieve camera FOV")
        exit(1)

    resp_station = tps.tmc.get_station()
    if resp_station.error != GeoComCode.OK or resp_station.params is None:
        echo_red("Could not retrieve station coordinates")
        logger.critical("Could not retrieve station coordinates")
        exit(1)

    station, hi = resp_station.params
    center = station + Coordinate(0, 0, hi)

    fov_hz, fov_v = resp_fov.params
    reduced_fov_hz = float(fov_hz) * (1 - overlap[0] / 100)
    reduced_fov_v = float(fov_hz) * (1 - overlap[1] / 100)

    delta_hz = (to_hz - from_hz).normalized()
    delta_v = to_v - from_v

    if abs(float(delta_hz)) < reduced_fov_hz:
        cols = 1
    else:
        cols = math.ceil(abs(float(delta_hz)) / reduced_fov_hz) + 1

    if abs(float(delta_v)) < reduced_fov_v:
        rows = 1
    else:
        rows = math.ceil(abs(float(delta_v)) / reduced_fov_v) + 1

    if not confirm(
        f"Start capturing images in {rows} row(s) and {cols} column(s)",
        True
    ):
        echo_yellow("Program cancelled")
        exit()

    print(
        "image",
        "fov_hz_rad",
        "fov_v_rad",
        "center_x_m",
        "center_y_m",
        "center_z_m",
        "pos_x_m",
        "pos_y_m",
        "pos_z_m",
        "dir_x_m",
        "dir_y_m",
        "dir_z_m",
        sep=",",
        file=file
    )

    console = Console()
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console
    )
    progress.start()
    task = progress.add_task(
        "Capturing panorama",
        total=rows*cols
    )

    for idx, hz, v in image_positions(
        from_hz,
        from_v,
        delta_hz,
        delta_v,
        cols,
        rows
    ):
        resp_turn = tps.aut.turn_to(hz, v)
        if resp_turn.error != GeoComCode.OK:
            echo_yellow("Could not turn to position")
            logger.error("Could not turn to position")
            continue

        resp_name = tps.cam.set_actual_image_name(prefix, idx)
        if resp_name.error != GeoComCode.OK:
            echo_yellow("Could not set image name")
            logger.error("Could not set image name")
            continue

        resp_img = tps.cam.take_image()
        if resp_img.error != GeoComCode.OK:
            echo_yellow("Could not take image")
            logger.error("Could not take image")
            continue

        resp_cam_pos = tps.cam.get_camera_position()
        if resp_cam_pos.params is None:
            echo_yellow("Could not retrieve camera position")
            logger.error("Could not retrieve camera position")
            continue

        resp_cam_dir = tps.cam.get_camera_direction(1)
        if resp_cam_dir.params is None:
            echo_yellow("Could not retrieve camera direction")
            logger.critical("Could not retrieve camera direction")
            continue

        pos = resp_cam_pos.params + center
        vec = resp_cam_dir.params

        print(
            f"{prefix}{idx:05d}.jpg",
            float(fov_hz),
            float(fov_v),
            center.x,
            center.y,
            center.z,
            pos.x,
            pos.y,
            pos.z,
            vec.x,
            vec.y,
            vec.z,
            sep=",",
            file=file
        )

        progress.update(task, advance=1)

    progress.stop()


def main(
    port: str,
    metadata: TextIO,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    zoom: str = "x1",
    overlap: tuple[int, int] = (30, 30),
    prefix: str = "panorama_"
) -> None:
    logger = getLogger("iman.panorama.measure")
    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger.getChild("instrument"))
        run_panorama(
            tps,
            metadata,
            Zoom[zoom.upper()],
            overlap,
            prefix,
            logger
        )
