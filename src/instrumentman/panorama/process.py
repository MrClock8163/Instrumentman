from pathlib import Path
import math
from typing import Callable

from PIL import Image, ImageDraw, ImageFont
from geocompy.data import Coordinate, Angle


def read_points(
    path: Path,
    skip: int = 0,
    delimiter: str = ";"
) -> list[tuple[str, Coordinate]]:
    points: list[tuple[str, Coordinate]] = []
    with path.open("rt", encoding="utf8") as file:
        for i in range(skip):
            next(file)

        for line in file:
            pt, x, y, z = line.strip().split(delimiter)
            points.append(
                (
                    pt,
                    Coordinate(
                        float(x),
                        float(y),
                        float(z)
                    )
                )
            )

    return points


def read_metadata(
    path: Path
) -> dict[str, tuple[Angle, Angle, Coordinate, Coordinate]]:
    pictures: dict[str, tuple[Angle, Angle, Coordinate, Coordinate]] = {}
    with path.open("rt", encoding="utf8") as file:
        next(file)
        for line in file:
            (
                img,
                fov_hz,
                fov_v,
                pos_x,
                pos_y,
                pos_z,
                dir_x,
                dir_y,
                dir_z
            ) = line.strip().split(",")

            pictures[img] = (
                Angle.parse(fov_hz),
                Angle.parse(fov_v),
                Coordinate(
                    float(pos_x),
                    float(pos_y),
                    float(pos_z)
                ),
                Coordinate(
                    float(dir_x),
                    float(dir_y),
                    float(dir_z)
                )
            )

    return pictures


def draw_marker_dot(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    markersize: float,
    rgb: tuple[int, int, int]
) -> None:
    draw.circle((x, y), markersize / 2, rgb)
    draw.text(
        (
            x + markersize / 3,
            y + markersize / 3
        ), text, rgb, font, anchor="la"
    )


def draw_marker_cross(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    markersize: float,
    rgb: tuple[int, int, int]
) -> None:
    leg = markersize / 2
    draw.line(
        (
            x - leg, y,
            x + leg, y
        ),
        rgb,
        round(markersize / 10)
    )
    draw.line(
        (
            x, y - leg,
            x, y + leg
        ),
        rgb,
        round(markersize / 10)
    )
    draw.text(
        (
            x + markersize / 4,
            y + markersize / 4
        ), text, rgb, font, anchor="la"
    )


def annotate_image(
    imgpath: Path,
    info: tuple[Angle, Angle, Coordinate, Coordinate],
    points: list[tuple[str, Coordinate]],
    markerdrawer: Callable[[ImageDraw.ImageDraw, float, float, str], None]
) -> None:
    image = Image.open(imgpath)
    draw = ImageDraw.Draw(image)
    fov_hz, fov_v, pos, vec = info
    half_width = image.width / 2
    half_height = image.height / 2
    half_fov_hz = fov_hz / 2
    half_fov_v = fov_v / 2

    img_hz, img_v, _ = (vec - pos).to_polar()

    for pt, coord in points:
        pt_hz, pt_v, _ = (coord - pos).to_polar()
        alpha = pt_hz.relative_to(img_hz)
        beta = pt_v.relative_to(img_v)

        x = round(half_width + math.tan(alpha) *
                  half_width / math.tan(half_fov_hz))
        y = round(half_height + math.tan(beta) *
                  half_height / math.tan(half_fov_v))

        markerdrawer(draw, x, y, pt)

    image.save(
        imgpath.parent.joinpath(
            imgpath.stem + "_annotated" + imgpath.suffix
        )
    )


def run_annotate(
    meta: dict[str, tuple[Angle, Angle, Coordinate, Coordinate]],
    images: tuple[Path],
    points: list[tuple[str, Coordinate]],
    rgb: tuple[int, int, int] = (0, 0, 0),
    fontsize: int = 50,
    marker: str = "cross",
    markersize: int = 50
) -> None:
    font = ImageFont.truetype("arial.ttf", fontsize)
    match marker:
        case "cross":
            markerdrawer = draw_marker_cross
        case "dot":
            markerdrawer = draw_marker_dot

    for path in images:
        info = meta.get(path.stem + path.suffix)
        if info is None:
            continue

        annotate_image(
            path,
            info,
            points,
            lambda draw, x, y, text: markerdrawer(
                draw,
                x,
                y,
                text,
                font,
                markersize,
                rgb
            )
        )


def main(
    metadata: Path,
    image: tuple[Path],
    action: str = "annotate",
    points: Path | None = None,
    skip: int = 0,
    delimiter: str = ",",
    rgb: tuple[int, int, int] = (0, 0, 0),
    fontsize: int = 50,
    marker: str = "cross",
    markersize: int = 50
) -> None:
    meta = read_metadata(metadata)
    match action:
        case "annotate" if points is not None:
            point = read_points(points, skip, delimiter)
            run_annotate(
                meta,
                image,
                point,
                rgb,
                fontsize,
                marker,
                markersize
            )
        case _:
            raise ValueError(f"Unknown action '{action}'")
