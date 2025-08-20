import os
from logging import Logger, getLogger

from click_extra import (
    Choice,
    prompt,
    pause,
    confirm,
    echo
)
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gcdata import Prism
from geocompy.geo.gctypes import GeoComCode

from ..utils import (
    echo_red,
    echo_green,
    echo_yellow
)
from ..targets import (
    TargetList,
    TargetPoint,
    load_targets_from_json,
    export_targets_to_json
)


def measure_targets(
    tps: GeoCom,
    logger: Logger,
    filepath: str
) -> TargetList | None:
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

    logger.info("Starting target measurements")
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
        logger.info(f"Recording {ptid}")
        resp_target = tps.bap.get_prism_type()
        if resp_target.params is None:
            echo_yellow("Could not retrieve target type.")
            logger.error(
                f"Could not retrieve target type, skipping ({resp_target})"
            )
            continue

        target = resp_target.params

        user_target: str = prompt(
            "Prism type",
            default=target.name,
            type=Choice([e.name for e in Prism if e.name != 'USER'])
        )
        if target != Prism[user_target]:
            resp_settarget = tps.bap.set_prism_type(user_target)
            if resp_settarget.error != GeoComCode.OK:
                echo_yellow("Could not update prism type")
                logger.error(
                    f"Could not update prism type, skipping ({resp_settarget})"
                )
                continue
            else:
                echo(f"Updated prism type to {user_target}")
                logger.info(
                    f"Updated prism type to {user_target} from user input"
                )
        target = Prism[user_target]

        if target == Prism.USER:
            echo_yellow(
                "User defined prisms are currently not supported."
            )
            logger.error(
                "User defined prisms are currently not supported, skipping"
            )
            continue

        resp_height = tps.tmc.get_target_height()
        height = resp_height.params
        if height is None:
            echo_yellow("Could not retrieve target height.")
            logger.error(
                f"Could not retrieve target height, skipping ({resp_height})"
            )
            continue

        user_height: float = prompt(
            "Target height",
            default=f"{resp_height.params:.4f}",
            type=float
        )
        resp_setheight = tps.tmc.set_target_height(user_height)
        if resp_setheight.error != GeoComCode.OK:
            echo_yellow("Could not update target height")
            logger.error(
                f"Could not update target height, skipping ({resp_setheight})"
            )
            continue
        else:
            echo(f"Updated target height to {user_height:.4f}")
            logger.info(
                f"Updated target height to {user_height:.4f} from user input"
            )

        pause("Aim at target, then press any key...")

        tps.aut.fine_adjust(0.5, 0.5)
        tps.tmc.do_measurement()
        resp = tps.tmc.get_simple_coordinate(10)
        if resp.params is None:
            echo_yellow("Could not measure target")
            logger.error("Could not measure target, skipping")
            continue

        points.add_target(
            TargetPoint(
                ptid,
                target,
                height,
                resp.params
            )
        )

        echo_green(f"{ptid} recorded")
        logger.info(f"{ptid} recorded")
        if not confirm("Record more targets?", default=True):
            break

    echo_green("Target measurement finished")
    logger.info("Target measurement finished")

    return points


def main_measure(
    port: str,
    output: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False
) -> None:
    logger = getLogger("iman.targets.measure")
    with open_serial(
        port,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger.getChild("instrument"))
        targets = measure_targets(tps, logger, output)
        if targets is None:
            echo_red("Program was cancelled or no targets were recorded")
            logger.info("Program was cancelled or no targets were recorded")
            exit(0)

    if targets is not None:
        export_targets_to_json(output, targets)
        echo_green(f"Saved target results to '{output}'")
        logger.info(f"Saved target results to '{output}'")
