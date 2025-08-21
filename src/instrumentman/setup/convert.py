from io import TextIOWrapper
import csv
from typing import cast, Callable

from click_extra import prompt, Choice
from jsonschema import ValidationError
from geocompy.data import Coordinate
from geocompy.geo.gcdata import Prism
from geocompy.gsi.gsiformat import (
    GsiBlock,
    GsiValueType,
    GsiUnit,
    GsiEastingWord,
    GsiNorthingWord,
    GsiHeightWord,
    GsiHorizontalAngleWord,
    GsiVerticalAngleWord,
    GsiSlopeDistanceWord,
    GsiTargetHeightWord,
    write_gsi_blocks_to_file
)

from ..utils import echo_red, echo_yellow, echo_green
from ..targets import (
    TargetList,
    TargetPoint,
    load_targets_from_json,
    export_targets_to_json
)


_PRISMCHOICES = Choice(
    (
        'ROUND',
        'MINI',
        'TAPE',
        'THREESIXTY',
        'USER1',
        'USER2',
        'USER3',
        'MINI360',
        'MINIZERO',
        'NDSTAPE',
        'GRZ121',
        'MPR122'
    )
)


def main_csv_to_targets(
    input: TextIOWrapper,
    output: TextIOWrapper,
    columns: tuple[str],
    skip: int = 0,
    delimiter: str = ",",
    reflector: str | None = None,
    height: float | None = None
) -> None:
    for i in range(skip):
        next(input)

    def get_column_index(
        columns: tuple[str],
        name: str,
        mandatory: bool = False
    ) -> int | None:
        try:
            return columns.index(name)
        except ValueError:
            if mandatory:
                echo_red(f"Mandatory '{name}' column was not specified")
                exit(1)

            return None

    def get_prism(
        pt: str,
        row: list[str],
        idx_prism: int | None,
        reflector: str | None
    ) -> Prism:
        if idx_prism is not None:
            return Prism[row[idx_prism]]

        if reflector is not None:
            return Prism[reflector]

        return Prism[
            prompt(
                f"Reflector type of {pt}",
                type=_PRISMCHOICES
            )
        ]

    def get_height(
        pt: str,
        row: list[str],
        idx_height: int | None,
        height: float | None
    ) -> float:
        if idx_height is not None:
            return float(row[idx_height])

        if height is not None:
            return height

        return cast(
            float,
            prompt(
                f"Target height of {pt}",
                type=float
            )
        )

    targets = TargetList()
    idx_pt = cast(int, get_column_index(columns, "pt"))
    idx_e = cast(int, get_column_index(columns, "e", True))
    idx_n = cast(int, get_column_index(columns, "n", True))
    idx_h = cast(int, get_column_index(columns, "h", True))
    idx_prism = get_column_index(columns, "prism")
    idx_height = get_column_index(columns, "ht")
    for row in csv.reader(input, delimiter=delimiter, lineterminator="\n"):
        name = row[idx_pt]
        east = float(row[idx_e])
        north = float(row[idx_n])
        up = float(row[idx_h])
        prism = get_prism(name, row, idx_prism, reflector)
        ht = get_height(name, row, idx_height, height)
        try:
            targets.add_target(
                TargetPoint(
                    name,
                    prism,
                    ht,
                    Coordinate(east, north, up)
                )
            )
        except ValueError:
            echo_red(f"Duplicate point '{name}' in source files")
            exit(1)

    export_targets_to_json(
        output,
        targets
    )


def main_targets_to_csv(
    input: TextIOWrapper,
    output: TextIOWrapper,
    columns: tuple[str],
    header: bool = True,
    delimiter: str = ",",
    precision: int | None = None
) -> None:
    def make_formatter(
        precision: int | None
    ) -> Callable[[float], str | float]:
        if precision is None:
            return lambda x: x

        fmt = f"{{:.{precision}f}}"
        return lambda x: fmt.format(x)

    try:
        targets = load_targets_from_json(input)
    except ValidationError:
        echo_red("Target definition file is not valid")
        exit(1)

    writer = csv.writer(output, delimiter=delimiter, lineterminator="\n")
    if header:
        writer.writerow(columns)

    formatter = make_formatter(precision)
    for t in targets:
        fields = {
            "pt": t.name,
            "e": formatter(t.coords.e),
            "n": formatter(t.coords.n),
            "h": formatter(t.coords.z),
            "ht": formatter(t.height),
            "prism": t.prism.name
        }
        writer.writerow((fields[c] for c in columns))


def main_gsi_to_targets(
    input: TextIOWrapper,
    output: TextIOWrapper,
    reflector: str | None = None,
    height: float | None = None,
    station: tuple[float, float, float] | None = None,
    instrumentheight: float | None = None
) -> None:
    targets = TargetList()
    station_coords: Coordinate | None = None
    if station is not None and instrumentheight is not None:
        x, y, z = station
        station_coords = Coordinate(
            x,
            y,
            z + instrumentheight
        )

    ht: float = 0.0
    prism: Prism = Prism.MINI
    for i, line in enumerate(input):
        if not line.strip():
            continue

        try:
            block = GsiBlock.parse(line.strip("\n"), keep_unknowns=False)
        except Exception:
            echo_yellow(f"Could not parse line {i + 1}")
            continue

        if block.blocktype != "measurement":
            continue

        point = block.value

        eastingword = block.get_word(GsiEastingWord)
        northingword = block.get_word(GsiNorthingWord)
        heightword = block.get_word(GsiHeightWord)
        if (
            eastingword is not None
            and northingword is not None
            and heightword is not None
        ):
            coord = Coordinate(
                eastingword.value,
                northingword.value,
                heightword.value
            )
            polar = False
        elif station_coords is not None:
            hzword = block.get_word(GsiHorizontalAngleWord)
            vword = block.get_word(GsiVerticalAngleWord)
            sword = block.get_word(GsiSlopeDistanceWord)

            if (
                hzword is not None
                and vword is not None
                and sword is not None
            ):
                coord = Coordinate.from_polar(
                    hzword.value,
                    vword.value,
                    sword.value
                ) + station_coords
                polar = True
            else:
                continue
        else:
            continue

        htword = block.get_word(GsiTargetHeightWord)
        if htword is not None:
            ht = htword.value
        elif height is not None:
            ht = height
        else:
            ht = prompt(
                f"Target height of {point}",
                type=float,
                default=ht
            )

        if polar:
            coord = coord - Coordinate(0, 0, ht)

        if reflector is not None:
            prism = Prism[reflector]
        else:
            answer: str = prompt(
                f"Reflector type of {point}",
                type=_PRISMCHOICES,
                default=prism.name
            )
            prism = Prism[answer]

        targets.add_target(
            TargetPoint(
                point,
                prism,
                ht,
                coord
            )
        )

    if len(targets) == 0:
        echo_red("Could not import any targets")
        exit(1)

    export_targets_to_json(output, targets)
    echo_green(f"Imported {len(targets)} target(s)")


_UNIT_MAPPING = {
    "mm": GsiUnit.MILLI,
    "mft": GsiUnit.MILLIFEET,
    "dmm": GsiUnit.DECIMILLI,
    "dmft": GsiUnit.DECIMILLIFEET,
    "cmm": GsiUnit.CENTIMILLI
}


def main_targets_to_gsi(
    input: TextIOWrapper,
    output: TextIOWrapper,
    gsi16: bool = False,
    length_unit: str = "dmm"
) -> None:
    try:
        targets = load_targets_from_json(input)
    except ValidationError:
        echo_red("Target definition file is not valid")
        exit(1)

    unit = _UNIT_MAPPING[length_unit]

    blocks: list[GsiBlock] = []
    for t in targets:
        blocks.append(
            GsiBlock(
                t.name,
                "measurement",
                GsiEastingWord(
                    t.coords.e,
                    GsiValueType.TYPE1
                ),
                GsiNorthingWord(
                    t.coords.n,
                    GsiValueType.TYPE1
                ),
                GsiHeightWord(
                    t.coords.h,
                    GsiValueType.TYPE1
                )
            )
        )

    write_gsi_blocks_to_file(
        blocks,
        output,
        gsi16,
        distunit=unit,
        address=1
    )
