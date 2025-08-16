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
    help="Directory to list files in",
    type=str,
    default=""
)
@com_option_group()
@option(
    "-d",
    "--device",
    help="Memory device",
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
    help="File type (all files are shown when not set)",
    type=Choice(
        (
            "image",
            "database",
            "overview-jpg",
            "overview-bmp",
            "telescope-jpg",
            "telescope-bmp",
            "scan",
            "last"
        ),
        case_sensitive=False
    )
)
@option(
    "--depth",
    help=(
        "Recursive depth "
        "(0: unlimited; 1<=x: depth of directory search)"
    ),
    type=IntRange(0),
    default=1
)
def cli_list(**kwargs: Any) -> None:
    """
    List files on an instrument.

    For each file in the specified directory (and discovered subdirectories
    when recursive search is enabled) the file name, file size and the time of
    last modification is displayed. Not empty directories and items, that are
    likely directories are show in blue and light blue colors. Known text
    formats are shown green. Image and drawing formats are shown in magenta.
    Database files are red. Other files are shown without special color.

    This command requires a GeoCom capable instrument, that supports file
    operations (TPS1200 and later).
    """
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
        "File to download (including path with '/' separators if filetype "
        "option is not specified)"
    ),
    type=str
)
@argument(
    "output",
    help="File to save downloaded data to",
    type=File("wb", lazy=False)
)
@com_option_group()
@option(
    "-d",
    "--device",
    help="Memory device",
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
    help="File type (full file path is required if this option is not set)",
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
    help="Chunk size (max. 225 for normal and 900 for large download mode)",
    type=IntRange(1, 900),
    default=225
)
@option(
    "--large",
    help="Use large download commands (only available from VivaTPS)",
    is_flag=True
)
def cli_download(**kwargs: Any) -> None:
    """
    Download a file from the instrument.

    Any format can be transferred. The file is downloaded in chunks of hex
    encoded binary data. The speed is strongly dependent on the connection
    baud and chunk size. Use the highest baud supported by the instrument, and
    the largest chunk size for the fastest download.

    This command requires a GeoCom capable instrument, that supports file
    operations (TPS1200 and later).
    """
    from .app import main_download

    main_download(**kwargs)
