from typing import TextIO
import math
from logging import getLogger, Logger
import json

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn
)
from rich.prompt import Confirm
from geocompy.data import Coordinate, Angle
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gcdata import Zoom
from geocompy.geo.gctypes import GeoComCode

from ..utils import console, print_error, print_warning
from .metadata import PanoramaMetadata, PanoramaFrameMetadata


def image_positions(
    from_hz: Angle,
    from_v: Angle,
    to_hz: Angle,
    to_v: Angle,
    fov_hz: Angle,
    fov_v: Angle,
    overlap_hz: int,
    overlap_v: int,
    adaptive_fov: bool
) -> list[tuple[Angle, Angle]]:
    positions: list[tuple[Angle, Angle]] = []
    delta_hz = (to_hz - from_hz).normalized()
    delta_v = (to_v - from_v).normalized()

    center_hz = (from_hz + delta_hz / 2).normalized()
    center_v = (from_v + delta_v / 2).normalized()

    # FOV has to be reduced by twice the overlap percent, because overlap
    # occurs on both sides of the view.
    redfov_hz = fov_hz * (1 - overlap_hz / 50)
    redfov_v = fov_v * (1 - overlap_v / 50)

    if redfov_v < delta_v:
        delta_v -= redfov_v

    rows = math.ceil(float(delta_v) / float(redfov_v))
    delta_v = redfov_v * rows

    if delta_v > math.pi:
        delta_v = Angle(math.pi)
        from_v = Angle(0)
        rows = math.ceil(math.pi / float(redfov_v))
    else:
        from_v = center_v - delta_v / 2

    if from_v < 0:
        from_v = Angle(0)

    elif to_v > math.pi:
        from_v = Angle(math.pi) - delta_v

    rowstep = delta_v / rows
    from_v = from_v + rowstep / 2

    for r in range(rows):
        v = from_v + rowstep * r
        row_delta_hz = delta_hz

        if adaptive_fov:
            if v <= Angle(math.pi / 2):
                row_radius = math.sin(v + redfov_v / 2)
            else:
                row_radius = math.sin(v - redfov_v / 2)

            fovchord = math.sqrt(2 - 2 * math.cos(redfov_hz))

            if fovchord > 2 * row_radius:
                row_redfov_hz = row_delta_hz
            else:
                row_redfov_hz = Angle(
                    math.acos(1 - fovchord**2 / (2*row_radius**2))
                )
        else:
            row_redfov_hz = redfov_hz

        cols = math.ceil(float(row_delta_hz) / float(row_redfov_hz))

        row_delta_hz = row_redfov_hz * cols

        if row_delta_hz > math.pi * 2:
            row_delta_hz = Angle(math.pi * 2)

        colstep = row_delta_hz / (cols)
        row_from_hz = (
            center_hz
            - row_delta_hz / 2
            + colstep / 2
        ).normalized()
        row_to_hz = (
            center_hz
            + row_delta_hz / 2
            - colstep / 2
        ).normalized()

        for c in range(cols):
            if r % 2 == 0:
                hz = (row_from_hz + colstep * c).normalized()
            else:
                hz = (row_to_hz - colstep * c).normalized()

            positions.append((hz, v))

    return positions


def get_extents_region(
    tps: GeoCom,
    horizontal: tuple[Angle, Angle] | None,
    vertical: tuple[Angle, Angle] | None,
    logger: Logger
) -> tuple[Angle, Angle, Angle, Angle]:
    if horizontal is not None and vertical is not None:
        from_hz, to_hz = horizontal
        from_v, to_v = vertical
        return from_hz, from_v, to_hz, to_v

    console.input(
        "Aim the instrument at the left starting corner, "
        "then press ENTER..."
    )
    resp_start = tps.tmc.get_angle()
    if resp_start.error != GeoComCode.OK or resp_start.params is None:
        print_error("Could not retrieve starting corner angles")
        logger.critical("Could not retrieve starting corner angles")
        exit(1)

    console.input(
        "Aim the instrument at the right finish corner, "
        "then press ENTER..."
    )
    resp_end = tps.tmc.get_angle()
    if resp_end.error != GeoComCode.OK or resp_end.params is None:
        print_error("Could not retrieve finishing corner angles")
        logger.critical("Could not retrieve finishing corner angles")
        exit(1)

    from_hz, from_v = resp_start.params
    to_hz, to_v = resp_end.params

    return from_hz, from_v, to_hz, to_v


def get_extents_strip(
    tps: GeoCom,
    vertical: tuple[Angle, Angle] | None,
    logger: Logger
) -> tuple[Angle, Angle, Angle, Angle]:
    from_hz = Angle(0)
    to_hz = Angle(2 * math.pi - 1e-5)
    if vertical is not None:
        from_v, to_v = vertical
        return from_hz, from_v, to_hz, to_v

    console.input(
        "Aim the instrument at the top of the strip, "
        "then press ENTER..."
    )
    resp_start = tps.tmc.get_angle()
    if resp_start.error != GeoComCode.OK or resp_start.params is None:
        print_error("Could not retrieve strip top angles")
        logger.critical("Could not retrieve strip top angles")
        exit(1)

    console.input(
        "Aim the instrument at the bottom of the strip, "
        "then press ENTER..."
    )
    resp_end = tps.tmc.get_angle()
    if resp_end.error != GeoComCode.OK or resp_end.params is None:
        print_error("Could not retrieve strip bottom angles")
        logger.critical("Could not retrieve strip bottom angles")
        exit(1)

    _, from_v = resp_start.params
    _, to_v = resp_end.params

    from_hz = Angle(0)
    to_hz = Angle.from_dms("359-59-59")

    return from_hz, from_v, to_hz, to_v


def get_extents_sphere() -> tuple[Angle, Angle, Angle, Angle]:
    return Angle(0), Angle(0), Angle(2 * math.pi - 1e-5), Angle(math.pi)


def run_panorama(
    tps: GeoCom,
    file: TextIO,
    zoom: Zoom,
    overlap: tuple[int, int],
    prefix: str,
    shape: str,
    layout: str,
    horizontal: tuple[Angle, Angle] | None,
    vertical: tuple[Angle, Angle] | None,
    logger: Logger
) -> None:
    match shape:
        case "sphere":
            from_hz, from_v, to_hz, to_v = get_extents_sphere()
        case "strip":
            from_hz, from_v, to_hz, to_v = get_extents_strip(
                tps,
                vertical,
                logger
            )
        case "region":
            from_hz, from_v, to_hz, to_v = get_extents_region(
                tps,
                vertical,
                horizontal,
                logger
            )
        case _:
            raise ValueError(f"Unknown capture area shape '{shape}'")

    if to_v < from_v:
        to_v, from_v = from_v, to_v

    # If the pointer is left active by accident, it will show up on every
    # image.
    tps.edm.switch_laserpointer(False)

    resp_zoom = tps.cam.set_zoom(zoom)
    if resp_zoom.error != GeoComCode.OK:
        print_error("Could set camera zoom factor")
        logger.critical("Could set camera zoom factor")
        exit(1)

    resp_fov = tps.cam.get_camera_fov(zoom=zoom)
    if resp_fov.params is None:
        print_error("Could not retrieve camera FOV")
        logger.critical("Could not retrieve camera FOV")
        exit(1)

    resp_station = tps.tmc.get_station()
    if resp_station.error != GeoComCode.OK or resp_station.params is None:
        print_error("Could not retrieve station coordinates")
        logger.critical("Could not retrieve station coordinates")
        exit(1)

    resp_intrinsic = tps.cam.get_overview_interior_orientation()
    if resp_intrinsic.error != GeoComCode.OK or resp_intrinsic.params is None:
        print_error("Could not retrieve camera intrinsics")
        logger.critical("Could not retrieve camera intrinsics")
        exit(1)

    cx, cy, focal, pixelsize = resp_intrinsic.params

    resp_extrinsic = tps.cam.get_overview_exterior_orientation()
    if resp_extrinsic.error != GeoComCode.OK or resp_extrinsic.params is None:
        print_error("Could not retrieve camera extrinsics")
        logger.critical("Could not retrieve camera extrinsics")
        exit(1)

    offset, yaw, pitch, roll = resp_extrinsic.params

    station, hi = resp_station.params
    center = station + Coordinate(0, 0, hi)

    fov_hz, fov_v = resp_fov.params

    match layout:
        case "grid":
            positions = image_positions(
                from_hz,
                from_v,
                to_hz,
                to_v,
                fov_hz,
                fov_v,
                overlap[0],
                overlap[1],
                False
            )
        case "adaptive-fov":
            positions = image_positions(
                from_hz,
                from_v,
                to_hz,
                to_v,
                fov_hz,
                fov_v,
                overlap[0],
                overlap[1],
                True
            )
        case _:
            raise ValueError("Unknown position layout")

    if not Confirm.ask(
        f"Start capturing panorama in {len(positions)} frame(s)",
        console=console,
        default=True
    ):
        print_warning("Program cancelled")
        exit()

    images: list[PanoramaFrameMetadata] = []

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
        total=len(positions)
    )

    for idx, (hz, v) in enumerate(positions):
        resp_turn = tps.aut.turn_to(hz, v)
        if resp_turn.error != GeoComCode.OK:
            print_warning("Could not turn to position")
            logger.error("Could not turn to position")
            continue

        resp_name = tps.cam.set_actual_image_name(prefix, idx)
        if resp_name.error != GeoComCode.OK:
            print_warning("Could not set image name")
            logger.error("Could not set image name")
            continue

        resp_img = tps.cam.take_image()
        if resp_img.error != GeoComCode.OK:
            print_warning("Could not take image")
            logger.error("Could not take image")
            continue

        resp_cam_pos = tps.cam.get_camera_position()
        if resp_cam_pos.params is None:
            print_warning("Could not retrieve camera position")
            logger.error("Could not retrieve camera position")
            continue

        resp_cam_dir = tps.cam.get_camera_direction(1)
        if resp_cam_dir.params is None:
            print_warning("Could not retrieve camera direction")
            logger.critical("Could not retrieve camera direction")
            continue

        pos = resp_cam_pos.params + center
        vec = resp_cam_dir.params

        meta: PanoramaFrameMetadata = {
            "filename": f"{prefix}{idx:05d}.jpg",
            "position": (pos.x, pos.y, pos.z),
            "vector": (vec.x, vec.y, vec.z)
        }

        images.append(meta)

        progress.update(task, advance=1)

    progress.stop()

    tps.aut.turn_to(0, math.pi)

    metadata: PanoramaMetadata = {
        "center": (center.x, center.y, center.z),
        "focal": focal / pixelsize,
        "principal": (cx, cy),
        "camera_offset": (offset.x, offset.y, offset.z),
        "camera_deviation": (
            float(yaw),
            float(pitch),
            float(roll)
        ),
        "images": images
    }
    json.dump(metadata, file, indent=4)


def main(
    port: str,
    metadata: TextIO,
    baud: int = 9600,
    timeout: int = 15,
    attempts: int = 1,
    sync_after_timeout: bool = False,
    zoom: str = "x1",
    overlap: tuple[int, int] = (5, 10),
    prefix: str = "panorama_",
    whitebalance: str | None = None,
    increase_tolerance: bool = False,
    shape: str = "region",
    layout: str = "adaptive-fov",
    horizontal: tuple[str, str] | None = None,
    vertical: tuple[str, str] | None = None
) -> None:
    logger = getLogger("iman.panorama.measure")
    with open_serial(
        port,
        attempts=attempts,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger=logger.getChild("instrument"))
        tolerances: tuple[Angle, Angle] | None = None
        try:
            resp_tol = tps.aut.get_tolerance()
            if (
                increase_tolerance
                and resp_tol.error == GeoComCode.OK
                and resp_tol.params is not None
            ):
                print("Set reduced tolerances")
                tolerances = resp_tol.params
                tps.aut.set_tolerance(
                    Angle.from_dms("0-30-00"),
                    Angle.from_dms("0-30-00")
                )
            if whitebalance is not None:
                tps.cam.set_whitebalance(whitebalance.upper())
            run_panorama(
                tps,
                metadata,
                Zoom[zoom.upper()],
                overlap,
                prefix,
                shape,
                layout,
                (
                    Angle.from_dms(horizontal[0]),
                    Angle.from_dms(horizontal[1])
                ) if horizontal is not None else None,
                (
                    Angle.from_dms(vertical[0]),
                    Angle.from_dms(vertical[1])
                ) if vertical is not None else None,
                logger
            )
        finally:
            if tolerances is not None:
                print("Restored reduced tolerances")
                tps.aut.set_tolerance(*tolerances)

            if whitebalance is not None:
                tps.cam.set_whitebalance("AUTO")
