import math
from typing import Sequence

from geocompy.data import Angle, Coordinate


def adjust_uniform_single(values: list[float]) -> tuple[float, float]:
    n = len(values)
    adjusted = math.fsum(values) / n
    dev = math.sqrt(math.fsum([(v - adjusted)**2 for v in values]) / n)
    return adjusted, dev


def preliminary_resection(
    measurements: Sequence[tuple[Angle, Angle, float]],
    targets: Sequence[Coordinate]
) -> Coordinate:
    """
    Calculates a preliminary resection station for the adjustment calculations.

    The calculation is done from the first two measurements, using
    distance intersection from the first two targets to find the horizontal
    coordinates. The vertical coordinate is calculated as trigonometric
    height from the first target.

    Parameters
    ----------
    measurements : Sequence[tuple[Angle, Angle, float]]
        Measurements to target points.
    targets : Sequence[Coordinate]
        Target point coordinates.

    Returns
    -------
    Coordinate
        Preliminary station.
    """
    hzs1, vs1, ds1 = measurements[0]
    hzs2, vs2, ds2 = measurements[1]
    t1_3d = targets[0]
    t2_3d = targets[1]

    t1 = t1_3d.to_2d()
    t2 = t2_3d.to_2d()

    hz12, _, d12 = (t2 - t1).to_polar()

    r1 = math.sin(vs1) * ds1
    r2 = math.sin(vs2) * ds2

    alpha = Angle(math.acos((r1**2 + d12**2 - r2**2) / (2 * r1 * d12)))
    if (hzs2 - hzs1).normalized() > Angle(180, 'deg'):
        alpha = -alpha

    return t1_3d + Coordinate.from_polar(
        hz12 + alpha,
        Angle(180, "deg") - vs1,
        ds1
    )
