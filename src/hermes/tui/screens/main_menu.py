"""Main menu screen for Hermes TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from hermes.core.config import get_config


class MainMenuScreen(Screen):
    """Main menu screen with operation selection."""

    BINDINGS = [
        Binding("up", "focus_previous", "Up", show=False),
        Binding("down", "focus_next", "Down", show=False),
        Binding("k", "focus_previous", "Up", show=False),
        Binding("j", "focus_next", "Down", show=False),
    ]

    def on_mount(self) -> None:
        """Focus the first button when screen mounts."""
        self.query_one("#btn-download", Button).focus()

    def action_focus_next(self) -> None:
        """Move focus to next widget."""
        self.focus_next()

    def action_focus_previous(self) -> None:
        """Move focus to previous widget."""
        self.focus_previous()

    def compose(self) -> ComposeResult:
        """Compose the main menu layout."""
        yield Header()

        config = get_config()
        profile = config.current_profile

        with Container(id="main-menu"), Vertical(id="menu-container"):
            yield Static("🔄 Hermes - Crowdin i18n Manager", id="menu-title")
            yield Static(
                f"Profile: {profile.name} | Project: {profile.project_id}",
                id="profile-info",
            )

            yield Button("📥 Download Translations", id="btn-download", classes="menu-button")
            yield Button("📤 Upload Translations", id="btn-upload", classes="menu-button")
            yield Button("⚙ Settings", id="btn-settings", classes="menu-button")
            yield Button("❌ Exit", id="btn-exit", classes="menu-button")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-download":
            from hermes.tui.screens.download import DownloadScreen

            self.app.push_screen(DownloadScreen())

        elif button_id == "btn-upload":
            from hermes.tui.screens.upload import UploadScreen

            self.app.push_screen(UploadScreen())

        elif button_id == "btn-settings":
            from hermes.tui.screens.settings import SettingsScreen

            self.app.push_screen(SettingsScreen())

        elif button_id == "btn-exit":
            self.app.exit()
