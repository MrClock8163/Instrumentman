from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    IntRange,
    Choice
)

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
        "path to save the JSON containing the recorded targets "
        "(if the file already exists, the new targets can be appended)"
    ),
    type=str
)
@com_option_group()
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
