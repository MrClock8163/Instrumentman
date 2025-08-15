from typing import Any

from click_extra import extra_command

from ..utils import (
    com_option_group,
    com_port_argument
)


@extra_command(
    "geocom",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
def cli_geocom(**kwargs: Any) -> None:
    """
    Test the availability of various GeoCom protocol functions on an
    instrument.

    From each GeoCom subsystem, a single command is run to test the
    responsiveness of the instrument. Some of the commands might change
    instrument settings.

    The results are displayed in a table, listing all subsystems and their
    success/failure.
    """
    from .app import main

    kwargs["protocol"] = "geocom"
    main(**kwargs)


@extra_command(
    "gsidna",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
def cli_gsidna(**kwargs: Any) -> None:
    """
    Test the availability of various GSI Online DNA functions on an
    instrument.

    From both the settings and the measurement systems, a single "get" and a
    "set" type command is executed to test the responsiveness. Some
    instrument settings might get changed.

    The results are displayed in a table, listing all commands and their
    success/failure.
    """
    from .app import main

    kwargs["protocol"] = "gsidna"
    main(**kwargs)
