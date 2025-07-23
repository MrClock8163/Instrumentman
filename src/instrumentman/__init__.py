from click_extra import extra_group, version_option

try:
    from ._version import __version__ as __version__
except Exception:
    __version__ = "0.0.0"  # Placeholder value for source installs

from . import morse
from . import terminal
from . import setup
from . import setmeasurement
from . import protocoltest
from . import inclination
from . import filetransfer
from . import jobs


@extra_group("iman", params=None)  # type: ignore[misc]
@version_option()
def cli() -> None:
    """Automated measurement programs and related utilities for surveying
    instruments."""
    pass


@cli.group("measure")  # type: ignore[misc]
def cli_measure() -> None:
    """Conduct measurements."""


@cli.group("import")  # type: ignore[misc]
def cli_import() -> None:
    """Import external data and convert it for use with other commands."""


@cli.group("calc")  # type: ignore[misc]
def cli_calc() -> None:
    """Preform calculations from measurement results."""


@cli.group("merge")  # type: ignore[misc]
def cli_merge() -> None:
    """Merge various output files."""


@cli.group("validate")  # type: ignore[misc]
def cli_validate() -> None:
    """Validate intermediate files."""


@cli.group("test")  # type: ignore[misc]
def cli_test() -> None:
    """Test protocol responsiveness."""


@cli.group("list")  # type: ignore[misc]
def cli_list() -> None:
    """List various data stored on the instrument."""


@cli.group("download")  # type: ignore[misc]
def cli_download() -> None:
    """Download data from the instrument."""


cli.add_command(morse.cli)
cli.add_command(terminal.cli)
cli_measure.add_command(setmeasurement.cli_measure)
cli_measure.add_command(setup.cli_measure)
cli_measure.add_command(inclination.cli_measure)
cli_calc.add_command(setmeasurement.cli_calc)
cli_calc.add_command(inclination.cli_calc)
cli_test.add_command(protocoltest.cli_geocom)
cli_test.add_command(protocoltest.cli_gsidna)
cli_merge.add_command(setmeasurement.cli_merge)
cli_merge.add_command(inclination.cli_merge)
cli_validate.add_command(setmeasurement.cli_validate)
cli_import.add_command(setup.cli_import)
cli_list.add_command(filetransfer.cli_list)
cli_list.add_command(jobs.cli_list)
cli_download.add_command(filetransfer.cli_download)
