from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    option_group,
    IntRange,
    File,
    file_path
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
    type=IntRange(1, 12),
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


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "input",
    help="inclination measurement file to process",
    type=file_path()
)
def cli_calc(**kwargs: Any) -> None:
    """Calculate inclination from multiple measurements."""
    from .app import main_calc

    main_calc(**kwargs)


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "output",
    help="output file",
    type=file_path()
)
@argument(
    "inputs",
    help="inclination measurement files",
    type=file_path(exists=True),
    nargs=-1,
    required=True
)
def cli_merge(**kwargs: Any) -> None:
    """Merge results from multiple inclination measurements."""
    from .app import main_merge

    main_merge(**kwargs)
