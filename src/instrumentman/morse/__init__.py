from typing import Any

from click_extra import (
    extra_command,
    option,
    argument,
    Choice,
    IntRange
)

from ..utils import (
    com_option_group,
    com_port_argument
)


@extra_command(
    "morse",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "message",
    help="message to relay as a string of ASCII characters",
    type=str
)
@option(
    "-i",
    "--intensity",
    help="beeping intensity",
    type=IntRange(0, 100),
    default=100
)
@option(
    "-u",
    "--unittime",
    help="beep unit time in milliseconds [ms]",
    type=IntRange(min=50),
    default=50
)
@option(
    "-c",
    "--compatibility",
    help="instrument compatibility",
    type=Choice(["none", "TPS1000"], case_sensitive=False),
    default="none"
)
@option(
    "--ignore-non-ascii",
    help="suppress encoding errors and skip non-ASCII characters",
    is_flag=True
)
@com_option_group()
def cli(**kwargs: Any) -> None:
    """Play a Morse encoded ASCII message through the beep signals
        of a GeoCom capable total station.
        """

    from .app import main

    main(**kwargs)
