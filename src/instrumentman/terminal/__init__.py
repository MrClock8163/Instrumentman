from click_extra import extra_command


@extra_command("terminal", params=None)  # type: ignore[misc]
def cli() -> None:
    """Test instrument commands in an interactive TUI."""

    from .app import GeoComTerminal

    tui = GeoComTerminal()
    tui.run()
