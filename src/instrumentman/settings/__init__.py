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
    help="Communication protocol",
    type=Choice(["geocom", "gsidna"], case_sensitive=False)
)
@argument(
    "file",
    help="File to save settings to",
    type=file_path(readable=False)
)
@com_option_group()
@option(
    "-f",
    "--format",
    help="Settings file format",
    type=Choice(["auto", "json", "yaml", "toml"], case_sensitive=False),
    default="auto"
)
@option(
    "--defaults",
    help=(
        "Add defaults for settings that could not be saved "
        "(e.g. not applicable to the current instrument)"
    ),
    is_flag=True
)
def cli_download(**kwargs: Any) -> None:
    """
    Save instrument settings to file.

    Runs a set of predefined settings query commands of the given protocol.
    Settings that cannot be queried (i.e. not applicable to the specific
    instrument, or cannot be queried only set) are not saved, unless defaults
    are enabled. If defaults are enabled, the default values are saved for
    missing commands.

    This command requires a GeoCom capable instrument.
    """
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
    help="File containing instrument settings",
    type=file_path(exists=True, readable=True)
)
@com_option_group()
@option(
    "-f",
    "--format",
    help="Settings file format",
    type=Choice(["auto", "json", "yaml", "toml"], case_sensitive=False),
    default="auto"
)
def cli_upload(**kwargs: Any) -> None:
    """
    Load instrument settings from file.

    The options are read from the settings config file, and the corresponding
    instrument commands are executed with the supplied values.

    This command requires a GeoCom capable instrument.
    """
    from .load import main

    main(**kwargs)


@extra_command(
    "settings",
    params=None,
    context_settings={"auto_envvar_prefix": None}
)  # type: ignore[misc]
@argument(
    "file",
    help="Settings file to validate",
    type=file_path(exists=True, readable=True)
)
@option(
    "-f",
    "--format",
    help="Settings file format",
    type=Choice(["auto", "json", "yaml", "toml"], case_sensitive=False),
    default="auto"
)
def cli_validate(**kwargs: Any) -> None:
    """
    Validate instrument settings config.

    This utility simply validates, that the given settings config file follows
    the required schema.
    """
    from .validate import main

    main(**kwargs)
