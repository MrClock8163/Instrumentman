from typing import Any

from click_extra import (
    extra_command,
    argument,
    option,
    file_path,
    Choice
)

from ..utils import (
    com_port_argument,
    com_option_group
)


@extra_command(
    "settings",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@com_port_argument()
@argument(
    "protocol",
    help="communication protocol",
    type=Choice(["geocom", "gsidna"], case_sensitive=False)
)
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
    "--defaults",
    help=(
        "add defaults for settings that could not be saved "
        "(e.g. not applicable to the current instrument)"
    ),
    is_flag=True
)
def cli_download(**kwargs: Any) -> None:
    """Save instrument settings to file."""
    from .save import main

    main(**kwargs)


@extra_command(
    "settings",
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
def cli_upload(**kwargs: Any) -> None:
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
