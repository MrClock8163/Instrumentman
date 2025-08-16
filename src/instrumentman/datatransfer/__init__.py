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
    help="File to save received data",
    type=File("wb", encoding="utf8", lazy=True)
)
@option(
    "--eof",
    help="End-of-file marker (i.e. the last line to receive)",
    type=str,
    default=""
)
@option(
    "--autoclose/--no-autoclose",
    help="Close transfer automatically upon timeout or when EOF is received",
    default=True
)
@option(
    "--include-eof/--no-include-eof",
    help=(
        "Wether the EOF marker is part of the output format "
        "(or just sent by the instrument regardless of the format in question)"
    ),
    default=False
)
def cli_download(**kwargs: Any) -> None:
    """
    Receive data sent from the instrument.

    This command is intended to receive and save ASCII or extended ASCII
    documents line by line, such as typical data exports from instruments.

    To sucessfully receive the data, the program has to be started before the
    instrument starts sending the lines.

    Since not all ASCII export formats have an EOF marker, the download can be
    closed by two mechanisms if no marker is set. The process can be closed
    manually by keyboard interrupt once all data expected was received.
    Alternatively the process can close automatically at the first connection
    timeout (only if a first line was ever received, otherwise the program
    waits indefinitely and has to be interrupted manually).
    """
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
    help="Data file to upload",
    type=File("rt", encoding="ascii")
)
@com_baud_option(1200)
@com_timeout_option()
@option(
    "-s",
    "--skip",
    help="Number of header rows to skip",
    type=IntRange(min=0),
    default=0
)
def cli_upload(**kwargs: Any) -> None:
    """
    Upload ASCII data to the instrument.

    This command can be used to send ASCII data line by line to an instrument,
    that supports serial data transfer. Such data can be a CSV formatted
    coordinate list, or an instrument specific format type (e.g. Leica GSI,
    Sokkia SDR).

    To ensure the successful reception of the data, it is recommended to use
    1200 baud. At higher speeds the instrument might not be able to process the
    data quickly enough, leading to the receiving buffer filling up, which will
    result in loss of data.

    The instrument should be set to receiving mode before starting the upload.
    """
    from .app import main_upload

    main_upload(**kwargs)
