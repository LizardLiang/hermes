"""Main Textual TUI application for Hermes."""

import atexit
import sys

from textual.app import App
from textual.binding import Binding

from hermes.core.config import Config, get_config


def _restore_terminal():
    """Restore terminal to normal state on exit.

    This ensures the terminal is properly restored even if the app
    is forcibly killed (e.g., via Task Manager).
    """
    try:
        # Exit alternate screen buffer and show cursor
        sys.stdout.write('\x1b[?1049l')  # Exit alternate screen
        sys.stdout.write('\x1b[?25h')    # Show cursor
        sys.stdout.flush()
    except Exception:
        pass


# Register cleanup handler
atexit.register(_restore_terminal)


class HermesApp(App):
    """Hermes TUI Application - Crowdin i18n management tool."""

    TITLE = "Hermes - Crowdin i18n Manager"
    SUB_TITLE = "Download & Upload Translations"

    CSS_PATH = "hermes.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "go_back", "Back", show=True),
        Binding("f1", "show_help", "Help", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.config: Config = get_config()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        from hermes.tui.screens.main_menu import MainMenuScreen

        self.push_screen(MainMenuScreen())

    def action_go_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def action_show_help(self) -> None:
        """Show help information."""
        self.notify(
            "Hermes - Crowdin i18n Manager\n"
            "Use arrow keys to navigate, Enter to select.\n"
            "Press 'q' to quit, Escape to go back.",
            title="Help",
            timeout=5,
        )


def run_tui() -> None:
    """Run the TUI application."""
    app = HermesApp()
    app.run()


if __name__ == "__main__":
    run_tui()
