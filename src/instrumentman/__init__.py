from pathlib import Path

from click_extra import extra_group, version_option

try:
    from ._version import __version__ as __version__
except Exception:
    __version__ = "0.0.0"  # Placeholder value for source installs

from .utils import (
    logging_option_group,
    logging_levels_constraint,
    logging_output_constraint,
    logging_target_constraint,
    logging_rotation_constraint,
    configure_logging
)
from . import morse
from . import terminal
from . import setup
from . import setmeasurement
from . import station
from . import protocoltest
from . import inclination
from . import filetransfer
from . import jobs
from . import datatransfer
from . import settings


@extra_group(
    "iman",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@version_option()
@logging_option_group()
@logging_levels_constraint()
@logging_output_constraint()
@logging_target_constraint()
@logging_rotation_constraint()
def cli(
    protocol: bool = False,
    debug: bool = False,
    info: bool = False,
    warning: bool = False,
    error: bool = False,
    critical: bool = False,
    file: Path | None = None,
    stdout: bool = False,
    stderr: bool = False,
    format: str = "{message}",
    dateformat: str = "%Y-%m-%d %H:%M:%S",
    rotate: tuple[int, int] | None = None
) -> None:
    """
    \b
    +--------------------------------------------------------------------+
    |                                                                    |
    |       .---------.                                                  |
    |      / +-------+ \\                                                 |
    |     .__| +---+ |__.                                                |
    |     |  | |   | |  |    ___                                         |
    |     |  |=| @ |=|  |   |_ _|          _ __ ___     __ _   _ __      |
    |     |  | |   | |  |    | |   _____  | '_ ` _ \\   / _` | | '_ \\     |
    |     |  | +---+ |  |    | |  |_____| | | | | | | | (_| | | | | |    |
    |    .+--+-------+--+.  |___|         |_| |_| |_|  \\__,_| |_| |_|    |
    |    | .----.   123  |                                               |
    |    | |____|   456  |                                               |
    |    '_______________'                                               |
    |                                                                    |
    +--------------------------------------------------------------------+

    Instrumentman (or I-man for short) is a collection of command line programs
    related to the automation of surveying instruments (primarily robotic total
    stations) through serial line command protocols (mainly Leica GeoCom).

    The individual commands are available through their respective action
    based command groups. The help page for each command can be accessed
    through the -h/--help option. Logging can be set up with options of this
    root command.

    Examples:

    iman download file -h

    iman --debug --file log.log measure inclination -o incline.csv -p 3 COM1

    iman calc sets merged.json results.csv

    iman terminal
    """
    configure_logging(
        protocol,
        debug,
        info,
        warning,
        error,
        critical,
        file,
        stderr,
        stdout,
        format,
        dateformat,
        rotate
    )


@cli.group("measure")  # type: ignore[misc]
def cli_measure() -> None:
    """Conduct measurements."""


@cli.group("convert")  # type: ignore[misc]
def cli_convert() -> None:
    """Convert between various file formats."""


@cli.group("calculate", aliases=["calc"])  # type: ignore[misc]
def cli_calc() -> None:
    """Preform calculations from measurement results."""


@cli.group("merge", aliases=["join", "concat"])  # type: ignore[misc]
def cli_merge() -> None:
    """Merge various output files."""


@cli.group("validate", aliases=["check"])  # type: ignore[misc]
def cli_validate() -> None:
    """Validate intermediate files."""


@cli.group("test")  # type: ignore[misc]
def cli_test() -> None:
    """Test protocol responsiveness."""


@cli.group("list", aliases=["ls"])  # type: ignore[misc]
def cli_list() -> None:
    """List various data stored on the instrument."""


@cli.group("download", aliases=["dl", "save"])  # type: ignore[misc]
def cli_download() -> None:
    """Download data from the instrument."""


@cli.group("upload", aliases=["ul", "load"])  # type: ignore[misc]
def cli_upload() -> None:
    """Upload data to the instrument."""


cli.add_command(morse.cli)
cli.add_command(terminal.cli)
cli_measure.add_command(setmeasurement.cli_measure)
cli_measure.add_command(setup.cli_measure)
cli_measure.add_command(inclination.cli_measure)
cli_calc.add_command(setmeasurement.cli_calc)
cli_calc.add_command(inclination.cli_calc)
cli_calc.add_command(station.cli_calc)
cli_test.add_command(protocoltest.cli_geocom)
cli_test.add_command(protocoltest.cli_gsidna)
cli_merge.add_command(setmeasurement.cli_merge)
cli_merge.add_command(inclination.cli_merge)
cli_validate.add_command(setmeasurement.cli_validate)
cli_validate.add_command(settings.cli_validate)
cli_list.add_command(filetransfer.cli_list)
cli_list.add_command(jobs.cli_list)
cli_download.add_command(filetransfer.cli_download)
cli_download.add_command(datatransfer.cli_download)
cli_download.add_command(settings.cli_download)
cli_upload.add_command(datatransfer.cli_upload)
cli_upload.add_command(settings.cli_upload)
cli_upload.add_command(station.cli_upload)
cli_convert.add_command(setup.cli_convert_csv_to_targets)
cli_convert.add_command(setup.cli_convert_targets_to_csv)
cli_convert.add_command(setup.cli_convert_gsi_to_targets)
cli_convert.add_command(setup.cli_convert_targets_to_gsi)
cli_convert.add_command(setmeasurement.cli_convert_set_to_gsi)
