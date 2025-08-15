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
    """
    List job files on an instrument.

    For every job related file/directory, the name of the corresponding job,
    and the file/directory name is displayed in a table. Depending on the
    instrument, the listing might include miltiple items for each job
    (e.g. digital levels seem to list both job files and related point code
    files as well), the job directories or the database files themselves.

    This command requires a GeoCom capable instrument.
    """
    from .app import main_list

    main_list(**kwargs)
