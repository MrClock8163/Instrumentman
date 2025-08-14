from pathlib import Path
import json

from jsonschema import ValidationError
from geocompy.data import Angle, Coordinate

from ..targets import load_targets_from_json
from ..setmeasurement.sessions import SessionDict
from ..setmeasurement.process import (
    SessionValidator,
    calc_angles
)
from ..utils import echo_red
from ..calculations import resection_2d_1d, preliminary_resection


def main(
    measurements: Path,
    targets: Path,
    output: Path,
    points: tuple[str, ...] = (),
    height: float = 0
) -> None:
    with measurements.open("rt", encoding="utf8") as file:
        data: SessionDict = json.load(file)

    validator = SessionValidator(False)
    try:
        validator.validate(data)
    except ValidationError as ve:
        echo_red("Measurement data does not follow the required schema")
        echo_red(ve)
        exit(4)
    except ValueError as e:
        echo_red("The Measurement data did not pass validation")
        echo_red(e)
        exit(4)

    try:
        targetlist = load_targets_from_json(str(targets))
    except ValidationError:
        echo_red("Target data does not follow the required schema")
        exit(4)

    target_names = targetlist.get_target_names()
    if len(points) > 0:
        target_names = list(set(target_names).intersection(points))

    actual_targets: list[str] = []
    references: list[Coordinate] = []
    obs: list[tuple[Angle, Angle, float]] = []
    for cycle in data["cycles"]:
        for p in cycle["points"]:
            name = p["name"]
            if name not in target_names:
                continue

            actual_targets.append(name)

            t = targetlist.get_target(name)
            coord = t.coords
            coord.z += t.height
            references.append(coord)
            hz = Angle(p["face1"][0])
            v = Angle(p["face1"][1])
            d = p["face1"][2]
            if p.get("face2") is not None:
                hz, v, _, _ = calc_angles(
                    hz,
                    v,
                    Angle(p["face2"][0]),
                    Angle(p["face2"][1])
                )
                d = (d + p["face2"][2]) / 2

            obs.append(
                (hz, v, d)
            )

    if len(set(actual_targets)) < 2:
        echo_red("Cannot calculate resection from less than 2 targets")
        exit(1)

    (
        converged,
        orientation,
        stdev_orientation,
        station,
        stdev_station
    ) = resection_2d_1d(
        obs,
        references,
        preliminary_resection(
            obs,
            references
        )
    )

    if not converged:
        echo_red("Resection calculation failed")
        exit(1)

    results = {
        "station": list(station - Coordinate(0, 0, height)),
        "stddev_station": list(stdev_station),
        "instrumentheight": height,
        "orientation": orientation.to_dms(4),
        "stddev_orientation": stdev_orientation.to_dms(4)
    }
    with output.open("wt", encoding="utf8") as file:
        json.dump(results, file, indent=4)
