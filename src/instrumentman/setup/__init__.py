from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    IntRange,
    Choice,
    File
)
from cloup.constraints import constraint, all_or_none

from ..utils import (
    com_option_group,
    com_port_argument
)


_PRISMCHOICE = Choice(
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


@extra_command(
    "targets",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "output",
    help=(
        "Path to save the JSON containing the recorded targets "
        "(if the file already exists, the new targets can be appended)"
    ),
    type=str
)
@com_option_group()
def cli_measure(**kwargs: Any) -> None:
    """
    Record new target points for automated measurements.

    The program can be used to record target point definitions for use in
    automated measurements. The process is interactive, and instructions are
    given at every step.

    The appropriate prism type and target height needs to be set on the
    instrument before recording each target point. The program will
    automatically request the information from the instrument and prompt for
    confirmation (they can be corrected in the prompt if necessary).
    """
    from .app import main_measure

    main_measure(**kwargs)


@extra_command(
    "csv-targets",
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
    "-c",
    "--column",
    "columns",
    help="Data column (pt, e, n and z are mandatory to specify)",
    type=Choice(
        ["ignore", "pt", "e", "n", "h", "prism", "ht"]
    ),
    multiple=True,
    required=True,
    default=()
)
@option(
    "--skip",
    help="Number of header rows to skip",
    type=IntRange(0),
    default=0
)
@option(
    "-d",
    "--delimiter",
    help="Column delimiter character",
    type=str,
    default=","
)
@option(
    "--reflector",
    help="Reflector at the targets (set only if CSV has no 'prism' column)",
    type=_PRISMCHOICE
)
@option(
    "--height",
    help="Target height (set only if CSV has no 'ht' column)",
    type=float
)
def cli_convert_csv_to_targets(**kwargs: Any) -> None:
    """
    Convert a CSV file containing coordinates to a target definition.

    The order and data of columns can be given by specifying the column
    option multiple times. For a successful import the point name (pt),
    easting (e), northing (n) and height (h) must be specified.

    If the CSV does not contain a prism column and the prism option was not
    set, the value will be prompted for at every point. Same applies to the
    target height.
    """
    from .convert import main_csv_to_targets

    main_csv_to_targets(**kwargs)


@extra_command(
    "targets-csv",
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
    "-c",
    "--column",
    "columns",
    help="Data column to output",
    type=Choice(
        ["pt", "e", "n", "h", "prism", "ht"]
    ),
    multiple=True,
    default=(),
    required=True
)
@option(
    "--header/--no-header",
    help="Write header row",
    type=bool,
    default=True
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
    help="Number of decimals to output",
    type=IntRange(0)
)
def cli_convert_targets_to_csv(**kwargs: Any) -> None:
    """
    Convert target definition to CSV coordinate list.

    The columns of the CSV can be defined by setting the column option
    multiple times. The output can show the name, easting, northing and height
    of each point, as well as the reflector type and height.
    """
    from .convert import main_targets_to_csv

    main_targets_to_csv(**kwargs)


@extra_command(
    "gsi-targets",
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
    "--reflector",
    help=(
        "Reflector at the targets "
        "(value is prompted for every point when not set)"
    ),
    type=_PRISMCHOICE
)
@option(
    "--height",
    help="Target height (value is prompted for every point when not set)",
    type=float
)
@option(
    "--station",
    help=(
        "Station coordinates "
        "(polar measurements cannot be imported without a station)"
    ),
    type=(float, float, float)
)
@option(
    "--iheight",
    "--instrumentheight",
    "instrumentheight",
    help="Instrument height at station",
    type=float
)
@constraint(
    all_or_none,
    ["station", "instrumentheight"]
)
def cli_convert_gsi_to_targets(**kwargs: Any) -> None:
    """
    Convert GSI (polar or cartesian) to target definition.

    The conversion can use both cartesian and polar measurement files, but
    the coordinates can only be calculated from polar data, if the station
    coordinates and instrument height are specified.

    If both cartesian and polar data is present in the file, the cartesian
    values are used.

    If the reflector and height options are not set, the values are prompted
    for at every point.

    Both GSI8 and GSI16 formats are accepted.
    """
    from .convert import main_gsi_to_targets

    main_gsi_to_targets(**kwargs)


@extra_command(
    "targets-gsi",
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
def cli_convert_targets_to_gsi(**kwargs: Any) -> None:
    """
    Convert target definition to GSI coordinate format.

    The program writes the point names and coordinates into a GSI measurement
    file. If the coordinates are known to be large, the format can be set to
    GSI16.

    The output only supports meter unit, but the precision can be set as
    appropriate.
    """
    from .convert import main_targets_to_gsi

    main_targets_to_gsi(**kwargs)
