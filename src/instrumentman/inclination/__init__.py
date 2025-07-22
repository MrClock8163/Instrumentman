from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    IntRange,
    File
)

from ..utils import (
    com_option_group,
    com_port_argument
)


@extra_command(
    "inclination",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
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
    type=File("rt", encoding="utf8")
)
@option(
    "-o",
    "--output",
    help="file to save results to in CSV format",
    type=File("wt", encoding="utf8", lazy=True)
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
    type=File("wt", encoding="utf8", lazy=True)
)
@argument(
    "inputs",
    help="inclination measurement files",
    type=File("rt", encoding="utf8"),
    nargs=-1,
    required=True
)
def cli_merge(**kwargs: Any) -> None:
    """Merge results from multiple inclination measurements."""
    from .app import main_merge

    main_merge(**kwargs)
