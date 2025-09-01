from typing import TypedDict


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
