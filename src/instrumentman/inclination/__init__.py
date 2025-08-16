from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    IntRange,
    File
)

from ..utils import (
    com_option_group,
    com_port_argument
)


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
@option(
    "-o",
    "--output",
    help="File to save output to",
    type=File("wt", encoding="utf8", lazy=True)
)
@option(
    "-p",
    "--positions",
    help="Number of positions to measure around the circle",
    type=IntRange(1, 12),
    default=1
)
@option(
    "-z",
    "--zero",
    help="Start from hz==0 (otherwise start from current orientation)",
    is_flag=True
)
@option(
    "-c",
    "--cycles",
    help="Repetition cycles",
    type=IntRange(1),
    default=1
)
def cli_measure(**kwargs: Any) -> None:
    """
    Measure instrument inclination in multiple positions.

    The total station turns and measures the crosswise and lengthwise
    inclination in the given number of positions and cycles. For every
    position, the two inclination components, as well as the bearing is
    recorded for later processing.

    This command requires a GeoCom capable total station.
    """
    from .app import main_measure

    main_measure(**kwargs)


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "input",
    help="Inclination measurement file to process",
    type=File("rt", encoding="utf8")
)
@option(
    "-o",
    "--output",
    help="File to save results to in CSV format",
    type=File("wt", encoding="utf8", lazy=True)
)
def cli_calc(**kwargs: Any) -> None:
    """
    Calculate inclination from measurements.

    Crosswise and lengthwise inclination components together with the
    corresponding azimuths can be used to calculate an oriented resulting
    inclination. The program first calculates the axis-aligned inclination
    components (and their deviations if multiple measurements are available),
    then computes the resulting inclination and its direction.
    """
    from .app import main_calc

    main_calc(**kwargs)


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "output",
    help="Output file",
    type=File("wt", encoding="utf8", lazy=True)
)
@argument(
    "inputs",
    help="Inclination measurement files",
    type=File("rt", encoding="utf8"),
    nargs=-1,
    required=True
)
def cli_merge(**kwargs: Any) -> None:
    """
    Merge results from multiple inclination measurements.

    Simple utility command to concatenate multiple inclination measurement
    output files. The contents are simply copied, the actual data is not
    validated.
    """
    from .app import main_merge

    main_merge(**kwargs)
