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
        ["ignore", "pt", "e", "n", "z", "prism", "ht"]
    ),
    multiple=True,
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
    help="Reflector at the targets (set only if CSV has no prism column)",
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
@option(
    "--height",
    help="Target height",
    type=float
)
def cli_convert_csv_to_targets(**kwargs: Any) -> None:
    """Convert a CSV file containing coordinates to a target definition."""
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
        ["pt", "e", "n", "z", "prism", "ht"]
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
    """Convert target definition to CSV coordinate list."""
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
    help="Reflector at the targets",
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
@option(
    "--height",
    help="Target height",
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
    """Convert GSI (polar or cartesian) to target definition."""
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
    "--precision",
    help=(
        "Coordinate precision to output"
        "(millimeter: 0.001m, decimillimeter: 0.0001m, "
        "centimillimeter: 0.00001m)"
    ),
    type=Choice(
        (
            "mm",
            "dmm",
            "cmm"
        ),
        case_sensitive=False
    ),
    default="mm"
)
def cli_convert_targets_to_gsi(**kwargs: Any) -> None:
    """Convert target definition to GSI coordinate format."""
    from .convert import main_targets_to_gsi

    main_targets_to_gsi(**kwargs)


@extra_command(
    "targets",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "reflector",
    help="prism type of the targets",
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
@argument(
    "input",
    help="csv file containing the target coordinates",
    type=str
)
@argument(
    "output",
    help="path to save the target definition to",
    type=str
)
@option(
    "-d",
    "--delimiter",
    help="column delimiter character",
    type=str,
    default=","
)
@option(
    "-c",
    "--columns",
    help=(
        "column spec "
        "(P: point ID, E: easting, N: northing, Z: height, _: ignore)"
    ),
    type=str,
    default="PENZ"
)
@option(
    "-s",
    "--skip",
    help="number of header rows to skip",
    type=IntRange(min=0),
    default=0
)
def cli_import(**kwargs: Any) -> None:
    """Import target points.

    If a coordinate list already exists with the target points, it can
    be imported from CSV format.

    As a CSV file may contain any number and types of columns, the
    mapping to the relevant columns can be given with a column spec.
    A column spec is a string, with each character representing a
    column type.

    - ``P``: point ID

    - ``E``: easting

    - ``N``: northing

    - ``Z``: up/height

    - ``_``: ignore/skip column

    Every column spec must specify the ``PENZ`` fields in the appropriate
    order.

    Examples:

    - ``PENZ``: standard column order

    - ``P_ENZ``: skipping 2nd column containing point codes

    - ``EN_Z_P``: mixed column order and skipping
    """
    from .app import main_import

    main_import(**kwargs)
