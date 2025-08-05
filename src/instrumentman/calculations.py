import math
from typing import Sequence

import numpy as np
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


def _matrices_resection_horizontal(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    station: Coordinate,
    orientation: Angle
) -> tuple[list[list[float]], list[float]]:
    design_matrix: list[list[float]] = []
    observation_vector: list[float] = []

    for (hz, v, d), coord in zip(measurements, targets):
        dr0 = coord - station
        dx0, dy0, dz0 = dr0
        hz0, v0, dsd0 = dr0.to_polar()
        dhd0 = dr0.to_2d().length()

        hz_o = (hz + orientation).normalized()
        design_matrix.append(
            [
                -1,
                -dx0 / dhd0**2,
                dy0 / dhd0**2
            ]
        )
        design_matrix.append(
            [
                0,
                -dx0 / dhd0,
                -dy0 / dhd0
            ]
        )
        observation_vector.extend(
            [
                float(hz0.relative_to(hz_o)),
                dhd0 - math.sin(v) * d
            ]
        )

    return design_matrix, observation_vector


def _matrices_resection_vertical(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    station: Coordinate
) -> tuple[list[list[float]], list[float]]:
    design_matrix: list[list[float]] = []
    observation_vector: list[float] = []

    for (_, v, d), coord in zip(measurements, targets):
        dr0 = coord - station

        design_matrix.append(
            [
                -1
            ]
        )
        observation_vector.extend(
            [
                dr0.z - d * math.cos(v)
            ]
        )

    return design_matrix, observation_vector


def _weights_resection_horizontal(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    *,
    accuracy_hz: float = 1,
    accuracy_v: float = 1,
    accuracy_d: tuple[float, float] = (1, 1.5)
) -> np.ndarray:
    weights: list[float] = []

    accuracy_sd, accuracy_sd_ppm = accuracy_d
    for _, v, sd in measurements:
        weights.extend(
            (
                1 / accuracy_hz**2,
                1 / (
                    (
                        (
                            accuracy_sd
                            + accuracy_sd_ppm * sd / 1000
                        ) * math.sin(v)
                    )**2
                    + (
                        sd * math.cos(v) * accuracy_v
                    )**2
                )
            )
        )

    return np.diag(weights)


def _weights_resection_vertical(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    *,
    accuracy_v: float = 1
) -> np.ndarray:
    weights: list[float] = []

    accuracy_v_rad = math.radians(accuracy_v / 3600)
    for _, v, sd in measurements:
        hd = math.sin(v) * sd
        if hd < 30:
            hd = 30
        weights.append(
            1 / (
                (hd * 5e-5)**2
                + (
                    hd * accuracy_v_rad
                )**2
            )
        )

    return np.diag(weights)


def _iter_resection_horizontal(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    station: Coordinate,
    orientation: Angle,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    design_float, obs_float = _matrices_resection_horizontal(
        measurements,
        targets,
        station,
        orientation
    )

    design = np.array(design_float)
    obs = np.array(obs_float)

    norm = design.T @ weights @ design
    norminv = np.linalg.pinv(norm)

    x = -norminv @ design.T @ weights @ obs

    v = design @ x - obs
    m0 = np.sqrt(v.T @ weights @  v / (len(measurements) * 2 - 3))
    m = m0 * np.sqrt(np.diag(norminv))

    return x, m


def _iter_resection_vertical(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    station: Coordinate,
    weights: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    design_float, obs_float = _matrices_resection_vertical(
        measurements,
        targets,
        station
    )

    design = np.array(design_float)
    obs = np.array(obs_float)

    norm = design.T @ weights @ design
    norminv = np.linalg.pinv(norm)

    x = -norminv @ design.T @ weights @ obs

    v = design @ x - obs
    m0 = np.sqrt(v.T @ weights @  v / (len(measurements) - 1))
    m = m0 * np.sqrt(np.diag(norminv))

    return x, m


def resection_horizontal(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    preliminary_station: Coordinate,
    *,
    x_tolerance: float = 5e-4,
    y_tolerance: float = 5e-4,
    orientation_tolerance: Angle = Angle(1 / 3600, "deg"),
    max_iterations: int = 20,
    uniform_weights: bool = False,
    accuracy_hz: float = 1,
    accuracy_v: float = 1,
    accuracy_d: tuple[float, float] = (1, 1.5)
) -> tuple[bool, Angle, Angle, Coordinate, Coordinate]:
    if len(measurements) != len(targets) or len(targets) < 2:
        raise ValueError("Cannot calculate resection with less than 2 targets")

    station = preliminary_station
    delta_st0, _, _ = (targets[0] - station).to_polar()
    orientation = (delta_st0 - measurements[0][0]).normalized()

    o_tolerance = float(orientation_tolerance)

    if uniform_weights:
        weights = np.eye(len(measurements) * 2)
    else:
        weights = _weights_resection_horizontal(
            measurements,
            targets,
            accuracy_hz=accuracy_hz,
            accuracy_v=accuracy_v,
            accuracy_d=accuracy_d
        )

    stdev_orientation = Angle(0)
    stdev_station = Coordinate(0, 0, 0)
    corr_o = corr_x = corr_y = np.inf
    iterations = 0
    while (
        abs(corr_o) > o_tolerance
        or abs(corr_x) > x_tolerance
        or abs(corr_y) > y_tolerance
    ):
        if iterations >= max_iterations:
            return (
                False, orientation, stdev_orientation, station, stdev_station
            )

        x, m = _iter_resection_horizontal(
            measurements,
            targets,
            station,
            orientation,
            weights
        )

        corr_o, corr_x, corr_y = x

        orientation = (orientation + Angle(corr_o)).normalized()
        station = station + Coordinate(corr_x, corr_y, 0)
        # seemingly should be deg, but not sure
        stdev_orientation = Angle(m[0])
        stdev_station = Coordinate(m[1], m[2], 0)

        iterations += 1

    return True, orientation, stdev_orientation, station, stdev_station


def resection_vertical(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    preliminary_station: Coordinate,
    *,
    uniform_weights: bool = False,
    accuracy_v: float = 1
) -> tuple[Coordinate, Coordinate]:
    if uniform_weights:
        weights = np.eye(len(measurements))
    else:
        weights = _weights_resection_vertical(
            measurements,
            targets,
            accuracy_v=accuracy_v
        )

    x, m = _iter_resection_vertical(
        measurements,
        targets,
        preliminary_station,
        weights
    )

    return preliminary_station + Coordinate(0, 0, x[0]), Coordinate(0, 0, m[0])


def resection_2d_1d(
    measurements: list[tuple[Angle, Angle, float]],
    targets: list[Coordinate],
    preliminary_station: Coordinate,
    *,
    x_tolerance: float = 5e-4,
    y_tolerance: float = 5e-4,
    orientation_tolerance: Angle = Angle(1 / 3600, "deg"),
    max_iterations: int = 20,
    uniform_weights: bool = False,
    accuracy_hz: float = 1,
    accuracy_v: float = 1,
    accuracy_d: tuple[float, float] = (1, 1.5)
) -> tuple[bool, Angle, Angle, Coordinate, Coordinate]:
    (
        converged,
        orientation,
        stdev_orientation,
        station,
        stdev_station_hz
    ) = resection_horizontal(
        measurements,
        targets,
        preliminary_station,
        x_tolerance=x_tolerance,
        y_tolerance=y_tolerance,
        orientation_tolerance=orientation_tolerance,
        max_iterations=max_iterations,
        accuracy_hz=accuracy_hz,
        accuracy_v=accuracy_v,
        accuracy_d=accuracy_d,
        uniform_weights=uniform_weights
    )

    station, stdev_station_v = resection_vertical(
        measurements,
        targets,
        station,
        uniform_weights=uniform_weights,
        accuracy_v=accuracy_v
    )

    return (
        converged,
        orientation,
        stdev_orientation,
        station,
        stdev_station_hz + stdev_station_v
    )
