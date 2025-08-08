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
    help="input session file to process",
    type=file_path(exists=True)
)
@argument(
    "targets",
    type=file_path(exists=True),
    help="JSON file containing target definitions"
)
@argument(
    "output",
    help="output JSON file",
    type=file_path(readable=False)
)
@option(
    "--points",
    help="target points to use as references",
    type=str
)
@option(
    "--height",
    help="instrument height",
    type=float,
    default=0
)
def cli_calc(**kwargs: Any) -> None:
    """Calculate station coordinates from set measurements by resection."""
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
    help="station coordinates",
    type=(float, float, float),
    is_flag=False,
    flag_value=(0, 0, 0)
)
@option(
    "-i",
    "--instrumentheight",
    "--iheight",
    help="instrument height",
    type=float,
    is_flag=False,
    flag_value=0
)
@option(
    "-o",
    "--orientation",
    help="instrument orientation correction",
    type=Angle()
)
@option(
    "-a",
    "--azimuth",
    help="current azimuth",
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
    """Upload station setup to instrument."""
    from .upload import main

    main(**kwargs)
