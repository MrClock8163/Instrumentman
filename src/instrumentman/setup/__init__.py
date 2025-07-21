from typing import Any

from click_extra import (
    extra_group,
    extra_command,
    argument,
    option,
    option_group,
    IntRange,
    Choice
)

from ..utils import (
    com_baud_option,
    com_timeout_option,
    com_port_argument
)


@extra_command(
    "measure",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "output",
    help=(
        "path to save the JSON containing the recorded targets "
        "(if the file already exists, the new targets can be appended)"
    ),
    type=str
)
@option_group(
    "Connection options",
    "Options related to the serial connection",
    com_baud_option(),
    com_timeout_option(),
    option(
        "-r",
        "--retry",
        help="number of connection retry attempts",
        type=IntRange(min=0, max=10),
        default=1
    ),
    option(
        "--sync-after-timeout",
        help="attempt to synchronize message que after a connection timeout",
        is_flag=True
    )
)
def cli_measure(**kwargs: Any) -> None:
    """Measure target points.

    The program gives instructions in the terminal at each step.

    .. caution::
        :class: warning

        The appropriate prism type needs to be set on the instrument before
        recording each target point. The program will automatically request
        the type from the instrument after the point is measured.
    """
    from .app import main_measure

    main_measure(**kwargs)


@extra_command(
    "import",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "reflector",
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
    type=str
)
@argument(
    "output",
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


@extra_group("targets", params=None)  # type: ignore[misc]
def cli() -> None:
    """Record target points for later automated measurements."""


cli.add_command(cli_measure)
cli.add_command(cli_import)
