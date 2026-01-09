"""Download screen for Hermes TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    ProgressBar,
    RichLog,
    Static,
)
from textual.worker import Worker, get_current_worker

from hermes.core.config import Config, get_config
from hermes.core.crowdin_api import CrowdinAPI, CrowdinError
from hermes.core.file_operations import (
    extract_and_replace_files,
    process_language_files,
)


class DownloadScreen(Screen):
    """Screen for downloading translations from Crowdin."""

    BINDINGS = [
        Binding("up", "focus_previous", "Up", show=False),
        Binding("down", "focus_next", "Down", show=False),
        Binding("k", "focus_previous", "Up", show=False),
        Binding("j", "focus_next", "Down", show=False),
        Binding("escape", "cancel_selection", "Cancel", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.config: Config = get_config()
        self._operation_running = False
        self._log_content: list[str] = []
        # Profile selection state
        self._selecting_profile = False
        self._profile_list: list[str] = []
        self._profile_index = 0

    def compose(self) -> ComposeResult:
        """Compose the download screen layout."""
        yield Header()

        with Container(id="operation-container"):
            yield Static("📥 Download Translations", id="operation-title")

            with Horizontal(id="main-layout"):
                # Left panel - controls
                with Vertical(id="left-panel"):
                    yield Button(
                        f"Profile: {self.config.active_profile}",
                        id="btn-profile",
                        variant="default",
                    )
                    yield Button("▶ Start", id="btn-start", variant="success")
                    yield Button("Back", id="btn-back", variant="default")

                # Right panel - output
                with Vertical(id="right-panel"):
                    with Vertical(id="log-container"):
                        yield RichLog(id="log-view", highlight=True, markup=True)

                    with Horizontal(id="status-container"):
                        yield Static("Ready", id="status-label")
                        yield ProgressBar(total=100, show_eta=False, id="progress-bar")

        yield Footer()

    def on_mount(self) -> None:
        """Focus the profile button when screen mounts."""
        self.query_one("#btn-profile", Button).focus()

    def action_focus_next(self) -> None:
        """Move focus to next widget or profile item."""
        if self._selecting_profile:
            self._move_profile_selection(1)
        else:
            self.focus_next()

    def action_focus_previous(self) -> None:
        """Move focus to previous widget or profile item."""
        if self._selecting_profile:
            self._move_profile_selection(-1)
        else:
            self.focus_previous()

    def action_cancel_selection(self) -> None:
        """Cancel profile selection and return to sidebar."""
        if self._selecting_profile:
            self._exit_profile_selection()
            self.query_one("#btn-profile", Button).focus()

    def _move_profile_selection(self, delta: int) -> None:
        """Move the profile selection cursor."""
        if not self._profile_list:
            return
        self._profile_index = (self._profile_index + delta) % len(self._profile_list)
        self._render_profile_list()

    def _enter_profile_selection(self) -> None:
        """Enter profile selection mode."""
        self._selecting_profile = True
        self._profile_list = list(self.config.profiles.keys())
        try:
            self._profile_index = self._profile_list.index(self.config.active_profile)
        except ValueError:
            self._profile_index = 0
        self._render_profile_list()

    def _render_profile_list(self) -> None:
        """Render the profile list in the log view."""
        log = self.log_view
        log.clear()

        log.write("[bold cyan]━━━ Select Profile ━━━[/bold cyan]")
        log.write("")
        log.write("[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]")
        log.write("")

        for i, profile_name in enumerate(self._profile_list):
            profile = self.config.profiles[profile_name]
            if i == self._profile_index:
                # Highlighted selection
                log.write(f"[bold reverse] ▸ {profile_name} [/bold reverse]")
                log.write(f"    [dim]Project: {profile.project_id}[/dim]")
                log.write(f"    [dim]Data: {profile.data_path}[/dim]")
            else:
                log.write(f"   {profile_name}")

        log.write("")
        log.write("[dim]─────────────────────────────[/dim]")

    def _select_current_profile(self) -> None:
        """Select the currently highlighted profile."""
        if self._profile_list and 0 <= self._profile_index < len(self._profile_list):
            selected = self._profile_list[self._profile_index]
            self.config.active_profile = selected
            self.query_one("#btn-profile", Button).label = f"Profile: {selected}"
        self._exit_profile_selection()

    def _exit_profile_selection(self) -> None:
        """Exit profile selection mode."""
        self._selecting_profile = False
        log = self.log_view
        log.clear()
        # Restore previous log content
        for line in self._log_content:
            log.write(line)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-profile":
            if not self._operation_running:
                if self._selecting_profile:
                    self._select_current_profile()
                else:
                    self._enter_profile_selection()

        elif button_id == "btn-start":
            if self._selecting_profile:
                self._select_current_profile()
            elif not self._operation_running:
                self.start_download()

        elif button_id == "btn-back":
            if self._selecting_profile:
                self._exit_profile_selection()
            elif not self._operation_running:
                self.app.pop_screen()
            else:
                self.notify("⚠️ Please wait for the operation to complete", severity="warning")

    def on_key(self, event) -> None:
        """Handle key events for profile selection."""
        if self._selecting_profile and event.key == "enter":
            self._select_current_profile()
            event.prevent_default()
            event.stop()

    def start_download(self) -> None:
        """Start the download operation."""
        profile = self.config.current_profile

        # Validate configuration
        if not profile.crowdin_token:
            self.notify("❌ Crowdin API token not configured!", severity="error")
            self.log_message(
                "[red]Error: Crowdin API token not configured. Go to Settings to add it.[/red]"
            )
            return

        self._operation_running = True
        self._log_content.clear()
        self.log_view.clear()
        self.query_one("#btn-start", Button).disabled = True
        self.update_status("Starting download...")
        self.log_message("[blue]Starting download operation...[/blue]")

        # Run download in background worker
        self.run_download_worker()

    @property
    def log_view(self) -> RichLog:
        """Get the log view widget."""
        return self.query_one("#log-view", RichLog)

    def log_message(self, message: str) -> None:
        """Add a message to the log view."""
        self._log_content.append(message)
        self.log_view.write(message)

    def update_status(self, status: str) -> None:
        """Update the status label."""
        self.query_one("#status-label", Static).update(f"Status: {status}")

    def update_progress(self, value: int) -> None:
        """Update the progress bar."""
        self.query_one("#progress-bar", ProgressBar).update(progress=value)

    def run_download_worker(self) -> Worker:
        """Run the download operation in a background worker."""
        return self.run_worker(self._download_task, exclusive=True, thread=True)

    async def _download_task(self) -> None:
        """Background task for downloading translations."""
        worker = get_current_worker()
        profile = self.config.current_profile

        try:
            # Step 1: Initialize API
            self.app.call_from_thread(self.log_message, "[cyan]Initializing Crowdin API...[/cyan]")
            self.app.call_from_thread(self.update_progress, 5)

            api = CrowdinAPI(profile.crowdin_token, profile.project_id)

            # Step 2: Initiate build
            self.app.call_from_thread(self.log_message, "[cyan]Initiating translation build...[/cyan]")
            self.app.call_from_thread(self.update_status, "Initiating build...")
            self.app.call_from_thread(self.update_progress, 10)

            build_id = api.initiate_build()
            self.app.call_from_thread(
                self.log_message, f"[green]Build initiated. ID: {build_id}[/green]"
            )

            # Step 3: Wait for build to complete
            self.app.call_from_thread(self.log_message, "[cyan]Waiting for build to complete...[/cyan]")
            self.app.call_from_thread(self.update_status, "Building translations...")

            def build_progress(progress):
                self.app.call_from_thread(
                    self.log_message,
                    f"[dim]Build progress: {progress.status} - {progress.progress}%[/dim]",
                )
                # Map build progress to 10-50% of total
                mapped_progress = 10 + int(progress.progress * 0.4)
                self.app.call_from_thread(self.update_progress, mapped_progress)

            api.check_build_status(build_id, progress_callback=build_progress)
            self.app.call_from_thread(self.log_message, "[green]Build completed successfully![/green]")

            # Step 4: Download build
            self.app.call_from_thread(self.log_message, "[cyan]Downloading translations...[/cyan]")
            self.app.call_from_thread(self.update_status, "Downloading...")
            self.app.call_from_thread(self.update_progress, 55)

            def download_progress(percent):
                # Map download progress to 55-75% of total
                mapped_progress = 55 + int(percent * 0.2)
                self.app.call_from_thread(self.update_progress, mapped_progress)

            zip_path = api.download_build(build_id, progress_callback=download_progress)
            self.app.call_from_thread(self.log_message, f"[green]Downloaded to: {zip_path}[/green]")

            # Step 5: Extract files
            self.app.call_from_thread(self.log_message, "[cyan]Extracting files...[/cyan]")
            self.app.call_from_thread(self.update_status, "Extracting...")
            self.app.call_from_thread(self.update_progress, 80)

            extract_and_replace_files(zip_path, profile.data_path)
            self.app.call_from_thread(
                self.log_message, f"[green]Extracted to: {profile.data_path}[/green]"
            )

            # Step 6: Process language files
            self.app.call_from_thread(self.log_message, "[cyan]Processing language files...[/cyan]")
            self.app.call_from_thread(self.update_status, "Processing...")
            self.app.call_from_thread(self.update_progress, 90)

            def process_progress(lang, current, total):
                self.app.call_from_thread(
                    self.log_message,
                    f"[dim]Processing {lang} ({current}/{total})[/dim]",
                )

            processed = process_language_files(
                profile.data_path,
                profile.result_path,
                progress_callback=process_progress,
            )

            # Complete
            self.app.call_from_thread(self.update_progress, 100)
            self.app.call_from_thread(self.update_status, "Complete!")
            self.app.call_from_thread(
                self.log_message,
                f"[bold green]✅ Download complete! Processed {len(processed)} languages.[/bold green]",
            )

            for lang in processed:
                self.app.call_from_thread(self.log_message, f"  • {lang}")

        except CrowdinError as e:
            self.app.call_from_thread(self.log_message, f"[bold red]❌ Error: {e}[/bold red]")
            self.app.call_from_thread(self.update_status, "Error!")
            self.app.call_from_thread(self.notify, f"Download failed: {e}", severity="error")

        except Exception as e:
            self.app.call_from_thread(
                self.log_message, f"[bold red]❌ Unexpected error: {e}[/bold red]"
            )
            self.app.call_from_thread(self.update_status, "Error!")
            self.app.call_from_thread(self.notify, f"Unexpected error: {e}", severity="error")

        finally:
            self.app.call_from_thread(self._finish_operation)

    def _finish_operation(self) -> None:
        """Clean up after operation completes."""
        self._operation_running = False
        self.query_one("#btn-start", Button).disabled = False
