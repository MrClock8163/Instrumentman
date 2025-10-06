from pathlib import Path
from typing import TypedDict, cast
import json
import os

from jsonschema import validate


class PanoramaFrameMetadata(TypedDict):
    filename: str
    # grid: tuple[int, int]  # position in grid
    position: tuple[float, float, float]
    vector: tuple[float, float, float]


class PanoramaMetadata(TypedDict):
    center: tuple[float, float, float]
    focal: float
    principal: tuple[float, float]
    camera_offset: tuple[float, float, float]
    camera_deviation: tuple[float, float, float]
    images: list[PanoramaFrameMetadata]


def read_metadata(
    path: Path
) -> PanoramaMetadata:
    with path.open("rt", encoding="utf8") as file:
        data = json.load(file)

    with open(
        os.path.join(
            os.path.dirname(__file__),
            "schema_metadata.json"
        ),
        "rt",
        encoding="utf8"
    ) as file_schema:
        schema = json.load(file_schema)

    validate(data, schema)

    return cast(PanoramaMetadata, data)
