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
    from .app import main_shutdown_geocom

    main_shutdown_geocom(**kwargs)


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
    from .app import main_startup_geocom

    main_startup_geocom(**kwargs)
