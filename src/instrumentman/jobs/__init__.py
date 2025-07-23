from typing import Any

from click_extra import extra_command

from ..utils import (
    com_option_group,
    com_port_argument
)


@extra_command(
    "jobs",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@com_option_group()
def cli_list(**kwargs: Any) -> None:
    """List job files on an instrument."""
    from .app import main_list

    main_list(**kwargs)
