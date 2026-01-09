"""Settings screen for configuring Hermes profiles."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.validation import Length
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from hermes.core.config import Config, Profile, get_config


class SettingsScreen(Screen):
    """Settings screen for managing profiles and configuration."""

    BINDINGS = [
        Binding("up", "focus_previous", "Up", show=False),
        Binding("down", "focus_next", "Down", show=False),
        Binding("k", "focus_previous", "Up", show=False),
        Binding("j", "focus_next", "Down", show=False),
    ]

    def action_focus_next(self) -> None:
        """Move focus to next widget."""
        self.focus_next()

    def action_focus_previous(self) -> None:
        """Move focus to previous widget."""
        self.focus_previous()

    def __init__(self):
        super().__init__()
        self.config: Config = get_config()

    def compose(self) -> ComposeResult:
        """Compose the settings layout."""
        yield Header()

        with Container(id="operation-container"):
            yield Static("⚙️ Settings", id="operation-title")

            profile = self.config.current_profile

            with Vertical(classes="settings-section"):
                yield Static("Profile Information", classes="section-title")
                yield Static(f"Current Profile: {self.config.active_profile}")

                with Horizontal(classes="form-row"):
                    yield Label("Project ID:", classes="form-label")
                    yield Input(
                        value=profile.project_id,
                        id="input-project-id",
                        classes="form-input",
                        placeholder="e.g., 577773",
                    )

            with Vertical(classes="settings-section"):
                yield Static("File Paths", classes="section-title")

                with Horizontal(classes="form-row"):
                    yield Label("Data Path:", classes="form-label")
                    yield Input(
                        value=profile.data_path,
                        id="input-data-path",
                        classes="form-input",
                    )

                with Horizontal(classes="form-row"):
                    yield Label("Result Path:", classes="form-label")
                    yield Input(
                        value=profile.result_path,
                        id="input-result-path",
                        classes="form-input",
                    )

            with Vertical(classes="settings-section"):
                yield Static("API Tokens", classes="section-title")

                with Horizontal(classes="form-row"):
                    yield Label("Crowdin Token:", classes="form-label")
                    yield Input(
                        value=profile.crowdin_token or "",
                        id="input-crowdin-token",
                        classes="form-input",
                        password=True,
                    )

            with Horizontal(id="button-row"):
                yield Button("💾 Save", id="btn-save", variant="success")
                yield Button("🔙 Back", id="btn-back", variant="default")

        yield Footer()

    def _compose_profile_tab(self) -> ComposeResult:
        """Compose the profile settings tab."""
        profile = self.config.current_profile

        with Vertical(classes="settings-section"):
            yield Static("Profile Information", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("Profile Name:", classes="form-label")
                yield Input(
                    value=profile.name,
                    id="input-profile-name",
                    classes="form-input",
                    validators=[Length(minimum=1)],
                )

            with Horizontal(classes="form-row"):
                yield Label("Project ID:", classes="form-label")
                yield Input(
                    value=profile.project_id,
                    id="input-project-id",
                    classes="form-input",
                    placeholder="e.g., 577773",
                )

    def _compose_paths_tab(self) -> ComposeResult:
        """Compose the paths settings tab."""
        profile = self.config.current_profile

        with Vertical(classes="settings-section"):
            yield Static("File Paths", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("Data Path:", classes="form-label")
                yield Input(
                    value=profile.data_path,
                    id="input-data-path",
                    classes="form-input",
                    placeholder="GSSKPIM-1 (translations)/",
                )

            with Horizontal(classes="form-row"):
                yield Label("Result Path:", classes="form-label")
                yield Input(
                    value=profile.result_path,
                    id="input-result-path",
                    classes="form-input",
                    placeholder="i18n/default/",
                )

            with Horizontal(classes="form-row"):
                yield Label("Keys File:", classes="form-label")
                yield Input(
                    value=profile.key_path,
                    id="input-key-path",
                    classes="form-input",
                    placeholder="keys.txt",
                )

            with Horizontal(classes="form-row"):
                yield Label("Prompts File:", classes="form-label")
                yield Input(
                    value=profile.prompts_path,
                    id="input-prompts-path",
                    classes="form-input",
                    placeholder="prompts.txt",
                )

    def _compose_tokens_tab(self) -> ComposeResult:
        """Compose the API tokens tab."""
        profile = self.config.current_profile

        with Vertical(classes="settings-section"):
            yield Static(
                "API Tokens (stored securely in system keyring)",
                classes="section-title",
            )

            with Horizontal(classes="form-row"):
                yield Label("Crowdin Token:", classes="form-label")
                yield Input(
                    value=profile.crowdin_token or "",
                    id="input-crowdin-token",
                    classes="form-input",
                    password=True,
                    placeholder="Enter Crowdin API token",
                )

            with Horizontal(classes="form-row"):
                yield Label("Gemini Token:", classes="form-label")
                yield Input(
                    value=profile.gemini_token or "",
                    id="input-gemini-token",
                    classes="form-input",
                    password=True,
                    placeholder="Enter Gemini API token (for translations)",
                )

            yield Static(
                "💡 Tokens are stored in the config file (base64 obfuscated).\n"
                "   Keep the config file secure.",
                classes="form-hint",
            )

    def _compose_manage_tab(self) -> ComposeResult:
        """Compose the profile management tab."""
        with Vertical(classes="settings-section"):
            yield Static("Create New Profile", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("New Name:", classes="form-label")
                yield Input(
                    value="",
                    id="input-new-profile",
                    classes="form-input",
                    placeholder="Enter new profile name",
                )

            yield Button("➕ Create Profile", id="btn-create-profile", variant="primary")

        with Vertical(classes="settings-section"):
            yield Static("Delete Profile", classes="section-title")
            yield Static(
                "⚠️ The 'default' profile cannot be deleted.",
                classes="form-hint",
            )
            yield Button("🗑️ Delete Current Profile", id="btn-delete-profile", variant="error")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle profile selection change."""
        if event.select.id == "profile-select":
            self.config.active_profile = str(event.value)
            # Refresh the screen to show new profile values
            self.app.pop_screen()
            self.app.push_screen(SettingsScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-save":
            self._save_settings()

        elif button_id == "btn-back":
            self.app.pop_screen()

        elif button_id == "btn-create-profile":
            self._create_profile()

        elif button_id == "btn-delete-profile":
            self._delete_profile()

    def _save_settings(self) -> None:
        """Save current settings to config."""
        profile = self.config.current_profile

        # Get values from inputs
        profile_name = self.query_one("#input-profile-name", Input).value
        project_id = self.query_one("#input-project-id", Input).value
        data_path = self.query_one("#input-data-path", Input).value
        result_path = self.query_one("#input-result-path", Input).value
        key_path = self.query_one("#input-key-path", Input).value
        prompts_path = self.query_one("#input-prompts-path", Input).value
        crowdin_token = self.query_one("#input-crowdin-token", Input).value
        gemini_token = self.query_one("#input-gemini-token", Input).value

        # Update profile
        profile.project_id = project_id
        profile.data_path = data_path
        profile.result_path = result_path
        profile.key_path = key_path
        profile.prompts_path = prompts_path

        # Update tokens (stored in keyring)
        if crowdin_token:
            profile.crowdin_token = crowdin_token
        if gemini_token:
            profile.gemini_token = gemini_token

        # Handle profile rename
        if profile_name != profile.name:
            old_name = profile.name
            profile.name = profile_name
            del self.config.profiles[old_name]
            self.config.profiles[profile_name] = profile
            self.config.active_profile = profile_name

        # Save to disk
        self.config.save()
        self.notify("✅ Settings saved successfully!", title="Saved")

    def _create_profile(self) -> None:
        """Create a new profile."""
        new_name = self.query_one("#input-new-profile", Input).value.strip()

        if not new_name:
            self.notify("❌ Please enter a profile name", severity="error")
            return

        if new_name in self.config.profiles:
            self.notify(f"❌ Profile '{new_name}' already exists", severity="error")
            return

        # Create new profile with default values
        new_profile = Profile(name=new_name)
        self.config.add_profile(new_profile)
        self.config.active_profile = new_name
        self.config.save()

        self.notify(f"✅ Profile '{new_name}' created!", title="Success")

        # Refresh screen
        self.app.pop_screen()
        self.app.push_screen(SettingsScreen())

    def _delete_profile(self) -> None:
        """Delete the current profile."""
        profile_name = self.config.active_profile

        if profile_name == "default":
            self.notify("❌ Cannot delete the default profile", severity="error")
            return

        if self.config.delete_profile(profile_name):
            self.config.save()
            self.notify(f"✅ Profile '{profile_name}' deleted!", title="Deleted")

            # Refresh screen
            self.app.pop_screen()
            self.app.push_screen(SettingsScreen())
        else:
            self.notify("❌ Failed to delete profile", severity="error")
