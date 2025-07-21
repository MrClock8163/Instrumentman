from click_extra import extra_group

try:
    from ._version import __version__ as __version__
except Exception:
    __version__ = "0.0.0"  # Placeholder value for source installs

from . import morse
from . import terminal
from . import setup
from . import setmeasurement
from . import geocomtest


@extra_group(
    "iman",
    params=None
)  # type: ignore[misc]
def cli() -> None:
    """Automated measurement programs and related utilities for surveying
    instruments."""
    pass


cli.add_command(morse.cli)
cli.add_command(terminal.cli)
cli.add_command(setup.cli)
cli.add_command(setmeasurement.cli)
cli.add_command(geocomtest.cli)
