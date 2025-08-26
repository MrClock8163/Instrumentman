from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    constraint,
    Choice,
    IntRange,
    File,
    file_path
)
from cloup.constraints import all_or_none

from ..utils import (
    com_option_group,
    com_port_argument,
    Angle
)


@extra_command(
    "sets",
    params=None,
    context_settings={"auto_envvar_prefix": None},
    aliases=["set"]
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "targets",
    type=file_path(exists=True),
    help="JSON file containing target definitions"
)
@argument(
    "output",
    type=str,
    help=(
        "Output file path or path template with placeholders "
        "('{date}', '{time}', '{order}', '{cycles}')"
    )
)
@com_option_group()
@option(
    "--dateformat",
    type=str,
    default="%Y%m%d",
    help="Date format as accepted by strftime"
)
@option(
    "--timeformat",
    type=str,
    default="%H%M%S",
    help="Time format as accepted by strftime"
)
@option(
    "-c",
    "--cycles",
    type=IntRange(min=1),
    default=1,
    help="Number of measurement cycles"
)
@option(
    "-o",
    "--order",
    help="Measurement order (capital letter: face 1, lower case: face 2)",
    type=Choice(["AaBb", "AabB", "ABab", "ABba", "ABCD"]),
    default="ABba"
)
@option(
    "-s",
    "--sync-time",
    help="Synchronize instrument time and date with the computer",
    is_flag=True
)
@option(
    "-p",
    "--point",
    "points",
    type=str,
    multiple=True,
    help=(
        "Target to use from loaded target definition "
        "(set multiple times to use specific points, leave unset to use all)"
    ),
    default=()
)
def cli_measure(**kwargs: Any) -> None:
    """
    Run sets of measurements to predefined targets.

    The target coordinates are loaded from the specified target definition
    file. The total station aims at the target coordinates (fine adjusting
    with ATR) and takes polar measurements in the given order.

    The measurement results are saved in a JSON format for later processing.

    This command requires a GeoCom capable robotic total station, that has
    ATR.
    """
    from .measure import main

    main(**kwargs)


@extra_command(
    "sets",
    params=None,
    context_settings={"auto_envvar_prefix": None},
    aliases=["set"]
)  # type: ignore[misc]
@argument(
    "output",
    help="Output file",
    type=file_path()
)
@argument(
    "inputs",
    help="Set measurement session JSON files (glob notation)",
    type=file_path(exists=True),
    nargs=-1,
    required=True
)
@option(
    "--allow-oneface",
    help="Accept points with face 1 measurements only as well",
    is_flag=True
)
def cli_merge(**kwargs: Any) -> None:
    """
    Merge the output of multiple set measurement sessions.

    The results of every set measurement session are saved to a separate file.
    When multiple sessions are measured using the same targets from the same
    station, the data files need to be merged to process them together.

    The merge will be refused if the station information, or the target
    points do not match between the targeted sessions.
    """
    from .process import main_merge

    main_merge(**kwargs)


@extra_command(
    "sets",
    params=None,
    context_settings={"auto_envvar_prefix": None},
    aliases=["set"]
)  # type: ignore[misc]
@argument(
    "inputs",
    help="Set measurement session JSON files (glob notation)",
    nargs=-1,
    required=True,
    type=file_path(exists=True)
)
@option(
    "-s",
    "--schema-only",
    help="Only validate the JSON schema",
    is_flag=True
)
@option(
    "--allow-oneface",
    help="Accept points with face 1 measurements only as well",
    is_flag=True
)
def cli_validate(**kwargs: Any) -> None:
    """
    Validate session output files.

    After the measurement sessions are finished, it might be useful to
    validate, that each session succeeded, no points were skipped.
    """
    from .process import main_validate

    main_validate(**kwargs)


@extra_command(
    "sets",
    params=None,
    context_settings={"auto_envvar_prefix": None},
    aliases=["set"]
)  # type: ignore[misc]
@argument(
    "input",
    help="Input session file to process",
    type=file_path(exists=True)
)
@argument(
    "output",
    help="Output CSV file",
    type=file_path(readable=False)
)
@option(
    "--header",
    help="Write column headers",
    is_flag=True
)
@option(
    "-d",
    "--delimiter",
    help="Column delimiter character",
    type=str,
    default=","
)
@option(
    "-p",
    "--precision",
    help="Decimal precision",
    type=IntRange(min=0),
    default=4
)
@option(
    "--allow-oneface",
    help="Accept points with face 1 measurements only as well",
    is_flag=True
)
@option(
    "--station",
    help="Override the recorded station coordinates",
    type=(float, float, float)
)
@option(
    "--instrumentheight",
    "--iheight",
    help="Override instrument height",
    type=float
)
@option(
    "--orientation",
    help="Override instrument orientation",
    type=Angle()
)
@constraint(
    all_or_none,
    ["station", "instrumentheight"]
)
def cli_calc(**kwargs: Any) -> None:
    """Calculate results from set measurements.

    The most common calculation needed after set measurements is the
    determination of the target coordinates, from results of multiple
    measurement sessions and/or cycles. The resulting coordinates (as well as
    their deviations) are saved to a simple CSV file.
    """
    from .process import main_calc

    main_calc(**kwargs)


@extra_command(
    "set-gsi",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "input",
    help="Source file to convert",
    type=File("r", encoding="utf8")
)
@argument(
    "output",
    help="Target file to save result to",
    type=File("wt", encoding="utf8", lazy=True)
)
@option(
    "-l",
    "--gsi16",
    help="Export to GSI16 format (instead of GSI8)",
    is_flag=True
)
@option(
    "-p",
    "--length-unit",
    help=(
        "Length unit and precision "
        "(millimeter, millifeet, decimillimeter, decimillifeet, "
        "centimillimeter)"
    ),
    type=Choice(
        (
            "mm",
            "mft",
            "dmm",
            "dmft",
            "cmm"
        ),
        case_sensitive=False
    ),
    default="dmm"
)
@option(
    "--angle-unit",
    help="Angular unit to use",
    type=Choice(
        (
            "gon",
            "deg",
            "dms",
            "mil"
        ),
        case_sensitive=False
    ),
    default="deg"
)
def cli_convert_set_to_gsi(**kwargs: Any) -> None:
    """
    Convert set measurements to GSI format for further processing.

    To process the measurements in external software, the set measurement
    results can be converted into the well established Leica GSI format.

    The values can be exported in any of the units supported by GSI. For
    large values, GSI16 can be enabled.
    """
    from .process import main_convert_set_to_gsi

    main_convert_set_to_gsi(**kwargs)
