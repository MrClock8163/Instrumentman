from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    file_path,
    Choice
)
from cloup import constraint
from cloup.constraints import If, IsSet, require_all

from ..utils import (
    com_port_argument,
    com_option_group
)


@extra_command(
    "save",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "file",
    help="file to save settings to",
    type=file_path(readable=False)
)
@com_option_group()
@option(
    "-f",
    "--format",
    help="settings file format",
    type=Choice(["auto", "json", "yaml", "toml"], case_sensitive=False),
    default="auto"
)
@option(
    "--save-all",
    help="save every setting, even if not applicable to the instrument",
    is_flag=True
)
@option(
    "--add-defaults",
    help="add defaults for settings that cannot be saved",
    is_flag=True
)
@constraint(
    If(IsSet("add_defaults"), require_all),
    ["add_defaults", "save_all"]
)
def cli_save(**kwargs: Any) -> None:
    """Save instrument settings to file."""
    ...


@extra_command(
    "load",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "settings",
    help="file containing instrument settings",
    type=file_path(exists=True, readable=True)
)
@com_option_group()
@option(
    "-f",
    "--format",
    help="settings file format",
    type=Choice(["auto", "json", "yaml", "toml"], case_sensitive=False),
    default="auto"
)
def cli_load(**kwargs: Any) -> None:
    """Load instrument settings from file."""
    from .load import main

    main(**kwargs)


@extra_command(
    "settings",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "file",
    help="settings file to validate",
    type=file_path(exists=True, readable=True)
)
@option(
    "-f",
    "--format",
    help="settings file format",
    type=Choice(["auto", "json", "yaml", "toml"], case_sensitive=False),
    default="auto"
)
def cli_validate(**kwargs: Any) -> None:
    """Validate instrument settings config."""
    from .validate import main

    main(**kwargs)
