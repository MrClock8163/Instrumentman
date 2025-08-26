from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    option_group,
    File,
    file_path,
    Choice,
    IntRange
)
from cloup.constraints import constraint, If, Equal, Not, require_all

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


@extra_command(
    "panorama",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "metadata",
    help="Metadata file produced by the measurement program",
    type=file_path(exists=True)
)
@argument(
    "image",
    help="Panorama image part",
    type=file_path(exists=True),
    nargs=-1,
    required=True
)
@option(
    "--action",
    help="Processing to perform",
    type=Choice(("annotate",), case_sensitive=False),
    default="annotate"
)
@option_group(
    "Point list file options",
    option(
        "--points",
        help="Coordinate list of points to annotate on the images",
        type=file_path(exists=True)
    ),
    option(
        "--skip",
        help="Number of header rows to skip",
        type=IntRange(0),
        default=0
    ),
    option(
        "--delimiter",
        help="Column delimiter",
        type=str,
        default=","
    )
)
@option_group(
    "Annotation options",
    option(
        "--rgb",
        help="Color in RGB8 notation",
        type=(IntRange(0, 255), IntRange(0, 255), IntRange(0, 255)),
        default=(0, 0, 0)
    ),
    option(
        "--fontsize",
        help="Text size in pixels",
        type=IntRange(1),
        default=50
    ),
    option(
        "--marker",
        help="Point marker shape",
        type=Choice(("cross", "dot"), case_sensitive=False),
        default="cross"
    ),
    option(
        "--markersize",
        help="Point marker size in pixels",
        type=IntRange(1),
        default=50
    )
)
@constraint(
    If(Not(Equal("action", "stitch")), require_all),
    ["action", "points"]
)
def cli_calc(**kwargs: Any) -> None:
    from .process import main

    main(**kwargs)
