from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    file_path
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
    "--coordinates",
    help="station coordinates",
    type=(float, float, float),
    default=(0, 0, 0)
)
@option(
    "--instrumentheight",
    "--iheight",
    help="instrument height",
    type=float,
    default=0
)
@option(
    "--orientation",
    help="instrument orientation correction",
    type=Angle(),
    default="0-00-00"
)
def cli_upload(**kwargs: Any) -> None:
    """Upload station setup to instrument."""
    from .upload import main

    main(**kwargs)
