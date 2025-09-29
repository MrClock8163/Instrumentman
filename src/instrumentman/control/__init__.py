from typing import Any

from click_extra import (
    extra_command,
    argument,
    Choice
)

from ..utils import (
    com_port_argument,
    com_option_group
)


@extra_command(
    "gsidna",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
def cli_shutdown_gsidna(**kwargs: Any) -> None:
    """
    Deactivate a GSI Online capable digital level.
    """
    from .app import main_shutdown_gsidna

    main_shutdown_gsidna(**kwargs)


@extra_command(
    "geocom",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "component",
    help="Instrument component to shut down",
    type=Choice(
        (
            "protocol",
            "instrument",
            "edm",
            "pointer",
            "telescopic-camera",
            "overview-camera"
        ),
        case_sensitive=False
    )
)
@com_port_argument()
@com_option_group()
def cli_shutdown_geocom(**kwargs: Any) -> None:
    """
    Deactivate components of a GeoCOM capable instrument.

    To reduce power consumption, in certain scenarios it can be beneficial to
    power off some components of an instrument. Or shut down the entire machine
    completely.

    Instruments before the TPS1200 series cannot be remotely reactivated after
    a complete shutdown (the GeoCOM online mode has to be manually switched
    on). Similarly, instruments that are not connected by physical cable (but
    by Bluetooth for example) cannot be reactivated as the wireless connection
    can only be esatblished with an active instrument. Only shut down these
    instruments remotely if no further operation is needed until the next
    manual access.
    """
    from .app import main_shutdown_geocom

    main_shutdown_geocom(**kwargs)


@extra_command(
    "gsidna",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
def cli_startup_gsidna(**kwargs: Any) -> None:
    """
    Activate/reactivate a GSI Online capable digital level.
    """
    from .app import main_startup_gsidna

    main_startup_gsidna(**kwargs)


@extra_command(
    "geocom",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "component",
    help="Instrument component to start up",
    type=Choice(
        (
            "instrument",
            "edm",
            "pointer",
            "telescopic-camera",
            "overview-camera"
        ),
        case_sensitive=False
    )
)
@com_port_argument()
@com_option_group()
def cli_startup_geocom(**kwargs: Any) -> None:
    """
    Activate/reactivate components of a GeoCOM capable instrument.

    Instruments can be reactivated remotely after a complete shutdown only if
    they are TPS1200 or newer series and connected by a physical cable.
    """
    from .app import main_startup_geocom

    main_startup_geocom(**kwargs)
