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
def cli(**kwargs: Any) -> None:
    """Test the availability of various GeoCom protocol functions on an
    instrument."""
    from .app import main

    main(**kwargs)
