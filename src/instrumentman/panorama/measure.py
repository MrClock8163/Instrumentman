from typing import TextIO
import math
from logging import getLogger, Logger

from click_extra import pause
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gcdata import Zoom
from geocompy.geo.gctypes import GeoComCode

from ..utils import echo_red


def run_panorama(
    tps: GeoCom,
    file: TextIO,
    zoom: Zoom,
    logger: Logger
) -> None:

    pause("Aim the instrument at the starting corner, then press any key...")
    resp_start = tps.tmc.get_angle()
    if resp_start.error != GeoComCode.OK or resp_start.params is None:
        echo_red("Could not retrieve starting corner angles")
        logger.critical("Could not retrieve starting corner angles")
        exit(1)

    pause("Aim the instrument at the finishing corner, then press any key...")
    resp_end = tps.tmc.get_angle()
    if resp_end.error != GeoComCode.OK or resp_end.params is None:
        echo_red("Could not retrieve finishing corner angles")
        logger.critical("Could not retrieve finishing corner angles")
        exit(1)

    from_hz, from_v = resp_start.params
    to_hz, to_v = resp_end.params

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

    fov_hz, fov_v = resp_fov.params

    delta_hz = to_hz.relative_to(from_hz)
    delta_v = to_v.relative_to(from_v)

    cols = math.ceil(abs(float(delta_hz)) / float(fov_hz)) + 1
    rows = math.ceil(abs(float(delta_v)) / float(fov_v)) + 1

    print(
        "image",
        "fov_hz_rad",
        "fov_v_rad",
        "pos_x_m",
        "pos_y_m",
        "pos_z_m",
        "dir_x_m",
        "dir_y_m",
        "dir_z_m",
        sep=",",
        file=file
    )

    counter = 1
    for i in range(rows):
        for j in range(cols):
            tps.aut.turn_to(
                (from_hz + delta_hz * j / (cols - 1)).normalized(),
                (from_v + delta_v * i / (rows - 1)).normalized()
            )
            tps.cam.set_actual_image_name(
                "panorama",
                counter
            )
            tps.cam.take_image()
            resp_cam_pos = tps.cam.get_camera_position()
            if resp_cam_pos.params is None:
                echo_red("Could not retrieve camera position")
                logger.critical("Could not retrieve camera position")
                exit(1)

            pos = resp_cam_pos.params

            resp_cam_dir = tps.cam.get_camera_direction(1)
            if resp_cam_dir.params is None:
                echo_red("Could not retrieve camera direction")
                logger.critical("Could not retrieve camera direction")
                exit(1)

            vec = resp_cam_dir.params

            print(
                f"panorama{counter:05d}.jpg",
                float(fov_hz),
                float(fov_v),
                pos.x,
                pos.y,
                pos.z,
                vec.x,
                vec.y,
                vec.z,
                sep=",",
                file=file
            )

            counter += 1


def main(
    port: str,
    metadata: TextIO,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    zoom: str = "x1"
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
        run_panorama(tps, metadata, Zoom[zoom.upper()], logger)
