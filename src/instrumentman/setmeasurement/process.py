import os
import json
import math
from typing import Sequence
import pathlib
from io import TextIOWrapper

from jmespath import search
from jsonschema import validate, ValidationError
from geocompy.data import Angle, Coordinate
from geocompy.gsi.gsiformat import (
    GsiBlock,
    GsiUnit,
    GsiValueType,
    GsiEastingWord,
    GsiNorthingWord,
    GsiHeightWord,
    GsiHorizontalAngleWord,
    GsiVerticalAngleWord,
    GsiSlopeDistanceWord,
    GsiTargetHeightWord,
    GsiInfo1Word,
    GsiInstrumentHeightWord,
    write_gsi_blocks_to_file
)

from .sessions import SessionDict
from ..utils import (
    echo_red,
    echo_green,
    echo_yellow,
    make_directory
)


class SessionValidator:
    def __init__(
        self,
        twoface: bool
    ) -> None:
        self._twoface = twoface
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "schema_session.json"
            ),
            "rt",
            encoding="utf8"
        ) as file_schema:
            self._schema = json.load(file_schema)

    def validate(self, data: SessionDict) -> None:
        validate(data, self._schema)

        ptids = search("cycles[*].points[*].name", data)
        if len(ptids) == 0:
            return

        first = ptids[0]
        for ids in ptids[1:]:
            if ids != first:
                raise ValueError("Mismatching points between cycles")

        if not self._twoface:
            return

        for i, c in enumerate(data["cycles"]):
            for p in c["points"]:
                if p.get("face2") is None:
                    raise ValueError(
                        f"Point {p['name']} is missing face 2 "
                        f"measurements in cycle {i + 1}"
                    )

    def validate_for_merge(self, data: Sequence[SessionDict]) -> None:
        for s in data:
            validate(s, self._schema)


def calc_angles(
    hz_f1: Angle,
    v_f1: Angle,
    hz_f2: Angle,
    v_f2: Angle
) -> tuple[Angle, Angle, Angle, Angle]:
    temp = hz_f2 - hz_f1
    if temp < 0:
        collim = (temp + Angle(180, 'deg')) / 2
    else:
        collim = (temp - Angle(180, 'deg')) / 2

    hz = hz_f1 + collim

    index = (Angle(360, 'deg') - v_f1 - v_f2) / 2
    v = v_f1 + index

    return hz, v, collim, index


def calc_coords(
    coords: list[Coordinate]
) -> tuple[Coordinate, Coordinate]:
    def adjust(values: list[float]) -> tuple[float, float]:
        n = len(values)
        adjusted = math.fsum(values) / n
        dev = math.sqrt(math.fsum([(v - adjusted)**2 for v in values]) / n)
        return adjusted, dev

    xi = [c.x for c in coords]
    yi = [c.y for c in coords]
    zi = [c.z for c in coords]

    x, x_dev = adjust(xi)
    y, y_dev = adjust(yi)
    z, z_dev = adjust(zi)

    return Coordinate(x, y, z), Coordinate(x_dev, y_dev, z_dev)


def main_merge(
    output: pathlib.Path,
    inputs: tuple[pathlib.Path],
    allow_oneface: bool = False
) -> None:
    sessions: list[SessionDict] = []
    for path in inputs:
        with path.open("rt", encoding="utf8") as file:
            sessions.append(json.load(file))

    validator = SessionValidator(not allow_oneface)
    try:
        validator.validate_for_merge(sessions)
    except ValidationError as ve:
        echo_red("One of the input files does not follow the required schema")
        echo_red(ve)
        exit(4)

    if len(sessions) == 0:
        echo_yellow("There were no sessions found to merge")
        exit(0)

    session: SessionDict = {
        "station": sessions[0]["station"],
        "instrumentheight": sessions[0]["instrumentheight"],
        "cycles": [c for s in sessions for c in s["cycles"]]
    }

    try:
        validator.validate(session)
    except ValidationError as ve:
        echo_red("The merging process caused a schema error")
        echo_red(ve)
        exit(4)
    except ValueError as e:
        echo_red(f"The merged output could not be validated ({e})")
        exit(4)

    make_directory(str(output))
    with open(output, "wt", encoding="utf8") as file:
        json.dump(
            session,
            file,
            indent=4
        )

    echo_green(
        f"Merged {len(session['cycles'])} cycles "
        f"from {len(sessions)} sessions"
    )


def main_validate(
    inputs: tuple[pathlib.Path],
    schema_only: bool = False,
    allow_oneface: bool = False
) -> None:
    sessions: list[SessionDict] = []
    for path in inputs:
        with path.open("rt", encoding="utf8") as file:
            sessions.append(json.load(file))

    validator = SessionValidator(not allow_oneface)
    if schema_only:
        try:
            validator.validate_for_merge(sessions)
            echo_green("Schema validation succeeded")
            exit(0)
        except ValidationError as ve:
            echo_red(
                "One of the input files does not follow the required schema"
            )
            echo_red(ve)
            exit(4)

    try:
        for s in sessions:
            validator.validate(s)

        echo_green("Validation succeeded")
        exit(0)
    except ValidationError as ve:
        echo_red(
            "One of the input files does not follow the required schema"
        )
        echo_red(ve)
        exit(4)
    except ValueError as e:
        echo_red(f"The merged output could not be validated ({e})")
        exit(4)


def main_calc(
    input: pathlib.Path,
    output: pathlib.Path,
    header: bool = False,
    delimiter: str = ",",
    precision: int = 4,
    allow_oneface: bool = False,
    station: tuple[float, float, float] | None = None,
    instrumentheight: float | None = None,
    orientation: str | None = None
) -> None:
    with input.open("rt", encoding="utf8") as file:
        data: SessionDict = json.load(file)

    validator = SessionValidator(not allow_oneface)
    try:
        validator.validate(data)
    except ValidationError as ve:
        echo_red("Input data does not follow the required schema")
        echo_red(ve)
        exit(4)
    except ValueError as e:
        echo_red("The input data did not pass validation")
        echo_red(e)
        exit(4)

    points = {"points": search("cycles[].points[]", data)}
    ptids = list(set(search("points[].name", points)))

    if station is None or instrumentheight is None:
        stn = Coordinate(
            *data["station"]
        ) + Coordinate(
            0,
            0,
            data["instrumentheight"]
        )
    else:
        stn = Coordinate(
            station[0],
            station[1],
            station[2] + instrumentheight
        )

    if orientation is None:
        ori = Angle(0)
    else:
        ori = Angle.from_dms(orientation)

    coords: dict[str, list[Coordinate]] = {}
    for pt in ptids:
        measurements = search(
            f"points[?name=='{pt}'].[height, face1, face2]",
            points
        )
        if pt not in coords:
            coords[pt] = []
        for cycle in measurements:
            height = cycle[0]
            hz = Angle(cycle[1][0])
            v = Angle(cycle[1][1])
            d = cycle[1][2]

            if cycle[2] is not None:
                hz_f2 = Angle(cycle[2][0])
                v_f2 = Angle(cycle[2][1])
                d_f2 = cycle[2][2]

                hz, v, co, z = calc_angles(
                    hz,
                    v,
                    hz_f2,
                    v_f2
                )

                d = (d + d_f2) / 2
            elif not allow_oneface:
                echo_red("Not all measurements have data for both faces")
                exit(4)

            c = stn + Coordinate.from_polar(
                (hz + ori).normalized(),
                v,
                d
            ) - Coordinate(
                0,
                0,
                height
            )
            coords[pt].append(c)

    final: list[tuple[str, Coordinate, Coordinate]] = []
    for name, coo in coords.items():
        coord, dev = calc_coords(coo)
        final.append((name, coord, dev))

    with output.open("wt", encoding="utf8") as file:
        if header:
            file.write(
                delimiter.join(
                    ["id", "e", "n", "h", "sigma_e", "sigma_n", "sigma_h"]
                ) + "\n"
            )

        fmt = "{0:." + str(precision) + "f}"
        for name, coord, dev in final:
            fields = [
                name,
                fmt.format(coord.x),
                fmt.format(coord.y),
                fmt.format(coord.z),
                fmt.format(dev.x),
                fmt.format(dev.y),
                fmt.format(dev.z)
            ]
            file.write(
                delimiter.join(fields) + "\n"
            )


_UNIT_MAPPING = {
    "mm": GsiUnit.MILLI,
    "mft": GsiUnit.MILLIFEET,
    "dmm": GsiUnit.DECIMILLI,
    "dmft": GsiUnit.DECIMILLIFEET,
    "cmm": GsiUnit.CENTIMILLI,
    "deg": GsiUnit.DEG,
    "gon": GsiUnit.GON,
    "dms": GsiUnit.DMS,
    "mil": GsiUnit.MIL
}


def main_convert_set_to_gsi(
    input: TextIOWrapper,
    output: TextIOWrapper,
    gsi16: bool = False,
    length_unit: str = "dmm",
    angle_unit: str = "deg"
) -> None:
    data: SessionDict = json.load(input)

    angleunit = _UNIT_MAPPING[angle_unit]
    distunit = _UNIT_MAPPING[length_unit]

    validator = SessionValidator(False)
    try:
        validator.validate(data)
    except ValidationError as ve:
        echo_red("Input data does not follow the required schema")
        echo_red(ve)
        exit(4)
    except ValueError as e:
        echo_red("The input data did not pass validation")
        echo_red(e)
        exit(4)

    stn_e, stn_n, stn_h = data["station"]
    blocks: list[GsiBlock] = []
    blocks.append(
        GsiBlock(
            "STN",
            "measurement",
            GsiEastingWord(
                stn_e,
                GsiValueType.TYPE1
            ),
            GsiNorthingWord(
                stn_n,
                GsiValueType.TYPE1
            ),
            GsiHeightWord(
                stn_h,
                GsiValueType.TYPE1
            )
        )
    )

    blocks.append(
        GsiBlock(
            "2",
            "code",
            GsiInfo1Word("STN"),
            GsiInstrumentHeightWord(
                data["instrumentheight"],
                GsiValueType.TYPE1,
            )
        )
    )

    for cycle in data["cycles"]:
        for point in cycle["points"]:
            blocks.append(
                GsiBlock(
                    point["name"],
                    "measurement",
                    GsiHorizontalAngleWord(
                        Angle(point["face1"][0]),
                        inputtype=GsiValueType.TYPE0
                    ),
                    GsiVerticalAngleWord(
                        Angle(point["face1"][1]),
                        inputtype=GsiValueType.TYPE0
                    ),
                    GsiSlopeDistanceWord(
                        point["face1"][2],
                        inputtype=GsiValueType.TYPE0
                    ),
                    GsiTargetHeightWord(point["height"])
                )
            )

            face2 = point.get("face2")
            if face2 is None:
                continue

            blocks.append(
                GsiBlock(
                    point["name"],
                    "measurement",
                    GsiHorizontalAngleWord(
                        Angle(face2[0]),
                        inputtype=GsiValueType.TYPE0
                    ),
                    GsiVerticalAngleWord(
                        Angle(face2[1]),
                        inputtype=GsiValueType.TYPE0
                    ),
                    GsiSlopeDistanceWord(
                        face2[2],
                        inputtype=GsiValueType.TYPE0
                    ),
                    GsiTargetHeightWord(point["height"])
                )
            )

    write_gsi_blocks_to_file(
        blocks,
        output,
        gsi16,
        angleunit,
        distunit,
        1
    )
