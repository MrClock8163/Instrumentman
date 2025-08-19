from io import TextIOWrapper
import csv
from typing import cast, Callable

from click_extra import prompt, Choice
from jsonschema import ValidationError
from geocompy.data import Coordinate
from geocompy.geo.gcdata import Prism

from ..utils import echo_red
from ..targets import (
    TargetList,
    TargetPoint,
    load_targets_from_json,
    export_targets_to_json
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
                type=Choice(
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
    idx_z = cast(int, get_column_index(columns, "z", True))
    idx_prism = get_column_index(columns, "prism")
    idx_height = get_column_index(columns, "ht")
    for row in csv.reader(input, delimiter=delimiter, lineterminator="\n"):
        name = row[idx_pt]
        east = float(row[idx_e])
        north = float(row[idx_n])
        up = float(row[idx_z])
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
            "z": formatter(t.coords.z),
            "ht": formatter(t.height),
            "prism": t.prism.name
        }
        writer.writerow((fields[c] for c in columns))
