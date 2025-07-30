from typing import Any

from click_extra import (
    extra_command,
    option,
    File
)

from ..utils import (
    com_port_argument,
    com_baud_option
)


@extra_command(
    "data",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_baud_option()
@option(
    "-o",
    "--output",
    help="file to save received data",
    type=File("wb", encoding="utf8", lazy=True)
)
@option(
    "--eof",
    help="end-of-file marker",
    type=str,
    default=""
)
def cli_download(**kwargs: Any) -> None:
    """Receive data sent from the instrument."""
    from .app import main_download

    main_download(**kwargs)
