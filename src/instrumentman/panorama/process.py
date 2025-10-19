# While the OpenCV Python binding package has some measure of type hints,
# these are often not reliable. To provide more accurate information to the
# reader, typing information provided by 'opencv-python' is overruled (and/or
# ignored) in many places in this module, with types that are closer to the
# actual behavior of the functions in the context of this program (and to
# correct problems in the 'opencv-python' type hints).

import os
from pathlib import Path
from typing import Sequence
from json import JSONDecodeError

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    MofNCompleteColumn,
    TimeRemainingColumn,
    TimeElapsedColumn
)
from jsonschema import ValidationError
from geocompy.data import Coordinate, Angle
import numpy as np
import numpy.typing as npt

try:
    import cv2 as cv
except ModuleNotFoundError:
    print(
        """
The panorama image processing requires extra dependencies.

- opencv-python

Install them manually, or install instrumentman with the 'panorama' extra:

python -m pip install instrumentman[panorama]
"""
    )
    exit(1)

from ..utils import print_warning, print_error, console
from .metadata import read_metadata, PanoramaMetadata


_MAX_SCALE = 5210  # np.iinfo(np.int16).max // (2 * np.pi)


def rot_x(angle: float) -> np.typing.NDArray[np.float64]:
    return np.array(
        (
            (1, 0, 0),
            (0, np.cos(angle), -np.sin(angle)),
            (0, np.sin(angle), np.cos(angle))
        )
    )


def rot_y(angle: float) -> np.typing.NDArray[np.float64]:
    return np.array(
        (
            (np.cos(angle), 0, np.sin(angle)),
            (0, 1, 0),
            (-np.sin(angle), 0, np.cos(angle))
        )
    )


def rot_z(angle: float) -> np.typing.NDArray[np.float64]:
    return np.array(
        (
            (np.cos(angle), -np.sin(angle), 0),
            (np.sin(angle), np.cos(angle), 0),
            (0, 0, 1)
        )
    )


def read_points(
    path: Path,
    skip: int = 0,
    delimiter: str = ","
) -> list[tuple[str, Coordinate, str]]:
    points: list[tuple[str, Coordinate, str]] = []
    with path.open("rt", encoding="utf8") as file:
        for i in range(skip):
            next(file)

        for line in file:
            fields = line.strip().split(delimiter)
            if len(fields) == 4:
                pt, x, y, z = fields
                label = ""
            else:
                pt, x, y, z = fields[:4]
                label = fields[4]

            points.append(
                (
                    pt,
                    Coordinate(
                        float(x),
                        float(y),
                        float(z)
                    ),
                    label
                )
            )

    return points


def apply_rotation(
    coord: Coordinate,
    mat: npt.NDArray[np.floating]
) -> Coordinate:
    vector = np.array((coord.x, coord.y, coord.z))
    vector @= mat

    return Coordinate(
        vector[0],
        vector[1],
        vector[2]
    )


def mean_coordinate(coords: list[Coordinate]) -> Coordinate:
    x: float = np.mean(np.array([c.x for c in coords]))
    y: float = np.mean(np.array([c.y for c in coords]))
    z: float = np.mean(np.array([c.z for c in coords]))

    return Coordinate(x, y, z)


def text_pos(
    text: str,
    point: tuple[float, float],
    offset: tuple[float, float],
    font: int,
    fontscale: float,
    thickness: int,
    justify: str
) -> tuple[int, int]:
    (w, h), _ = cv.getTextSize(
        text,
        font,
        fontscale,
        thickness
    )

    x, y = point
    ox, oy = offset

    match justify[0]:
        case "t":
            y += h
        case "m":
            y += h / 2

    match justify[1]:
        case "c":
            x -= w / 2
        case "r":
            x -= w

    return round(x + ox), round(y + oy)


def run_processing(
    meta: PanoramaMetadata,
    output: Path,
    images: dict[str, Path],
    shift: Angle,
    scale: float | None = None,
    points: list[tuple[str, Coordinate, str]] = [],
    compenstation_mode: int = cv.detail.EXPOSURE_COMPENSATOR_GAIN,
    blending_mode: int = cv.detail.BLENDER_MULTI_BAND,
    seam_mode: int = cv.detail.SEAM_FINDER_VORONOI_SEAM,
    seam_overlap: int = 0,
    visualize_stitch: bool = False,
    color: tuple[int, int, int] = (0, 0, 0),
    font: int = cv.FONT_HERSHEY_PLAIN,
    fontscale: float = 1,
    thickness: int = 2,
    marker: int = cv.MARKER_CROSS,
    markersize: int = 10,
    offset: tuple[int, int] = (10, -10),
    justify: str = "bl",
    label_font: int = cv.FONT_HERSHEY_PLAIN,
    label_fontscale: float = 1,
    label_thickness: int = 2,
    label_color: tuple[int, int, int] = (0, 0, 0),
    label_offset: tuple[int, int] = (10, 10),
    label_justify: str = "tl",
) -> None:
    corners: list[Sequence[int]] = []
    images_warped: list[npt.NDArray[np.uint8]] = []
    masks_warped: list[npt.NDArray[np.uint8]] = []

    center = Coordinate(*meta["center"])
    focal = meta["focal"]
    principal_x, principal_y = meta["principal"]
    camera_offset = Coordinate(*meta["camera_offset"])
    camera_yaw = meta["camera_deviation"][0]
    camera_pitch = meta["camera_deviation"][1]
    camera_roll = meta["camera_deviation"][2]

    instrinsics: npt.NDArray[np.float32] = np.array(
        (
            (focal, 0.0, principal_x),
            (0.0, focal, principal_y),
            (0.0, 0.0, 1.0)
        )
    ).astype(np.float32)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        warper: cv.PyRotationWarper | None = None
        for data in progress.track(
            meta["images"],
            description="Preprocessing images"
        ):
            vec = Coordinate(*data["vector"])
            path = images.get(data["filename"])
            if path is None:
                print_warning(f"Could not find '{data['filename']}'")
                continue

            # Returns uint8
            img: npt.NDArray[np.uint8] = cv.imread(
                str(path),
                cv.IMREAD_COLOR_BGR
            )  # type: ignore[assignment]
            if img is None:
                print_warning(f"Could not load '{data['filename']}'")
                continue

            hz, v, _ = vec.to_polar()
            hz = (hz - shift).normalized()
            height: int
            width: int
            height, width, _ = img.shape

            if visualize_stitch:
                img = np.stack(
                    (
                        np.full(
                            (height, width),
                            np.random.randint(0, 255),
                            np.uint8
                        ),
                        np.full(
                            (height, width),
                            np.random.randint(0, 255),
                            np.uint8
                        ),
                        np.full(
                            (height, width),
                            np.random.randint(0, 255),
                            np.uint8
                        )
                    ),
                    axis=2
                )

            if warper is None:
                if scale is None:
                    scale = focal

                scale = min(scale, _MAX_SCALE)
                warper = cv.PyRotationWarper("spherical", scale)

            rot: npt.NDArray[np.float32] = (
                rot_y(float(hz))
                @ rot_x(np.pi / 2 - float(v))
                @ rot_z(-camera_roll)
            ).astype(np.float32)

            # Maintains input type (uint8)
            image_warped: npt.NDArray[np.uint8]
            corner, image_warped = warper.warp(  # type: ignore[assignment]
                img,
                instrinsics,
                rot,
                cv.INTER_LINEAR,
                cv.BORDER_REPLICATE
            )

            mask_warped: npt.NDArray[np.uint8]
            _, mask_warped = warper.warp(  # type: ignore[assignment]
                np.full((height, width), 255, np.uint8),
                instrinsics,
                rot,
                cv.INTER_NEAREST,
                cv.BORDER_CONSTANT
            )
            corners.append(corner)
            images_warped.append(image_warped)
            masks_warped.append(mask_warped)

        task_seams = progress.add_task(description="Finding seams", total=None)
        finder = cv.detail.SeamFinder.createDefault(seam_mode)
        seams = finder.find(
            images_warped,  # type: ignore[arg-type]
            corners,
            masks_warped  # type: ignore[arg-type]
        )

        if scale is None:
            scale = 1000

        progress.update(task_seams, completed=len(seams), total=len(seams))

        task_merge = progress.add_task(
            description="Merging images",
            total=None
        )
        compensator = cv.detail.ExposureCompensator.createDefault(
            compenstation_mode
        )
        if compenstation_mode != cv.detail.EXPOSURE_COMPENSATOR_NO:
            compensator.feed(
                corners,
                images_warped,  # type: ignore[arg-type]
                masks_warped  # type: ignore[arg-type]
            )

        if seam_overlap == -1:
            seam_overlap = round(scale / 100)

        if seam_overlap > 0 and seam_mode != cv.detail.SEAM_FINDER_NO:
            kernel_size = 1 + 2 * seam_overlap
            kernel = cv.UMat(
                np.ones((kernel_size, kernel_size), np.uint8)
            )  # type: ignore[call-overload]
        else:
            kernel = None

        blender = cv.detail.Blender.createDefault(blending_mode)
        blender.prepare(
            corners,
            [(i.shape[1], i.shape[0]) for i in images_warped]
        )
        for i, (corner, img, msk, seam_msk) in enumerate(
            zip(corners, images_warped, masks_warped, seams)
        ):
            if compenstation_mode != cv.detail.EXPOSURE_COMPENSATOR_NO:
                img = compensator.apply(
                    i,
                    corner,
                    img,
                    msk
                )  # type: ignore[assignment]

            if kernel is not None:
                seam_msk = cv.dilate(
                    seam_msk,
                    kernel,
                    borderType=cv.BORDER_CONSTANT
                )

            blender.feed(
                img.astype(np.int16),
                seam_msk.get().astype(np.uint8),
                corner
            )

        result: npt.NDArray[np.int16]
        result, _ = blender.blend(
            None, None
        )  # type: ignore[call-overload]

        progress.update(
            task_merge,
            completed=len(images_warped),
            total=len(images_warped)
        )

        if len(points) > 0:
            # Top left image top left point for reference
            origin_x, origin_y, _, _ = cv.detail.resultRoi(
                corners,
                [(i.shape[1], i.shape[0]) for i in images_warped]
            )
            full_360 = round(scale * np.pi * 2)

            hz_0 = Angle(0)

            for pt, coord, label in progress.track(
                points,
                description="Annotating points"
            ):
                # To calculate the approximate "telescope" rotation, a
                # preliminary polar position is needed. Then the camera offset
                # is rotated with the preliminary angles.
                prelim_hz, prelim_v, _ = (coord - center).to_polar()
                offset_rot = (
                    rot_z(
                        float(prelim_hz)
                        - np.asin(
                            camera_yaw / np.sin(
                                float(prelim_v)
                                - camera_pitch
                            )
                        )
                    )
                    @ rot_x(np.pi / 2 - float(prelim_v) - camera_pitch)
                )
                pt_hz, pt_v, _ = (
                    coord
                    - (center + apply_rotation(camera_offset * 2, offset_rot))
                ).to_polar()
                pt_hz = (pt_hz - shift).normalized()

                pt_hz_rel = pt_hz.relative_to(hz_0)
                pt_x = round(float(pt_hz_rel) * scale - origin_x) % full_360
                pt_y = round(float(pt_v) * scale - origin_y) % full_360

                cv.drawMarker(
                    result,
                    (pt_x, pt_y),
                    color,
                    marker,
                    markersize,
                    thickness
                )

                cv.putText(
                    result,
                    pt,
                    text_pos(
                        pt,
                        (pt_x, pt_y),
                        offset,
                        font,
                        fontscale,
                        thickness,
                        justify
                    ),
                    font,
                    fontscale,
                    color,
                    thickness,
                    bottomLeftOrigin=False
                )
                if label == "":
                    continue

                cv.putText(
                    result,
                    label,
                    text_pos(
                        label,
                        (pt_x, pt_y),
                        label_offset,
                        label_font,
                        label_fontscale,
                        label_thickness,
                        label_justify
                    ),
                    label_font,
                    label_fontscale,
                    label_color,
                    label_thickness,
                    bottomLeftOrigin=False
                )

        task_save = progress.add_task("Saving final image", total=None)
        # For some reason the blending function returns the image as int16
        # instead uint8, and it might contain negative values. These need to be
        # clipped, otherwise the type conversion will result in color artifacts
        # due to the integer underflow.
        result = np.clip(result, 0, 255)
        cv.imwrite(
            str(output),
            result.astype(np.uint8)
        )
        progress.update(task_save, completed=1, total=1)


_MARKER_MAP = {
    "cross": cv.MARKER_CROSS,
    "x": cv.MARKER_TILTED_CROSS,
    "star": cv.MARKER_STAR,
    "diamond": cv.MARKER_DIAMOND,
    "square": cv.MARKER_SQUARE,
    "uptriangle": cv.MARKER_TRIANGLE_UP,
    "downtriangle": cv.MARKER_TRIANGLE_DOWN
}

_FONT_MAP = {
    "plain": cv.FONT_HERSHEY_PLAIN,
    "simplex": cv.FONT_HERSHEY_SIMPLEX,
    "duplex": cv.FONT_HERSHEY_DUPLEX,
    "complex": cv.FONT_HERSHEY_COMPLEX
}


_COMP_MAP = {
    "none": cv.detail.EXPOSURE_COMPENSATOR_NO,
    "channels": cv.detail.EXPOSURE_COMPENSATOR_CHANNELS,
    "gain": cv.detail.EXPOSURE_COMPENSATOR_GAIN
}


_BLEND_MAP = {
    "none": cv.detail.BLENDER_NO,
    "multiband": cv.detail.BLENDER_MULTI_BAND,
    "feather": cv.detail.BLENDER_FEATHER
}


_SEAM_MAP = {
    "none": cv.detail.SEAM_FINDER_NO,
    "voronoi": cv.detail.SEAM_FINDER_VORONOI_SEAM,
    "dynamic-programming": cv.detail.SEAM_FINDER_DP_SEAM
}


def main(
    metadata: Path,
    output: Path,
    image: tuple[Path],
    shift: str | None = None,
    compensation: str = "channel",
    blending: str = "multiband",
    seams: str = "voronoi",
    seam_overlap: int = 0,
    visualize_stitch: bool = False,
    scale: float | None = None,
    width: int | None = None,
    height: int | None = None,
    annotate: Path | None = None,
    skip: int = 0,
    delimiter: str = ",",
    color: tuple[int, int, int] = (0, 0, 0),
    font: str = "plain",
    fontsize: int = 10,
    thickness: int = 1,
    marker: str = "cross",
    markersize: int = 50,
    offset: tuple[int, int] | None = (10, -10),
    justify: str = "bl",
    label_font: str | None = None,
    label_fontsize: int | None = None,
    label_color: tuple[int, int, int] | None = None,
    label_thickness: int | None = None,
    label_offset: tuple[int, int] | None = (10, 10),
    label_justify: str = "bl"
) -> None:
    try:
        meta = read_metadata(metadata)
    except (ValidationError, JSONDecodeError):
        print_error(
            "The metadata file is not a valid JSON or does not follow the "
            "required schema"
        )
        exit(1)

    if annotate is not None:
        points = read_points(annotate, skip, delimiter)
    else:
        points = []

    image_map: dict[str, Path] = {p.stem + p.suffix: p for p in image}

    if width is not None:
        scale = width / (2 * np.pi)
    elif height is not None:
        scale = height / np.pi

    color = (color[2], color[1], color[0])
    if label_color is None:
        label_color = color
    else:
        label_color = (label_color[2], label_color[1], label_color[0])

    fontscale = cv.getFontScaleFromHeight(
        _FONT_MAP[font],
        fontsize,
        thickness
    )

    if label_thickness is None:
        label_thickness = thickness

    if label_fontsize is None:
        label_fontsize = fontsize

    if label_font is None:
        label_font = font

    label_fontscale = cv.getFontScaleFromHeight(
        _FONT_MAP[label_font],
        label_fontsize,
        label_thickness
    )

    if offset is None:
        offset = (fontsize // 2, -fontsize // 2)

    if label_offset is None:
        label_offset = (label_fontsize // 2, label_fontsize // 2)

    # Suppress OpenCV native warning logs if the user did not set a specific
    # logging level. Warnings break the rich console feedback.
    if "OPENCV_LOG_LEVEL" not in os.environ:
        os.environ["OPENCV_LOG_LEVEL"] = "OFF"

    try:
        run_processing(
            meta,
            output,
            image_map,
            Angle.from_dms(shift) if shift is not None else Angle(0),
            scale,
            points,
            _COMP_MAP[compensation],
            _BLEND_MAP[blending],
            _SEAM_MAP[seams],
            seam_overlap,
            visualize_stitch,
            color,
            _FONT_MAP[font],
            fontscale,
            thickness,
            _MARKER_MAP[marker],
            markersize,
            offset,
            justify,
            _FONT_MAP[label_font],
            label_fontscale,
            label_thickness,
            label_color,
            label_offset,
            label_justify
        )
    except cv.error as cve:
        print_error(f"The process failed due to an OpenCV error ({cve.code})")
        print_error(cve.err)
        raise cve
