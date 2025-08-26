from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    File,
    Choice
)

from ..utils import (
    com_port_argument,
    com_option_group
)


@extra_command(
    "panorama",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "metadata",
    help="File to write image metadata to",
    type=File("wt", encoding="utf8", lazy=True)
)
@com_option_group()
@option(
    "--zoom",
    help="Camera zoom factor",
    type=Choice(("x1", "x2", "x4", "x8"), case_sensitive=False),
    default="x1"
)
def cli_measure(**kwargs: Any) -> None:
    """
    Take pictures with the instrument camera for later panormaic stitching
    """
    from .measure import main

    main(**kwargs)
