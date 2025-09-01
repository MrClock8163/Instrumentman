from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    option_group,
    File,
    file_path,
    Choice,
    IntRange,
    FloatRange
)
from cloup.constraints import mutually_exclusive

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
@option(
    "--overlap",
    help="Minimum horizontal and vertical overlap between images (percentage)",
    type=(IntRange(5, 95), IntRange(5, 95)),
    default=(30, 30)
)
@option(
    "--prefix",
    help="Image prefix before number",
    type=str,
    default="panorama_"
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
    "output",
    help="Output image file path",
    type=file_path(readable=False)
)
@argument(
    "image",
    help="Panorama image part",
    type=file_path(exists=True),
    nargs=-1,
    required=True
)
@option(
    "--camera-offset",
    help="Axis-aligned camera offset from the instrument center",
    type=(float, float, float)
)
@option_group(
    "Output size options",
    (
        "The width and height options set the size, that a complete spherical "
        "panorama would be saved with (fractional panoramas will be "
        "proportionally smaller). Leave all options unset for automatic "
        "calculation."
    ),
    option(
        "--scale",
        help="Panorama scale in [pixels/rad]",
        type=FloatRange(0, min_open=True)
    ),
    option(
        "--width",
        help="Width of complete sphere panorama in pixels",
        type=IntRange(0, min_open=True)
    ),
    option(
        "--height",
        help="Height of complete sphere panorama in pixels",
        type=IntRange(0, min_open=True)
    ),
    constraint=mutually_exclusive
)
@option_group(
    "Point list file options",
    option(
        "--annotate",
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
        "--color",
        help="Color in RGB8 notation",
        type=(IntRange(0, 255), IntRange(0, 255), IntRange(0, 255)),
        default=(0, 0, 0)
    ),
    option(
        "--fontsize",
        help="Font size in pixels",
        type=IntRange(0, min_open=True),
        default=10
    ),
    # option(
    #     "--thickness",
    #     help="Font line thickness",
    #     type=IntRange(0, min_open=True),
    #     default=1
    # ),
    option(
        "--marker",
        help="Point marker shape",
        type=Choice(
            (
                "cross",
                "x",
                "star",
                "diamond",
                "square",
                "uptriangle",
                "downtriangle"
            ),
            case_sensitive=False
        ),
        default="cross"
    ),
    option(
        "--markersize",
        help="Point marker size in pixels",
        type=IntRange(1),
        default=10
    ),
    option(
        "--offset",
        help="Point name offset in pixels",
        type=(int, int)
    ),
    option(
        "--justify",
        help="Point name justification",
        type=Choice(
            (
                "tl", "tc", "tr",
                "ml", "mc", "mr",
                "bl", "bc", "br",
            ),
            case_sensitive=False
        ),
        default="bl"
    ),
    option(
        "--label-fontsize",
        help="Label font size in pixels",
        type=IntRange(0, min_open=True)
    ),
    # option(
    #     "--label_thickness",
    #     help="Label text line thickness",
    #     type=IntRange(0, min_open=True)
    # ),
    option(
        "--label-color",
        help="Color in RGB8 notation",
        type=(IntRange(0, 255), IntRange(0, 255), IntRange(0, 255))
    ),
    option(
        "--label-offset",
        help="Label text offset in pixels",
        type=(int, int)
    ),
    option(
        "--label-justify",
        help="Label text justification",
        type=Choice(
            (
                "tl", "tc", "tr",
                "ml", "mc", "mr",
                "bl", "bc", "br",
            ),
            case_sensitive=False
        ),
        default="tl"
    )
)
def cli_calc(**kwargs: Any) -> None:
    from .process import main

    main(**kwargs)
