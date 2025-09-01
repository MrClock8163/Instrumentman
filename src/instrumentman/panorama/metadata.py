from pathlib import Path
from typing import TypedDict, cast
import json


class PanoramaFrameMetadata(TypedDict):
    filename: str
    # grid: tuple[int, int]  # position in grid
    position: tuple[float, float, float]
    vector: tuple[float, float, float]


class PanoramaMetadata(TypedDict):
    grid: tuple[int, int]  # columns, rows
    fov: tuple[float, float]  # horizontal, vertical
    center: tuple[float, float, float]
    images: list[PanoramaFrameMetadata]


def read_metadata(
    path: Path
) -> PanoramaMetadata:
    with path.open("rt", encoding="utf8") as file:
        return cast(PanoramaMetadata, json.load(file))
