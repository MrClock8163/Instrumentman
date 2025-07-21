import os

from click_extra import (
    Choice,
    prompt,
    confirm,
    echo
)
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gcdata import Prism

from ..utils import (
    echo_red,
    echo_green,
    echo_yellow
)
from ..targets import (
    TargetList,
    TargetPoint,
    load_targets_from_json,
    export_targets_to_json,
    import_targets_from_csv
)


def measure_targets(tps: GeoCom, filepath: str) -> TargetList | None:
    if os.path.exists(filepath):
        action: str = prompt(
            f"{filepath} already exists. Action",
            default="replace",
            type=Choice(["cancel", "replace", "append"])
        )
        match action:
            case "cancel":
                exit(0)
            case "append":
                points = load_targets_from_json(filepath)
                echo(f"Loaded targets: {points.get_target_names()}")
            case _:
                points = TargetList()
    else:
        points = TargetList()

    ptid: str
    while ptid := prompt("Point ID (or nothing to finish)", type=str):
        if ptid in points:
            remove = confirm(
                f"{ptid} already exists. Overwrite?"
            )
            if remove:
                points.pop_target(ptid)
            else:
                continue

        resp_target = tps.bap.get_prism_type()
        if resp_target.params is None:
            echo_yellow("Could not retrieve target type.")
            continue

        target = resp_target.params
        if target == Prism.USER:
            echo_yellow(
                "User defined prism types are currently not supported."
            )
            continue

        user_target: str = prompt(
            "Prism type",
            default=target.name,
            type=Choice([e.name for e in Prism if e.name != 'USER'])
        )
        target = Prism[user_target]

        resp_height = tps.tmc.get_target_height()
        if resp_height.params is None:
            echo_yellow("Could not retrieve target height.")
            continue

        height: float = prompt(
            "Target height",
            default=f"{resp_height.params:.4f}",
            type=float
        )

        prompt("Aim at target, then press ENTER...", prompt_suffix="")

        tps.aut.fine_adjust(0.5, 0.5)
        tps.tmc.do_measurement()
        resp = tps.tmc.get_simple_coordinate(10)
        if resp.params is None:
            echo_yellow("Could not measure target.")
            continue

        points.add_target(
            TargetPoint(
                ptid,
                target,
                height,
                resp.params
            )
        )

        echo(f"{ptid} stored")
        if not confirm("Record more targets?", default=True):
            break

    echo_green("Set measurement setup finished")

    return points


def main_measure(
    port: str,
    output: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False
) -> None:

    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout
    ) as com:
        tps = GeoCom(com)
        targets = measure_targets(tps, output)
        if targets is None:
            echo_red("Setup was cancelled or no targets were recorded.")
            exit(0)

    export_targets_to_json(output, targets)
    echo_green(f"Saved setup results at '{output}'")


def main_import(
    reflector: str,
    input: str,
    output: str,
    delimiter: str = ",",
    columns: str = "PENZ",
    skip: int = 0
) -> None:

    if os.path.exists(output):
        action: str = prompt(
            f"{output} already exists. Action",
            type=Choice(["cancel", "replace", "append"]),
            default="cancel"
        )
        match action:
            case "cancel":
                exit(0)
            case "append":
                points = load_targets_from_json(output)
                echo(
                    f"Loaded targets: {', '.join(points.get_target_names())}"
                )
            case _:
                points = TargetList()
    else:
        points = TargetList()

    try:
        imported_points = import_targets_from_csv(
            input,
            delimiter,
            columns,
            Prism[reflector],
            skip
        )
    except FileNotFoundError as fe:
        echo_red("Could not find CSV file (file does not exist)")
        echo_red(fe)
        exit(1103)
    except OSError as oe:
        echo_red(
            "Cannot import CSV data due to a file operation error "
            "(no access or other error)"
        )
        echo_red(oe)
        exit(1102)
    except Exception as e:
        echo_red(
            "Cannot import CSV data due to an error "
            "(duplicated points, the header was not skipped, malformed data "
            "or incorrect column spec)"
        )
        echo_red(e)
        exit(1100)

    conflicts = set(
        points.get_target_names()
    ).intersection(imported_points.get_target_names())

    if len(conflicts) > 0:
        echo(f"Duplicates: {', '.join(sorted(list(conflicts)))}")
        echo_red("Found duplicate targets between CSV and existing JSON")
        exit(1101)

    echo(f"Imported targets: {', '.join(imported_points.get_target_names())}",)

    for t in imported_points:
        points.add_target(t)

    export_targets_to_json(output, points)
    echo_green(f"Saved import results at '{os.path.abspath(output)}'")
