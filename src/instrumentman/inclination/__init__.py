from typing import Any

from click_extra import (
    extra_command,
    option,
    option_group,
    IntRange,
    File
)

from ..utils import (
    com_baud_option,
    com_timeout_option,
    com_port_argument
)


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@option_group(
    "Connection options",
    "",
    com_baud_option(),
    com_timeout_option()
)
@option(
    "-o",
    "--output",
    help="file to save output to",
    type=File("wt", encoding="utf8", lazy=True)
)
@option(
    "-p",
    "--positions",
    help="number of positions to measure around the circle",
    type=IntRange(1),
    default=1
)
@option(
    "-z",
    "--zero",
    help="start from hz==0 (otherwise start from current orientation)",
    is_flag=True
)
@option(
    "-c",
    "--cycles",
    help="repetition cycles",
    type=IntRange(1),
    default=1
)
def cli_measure(**kwargs: Any) -> None:
    """Measure instrument inclination in multiple positions."""
    from .app import main_measure

    main_measure(**kwargs)
