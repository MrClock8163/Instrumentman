from pathlib import Path
from typing import Sequence
from json import JSONDecodeError

from rich.console import Console
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    MofNCompleteColumn,
    TimeRemainingColumn
)
from jsonschema import ValidationError
from geocompy.data import Coordinate, Angle
import numpy as np
import numpy.typing as npt

try:
    import cv2 as cv
    import cv2.typing as cvt
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

from ..utils import echo_yellow, echo_red
from .metadata import read_metadata, PanoramaMetadata


_MAX_SCALE = np.iinfo(np.int16).max // (2 * np.pi)


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


def run_annotate(
    meta: PanoramaMetadata,
    output: Path,
    images: dict[str, Path],
    scale: float | None = None,
    points: list[tuple[str, Coordinate, str]] = [],
    camera_offset: Coordinate | None = None,
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
    centers: list[tuple[int, int, Angle, Angle]] = []
    images_warped: list[cvt.MatLike] = []
    masks_warped: list[cvt.MatLike] = []
    cam_offsets: list[Coordinate] = []

    fov_w, fov_h = meta["fov"]
    center = Coordinate(*meta["center"])
    console = Console()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        for data in progress.track(
            meta["images"],
            description="Preprocessing images"
        ):
            pos = Coordinate(*data["position"])
            vec = Coordinate(*data["vector"])
            path = images.get(data["filename"])
            if path is None:
                echo_yellow(f"Could not find '{data['filename']}'")
                continue

            img = cv.imread(str(path))
            if img is None:
                echo_yellow(f"Could not load '{data['filename']}'")
                continue

            hz, v, _ = vec.to_polar()
            height: int
            width: int
            height, width, _ = img.shape
            f_w: float = width / 2 / np.tan(fov_w / 2)
            f_h: float = height / 2 / np.tan(fov_h / 2)
            if scale is None:
                scale = (f_w + f_h) / 2

            scale = min(scale, _MAX_SCALE)

            instrinsics: npt.NDArray[np.float32] = np.array(
                (
                    (f_w, 0.0, width/2),
                    (0.0, f_h, height/2),
                    (0.0, 0.0, 1.0)
                )
            ).astype("float32")
            rot: npt.NDArray[np.float32] = (
                rot_y(float(hz))
                @ rot_x(np.pi / 2 - float(v))
            ).astype("float32")

            warper = cv.PyRotationWarper("spherical", scale)
            corner, image_warped = warper.warp(
                img,
                instrinsics,
                rot,
                cv.INTER_LINEAR,
                cv.BORDER_REPLICATE
            )

            _, mask_warped = warper.warp(
                np.full((height, width), 255, "uint8"),
                instrinsics,
                rot,
                cv.INTER_NEAREST,
                cv.BORDER_CONSTANT
            )
            cx, cy = warper.warpPoint(
                (width / 2, height / 2), instrinsics, rot)

            centers.append(
                (
                    int(cx), int(cy),
                    hz, v
                )
            )
            corners.append(corner)
            images_warped.append(image_warped)
            masks_warped.append(mask_warped)

            # The de-rotation of the camera offset is not completely accurate
            # since the optical axis of the camera might not be parallel to the
            # axis of the telescope (which results in some angle deviation),
            # but it is good enough estimation in case the offset is not
            # precisely known beforehand.
            #
            # The matrix use in the spherical warp cannot be reused here,
            # because OpenCV uses a different axis orientation order.
            offset_rot = rot_z(float(hz)) @ rot_x(np.pi / 2 - float(v))
            cam_offsets.append(
                apply_rotation(pos - center, np.linalg.inv(offset_rot))
            )

    console.print("Merging images... ", end="")

    blender = cv.detail.Blender.createDefault(cv.detail.BLENDER_MULTI_BAND)
    blender.prepare(
        corners,
        [(i.shape[1], i.shape[0]) for i in images_warped]
    )
    for corner, img, msk in zip(corners, images_warped, masks_warped):
        dilated_mask = cv.dilate(msk, None)  # type: ignore[call-overload]
        seam_mask = cv.resize(
            dilated_mask,
            (msk.shape[1], msk.shape[0]),
            None,
            0,
            0,
            cv.INTER_LINEAR_EXACT
        )
        msk_warped = cv.bitwise_and(seam_mask, msk)
        blender.feed(img.astype("int16"), msk_warped, corner)

    result: cvt.MatLike
    result, _ = blender.blend(
        None, None
    )  # type: ignore[call-overload]

    console.print("Done")
    if len(points) > 0:
        console.print("Annotating points... ", end="")

        # Top left image center point for reference
        origin_x, origin_y, _, _ = cv.detail.resultRoi(
            corners,
            [(i.shape[1], i.shape[0]) for i in images_warped]
        )
        tl_x, tl_y, tl_hz, tl_v = centers[0]
        tl_x -= origin_x
        tl_y -= origin_y

        if scale is None:
            scale = 1000

        full_360 = round(scale * np.pi * 2)

        if camera_offset is None:
            camera_offset = mean_coordinate(cam_offsets)

        for pt, coord, label in points:
            # To calculate the approximate "telescope" rotation, a preliminary
            # polar position is needed. Then the camera offset is rotated with
            # the preliminary angles.
            prelim_hz, prelim_v, _ = (coord - center).to_polar()
            offset_rot = (
                rot_z(float(prelim_hz)) @ rot_x(np.pi / 2 - float(prelim_v))
            )
            pt_hz, pt_v, _ = (
                coord
                - (center + apply_rotation(camera_offset, offset_rot))
            ).to_polar()

            pt_hz_f = float(pt_hz - tl_hz)
            pt_v_f = float(pt_v - tl_v)
            pt_x = round(tl_x + pt_hz_f * scale) % full_360
            pt_y = round(tl_y + pt_v_f * scale) % full_360

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

        console.print("Done")

    console.print("Saving final image... ", end="")
    # For some reason the blending function returns the image as int16 instead
    # uint8, and it might contain negative values. These need to be clipped,
    # otherwise the type conversion will result in color artifacts due to the
    # integer underflow.
    result = np.clip(result, 0, 255)
    cv.imwrite(
        str(output),
        result.astype(np.uint8)
    )

    console.print("Done")
    console.print("Panorama complete", style="green")


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


def main(
    metadata: Path,
    output: Path,
    image: tuple[Path],
    camera_offset: tuple[float, float, float] | None = None,
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
        echo_red(
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

    if camera_offset is not None:
        cam_offset = Coordinate(
            camera_offset[0],
            camera_offset[1],
            camera_offset[2]
        )
    else:
        cam_offset = None

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

    try:
        run_annotate(
            meta,
            output,
            image_map,
            scale,
            points,
            cam_offset,
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
        echo_red(f"The process failed due to an OpenCV error ({cve.code})")
