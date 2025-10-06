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
from cloup.constraints import (
    constraint,
    mutually_exclusive,
    accept_none,
    require_all,
    If,
    Equal
)

from ..utils import (
    com_port_argument,
    com_option_group,
    Angle
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
    "--prefix",
    help="Image prefix before number",
    type=str,
    default="panorama_"
)
@option(
    "--whitebalance",
    help=(
        "Set white balance mode for the capture "
        "(mode is reset to auto after the program is finished)"
    ),
    type=Choice(
        (
            "auto",
            "indoor",
            "outdoor"
        ),
        case_sensitive=False
    )
)
@option(
    "--increase-tolerance",
    help=(
        "Increase the positioning tolerances for the duration of the program. "
        "USE WITH CAUTION!"
    ),
    is_flag=True
)
@option(
    "--overlap",
    help=(
        "Overlap between images within a row, and overlap between rows "
        "(percentage)"
    ),
    type=(IntRange(5, 95), IntRange(10, 95)),
    default=(5, 10)
)
@option(
    "--shape",
    help="Panorama area type",
    type=Choice(
        (
            "region",
            "strip",
            "sphere"
        ),
        case_sensitive=False
    ),
    default="region"
)
@option(
    "--layout",
    help="Image positions layout",
    type=Choice(
        ("grid", "adaptive-fov"),
        case_sensitive=False
    ),
    default="adaptive-fov"
)
@option(
    "--horizontal",
    help="Horizontal start (left) and end (right) bearing",
    type=(Angle(), Angle())
)
@option(
    "--vertical",
    help="Vertical start (top) and end (bottom) zenith angle",
    type=(Angle(), Angle())
)
@constraint(
    If(Equal("shape", "sphere"), accept_none),
    ["horizontal", "vertical"]
)
@constraint(
    If(Equal("shape", "strip"), accept_none),
    ["horizontal"]
)
@constraint(
    If("horizontal", require_all),
    ["vertical"]
)
def cli_measure(**kwargs: Any) -> None:
    """
    Take pictures with the overview camera of a total station for later
    panoramic processing.

    The angular area to cover can be set in the command line, or recorded
    with the instrument at the start of the program. To use the point
    annotation feature during later processing, the instrument should be
    properly set up and oriented in the local coordinate system when running
    this program.

    The acquisition positions are calculated, so that there is at least 5%
    overlap between images in a row, and 10% overlap between rows. When the
    defined panorama area covers the full range (360 degrees horiztal
    and/or 180 degrees vertical) the overlap will be usually larger, otherwise
    the program will opt to capture a slightly wider/taller area to keep the
    overlap close to the nominal values. The default position layout take into
    account, that images taken farther from horizon cover more and more
    horizontal area.

    The metadata required for later processing is saved on the controlling
    computer, the images themselves have to be downloaded from the instrument.
    The images are typically saved to the SD card (if available), in the
    'Data/Geocom/Images/Wide-angle' directory.

    Time required for the whole process mainly depends on the number of images,
    which in turn is dependent on the acquisition area. A full sphere panorama
    at 1x zoom on a non-piezo motorized instrument takes around 25-30 minutes
    to capture with around 350 images. New instruments with piezo motors might
    be faster, but the main limiting factor is the camera, not the motors.

    Enabling increased positioning tolerances might sligtly reduce the time,
    but if an unexpected error occurs, the program might not be able to restore
    the original tolerances, so USE WITH CAUTION.

    This command requires a GeoCOM capable robotic total station with overview
    camera imaging functions.
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
    "--shift",
    help=(
        "Shift bearing of panorama center to reorient view and potentially "
        "remove black gaps (only exact for strip and sphere)"
    ),
    type=Angle()
)
@option(
    "--compensation",
    help="Basic exposure compensation method",
    type=Choice(
        ("none", "channels", "gain"),
        case_sensitive=False
    ),
    default="channels"
)
@option(
    "--blending",
    help="Overlap blending method",
    type=Choice(
        ("none", "multiband", "feather"),
        case_sensitive=False
    ),
    default="multiband"
)
@option(
    "--seams",
    help="Method to delineate individual frames at overlaps",
    type=Choice(
        ("none", "voronoi", "dynamic-programming"),
        case_sensitive=False
    ),
    default="voronoi"
)
@option(
    "--seam-overlap",
    help=(
        "Pixel dilation of seam masks to provide blending overlap "
        "(set to -1 for automatic calculation)"
    ),
    type=IntRange(-1),
    default=0
)
@option(
    "--visualize-stitch",
    help="Debug option to show individual frames with random colors",
    is_flag=True
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
        type=FloatRange(0, 5210, min_open=True)
    ),
    option(
        "--width",
        help="Width of complete sphere panorama in [pixels]",
        type=IntRange(0, 32735, min_open=True)
    ),
    option(
        "--height",
        help="Height of complete sphere panorama in [pixels]",
        type=IntRange(0, 16367, min_open=True)
    ),
    constraint=mutually_exclusive
)
@option_group(
    "Point list file options",
    option(
        "--annotate",
        help="CSV coordinate list of points to annotate on the images",
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
        "--font",
        help="Font face type",
        type=Choice(
            (
                "plain",
                "simplex",
                "duplex",
                "complex"
            ),
            case_sensitive=False
        ),
        default="plain"
    ),
    option(
        "--fontsize",
        help="Font size in pixels",
        type=IntRange(0, min_open=True),
        default=10
    ),
    option(
        "--thickness",
        help="Font line thickness",
        type=IntRange(0, min_open=True),
        default=1
    ),
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
        "--label-font",
        help="Label font face type",
        type=Choice(
            (
                "plain",
                "simplex",
                "duplex",
                "complex"
            ),
            case_sensitive=False
        ),
        default="plain"
    ),
    option(
        "--label-fontsize",
        help="Label font size in pixels",
        type=IntRange(0, min_open=True)
    ),
    option(
        "--label_thickness",
        help="Label text line thickness",
        type=IntRange(0, min_open=True)
    ),
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
    """
    Merge previously captured panorama frames and optionally annotate measured
    points on the resulting panorama for documentation purposes.

    IMPORTANT: This command requires an extra dependency: 'opencv-python'

    The individual images are transformed into an equirectangular projection
    based on the orientation metadata saved at the time of acquisition. The
    projected images are then merged into a single panorama image.

    On the merged panorama it is possible to annotate measured points given
    with their 3D coordinates in a CSV file. The file is expected to contain
    point name, easting, northing and height columns in this order (and
    optionally a label column as last). The accuracy of the annotation is
    usually a few centimeters. This is due to errors introduced by the offset
    and the distortions of the overview camera. The program will try to
    approximate the offset to improve the accuracy. If the precise offset is
    known, it can also be provided explicitly.

    A limit of OpenCV is, that larger panoramas cannot be processed at full
    resolution. The maximum size that OpenCV in this configuration can handle
    is defined by the maximum of a 16-bit signed integer (32767). This means,
    that at full resolution (2560 x 1920) only 12 images horizontally (for near
    vertical views not even 1 image), and 17 images vertically can be
    processed. This can be solved by setting the scale or one of the other
    sizing options to downscale the processing resolution. (The program
    automatically downscales to an appropriate size.)
    """
    from .process import main

    main(**kwargs)
