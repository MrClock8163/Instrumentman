from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    file_path
)
from cloup.constraints import (
    constraint,
    mutually_exclusive,
    all_or_none
)

from ..utils import (
    com_port_argument,
    com_option_group,
    Angle
)


@extra_command(
    "station",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "measurements",
    help="Input session file to process",
    type=file_path(exists=True)
)
@argument(
    "targets",
    type=file_path(exists=True),
    help="JSON file containing target definitions"
)
@argument(
    "output",
    help="Output JSON file",
    type=file_path(readable=False)
)
@option(
    "-p",
    "--point",
    "points",
    help=(
        "Target to use as reference from loaded target definition "
        "(set multiple times to use specific points, leave unset to use all)"
    ),
    type=str,
    multiple=True,
    default=()
)
@option(
    "--height",
    help="Instrument height",
    type=float,
    default=0
)
def cli_calc(**kwargs: Any) -> None:
    """
    Calculate station coordinates from set measurements by resection.

    The resection is computed in separate horizontal and vertical calculations.
    Station coordinates and the orientation are displayed once done, as well as
    their deviations from the adjustment.
    """
    from .calculate import main

    main(**kwargs)


@extra_command(
    "station",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
@option(
    "-c",
    "--coordinates",
    help="Station coordinates",
    type=(float, float, float),
    is_flag=False,
    flag_value=(0, 0, 0)
)
@option(
    "-i",
    "--instrumentheight",
    "--iheight",
    help="Instrument height",
    type=float,
    is_flag=False,
    flag_value=0
)
@option(
    "-o",
    "--orientation",
    help="Instrument orientation correction",
    type=Angle()
)
@option(
    "-a",
    "--azimuth",
    help="Current azimuth",
    type=Angle(),
    is_flag=False,
    flag_value="0-00-00"
)
@constraint(
    mutually_exclusive,
    ["orientation", "azimuth"]
)
@constraint(
    all_or_none,
    ["coordinates", "instrumentheight"]
)
def cli_upload(**kwargs: Any) -> None:
    """
    Upload station setup to instrument.

    This program cen be used to update the station coordinates and height,
    and/or the orientation or azimuth.

    This command requires a GeoCom capable total station.
    """
    from .upload import main

    main(**kwargs)
