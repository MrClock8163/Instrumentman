from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    IntRange,
    File
)

from ..utils import (
    com_port_argument,
    com_baud_option,
    com_timeout_option
)


@extra_command(
    "data",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_baud_option()
@com_timeout_option(2)
@option(
    "-o",
    "--output",
    help="file to save received data",
    type=File("wb", encoding="utf8", lazy=True)
)
@option(
    "--eof",
    help="end-of-file marker (i.e. the last line to receive)",
    type=str,
    default=""
)
@option(
    "--autoclose/--no-autoclose",
    help="close transfer automatically upon timeout or when EOF is received",
    default=True
)
@option(
    "--inclide-eof/--no-include-eof",
    help=(
        "wether the EOF marker is part of the output format "
        "(or just sent by the instrument regardless of the format in question)"
    ),
    default=False
)
def cli_download(**kwargs: Any) -> None:
    """Receive data sent from the instrument."""
    from .app import main_download

    main_download(**kwargs)


@extra_command(
    "data",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "file",
    help="data file to upload",
    type=File("rt", encoding="ascii")
)
@com_baud_option(1200)
@com_timeout_option()
@option(
    "-s",
    "--skip",
    help="number of header rows to skip",
    type=IntRange(min=0),
    default=0
)
def cli_upload(**kwargs: Any) -> None:
    """Upload ASCII data to the instrument."""
    from .app import main_upload

    main_upload(**kwargs)
