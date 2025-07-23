from typing import Any

from click_extra import (
    extra_command,
    option,
    argument,
    IntRange,
    Choice,
    File
)

from ..utils import (
    com_option_group,
    com_port_argument
)


@extra_command(
    "files",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "directory",
    help="directory to list files in (path should end with '/')",
    type=str,
    default="/"
)
@com_option_group()
@option(
    "-d",
    "--device",
    help="memory device",
    type=Choice(
        (
            "internal",
            "cf",
            "sd",
            "usb",
            "ram"
        ),
        case_sensitive=False
    ),
    default="internal"
)
@option(
    "-f",
    "--filetype",
    help="file type",
    type=Choice(
        (
            "image",
            "database",
            "overview-jpg",
            "overview-bmp",
            "telescope-jpg",
            "telescope-bmp",
            "scan",
            "unknown",
            "last"
        ),
        case_sensitive=False
    ),
    default="unknown"
)
def cli_list(**kwargs: Any) -> None:
    """List files on an instrument."""
    from .app import main_list

    main_list(**kwargs)


@extra_command(
    "file",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "filename",
    help=(
        "file to download (including path with '/' separators if filetype "
        "option is not specified)"
    ),
    type=str
)
@argument(
    "output",
    help="file to save downloaded data to",
    type=File("wb", lazy=False)
)
@com_option_group()
@option(
    "-d",
    "--device",
    help="memory device",
    type=Choice(
        (
            "internal",
            "cf",
            "sd",
            "usb",
            "ram"
        ),
        case_sensitive=False
    ),
    default="internal"
)
@option(
    "-f",
    "--filetype",
    help="file type",
    type=Choice(
        (
            "image",
            "database",
            "overview-jpg",
            "overview-bmp",
            "telescope-jpg",
            "telescope-bmp",
            "scan",
            "unknown",
            "last"
        ),
        case_sensitive=False
    ),
    default="unknown"
)
@option(
    "-c",
    "--chunk",
    help="chunk size (max 450 for normal and 1800 for VivaTPS large download)",
    type=IntRange(1, 1800),
    default=450
)
@option(
    "--large",
    help="use large download commands (only available from VivaTPS)",
    is_flag=True
)
def cli_download(**kwargs: Any) -> None:
    """Download a file from the instrument."""
    from .app import main_download

    main_download(**kwargs)
