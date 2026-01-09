"""CLI interface for Hermes using Typer."""

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from hermes.core.config import Profile, get_config, get_config_path
from hermes.core.crowdin_api import CrowdinAPI, CrowdinError
from hermes.core.crowdin_upload_api import CrowdinUploadAPI
from hermes.core.file_operations import (
    extract_and_replace_files,
    process_language_files,
)

app = typer.Typer(
    name="hermes",
    help="Hermes - Crowdin i18n translation management tool",
    add_completion=False,
)
console = Console()

# Config subcommand group
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")


@app.command()
def download(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Profile to use"),
    project_id: str | None = typer.Option(None, "--project-id", help="Override project ID"),
    data_path: str | None = typer.Option(None, "--data-path", help="Override data path"),
    result_path: str | None = typer.Option(None, "--result-path", help="Override result path"),
    token: str | None = typer.Option(
        None, "--token", "-t", help="Crowdin API token", envvar="CROWDIN_TOKEN"
    ),
):
    """Download translations from Crowdin."""
    cfg = get_config()

    # Select profile
    if profile:
        if profile not in cfg.profiles:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            raise typer.Exit(1)
        cfg.active_profile = profile

    p = cfg.current_profile

    # Override with CLI options
    api_token = token or p.crowdin_token
    proj_id = project_id or p.project_id
    d_path = data_path or p.data_path
    r_path = result_path or p.result_path

    if not api_token:
        console.print("[red]Error: Crowdin API token not configured.[/red]")
        console.print("Set it with: hermes config set-token --crowdin YOUR_TOKEN")
        raise typer.Exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading translations...", total=100)

            # Initialize API
            api = CrowdinAPI(api_token, proj_id)

            # Initiate build
            progress.update(task, description="Initiating build...", completed=10)
            build_id = api.initiate_build()
            console.print(f"[green]Build initiated: {build_id}[/green]")

            # Wait for build
            progress.update(task, description="Building...", completed=20)
            api.check_build_status(build_id)
            console.print("[green]Build completed[/green]")

            # Download
            progress.update(task, description="Downloading...", completed=50)
            zip_path = api.download_build(build_id)
            console.print(f"[green]Downloaded: {zip_path}[/green]")

            # Extract
            progress.update(task, description="Extracting...", completed=70)
            extract_and_replace_files(zip_path, d_path)

            # Process
            progress.update(task, description="Processing...", completed=85)
            processed = process_language_files(d_path, r_path)

            progress.update(task, description="Complete!", completed=100)

        console.print("\n[bold green]✅ Download complete![/bold green]")
        console.print(f"Processed {len(processed)} languages: {', '.join(processed)}")

    except CrowdinError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def upload(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Profile to use"),
    project_id: str | None = typer.Option(None, "--project-id", help="Override project ID"),
    data_path: str | None = typer.Option(None, "--data-path", help="Override data path"),
    key_path: str | None = typer.Option(None, "--keys", "-k", help="Path to keys file"),
    prompts_path: str | None = typer.Option(None, "--prompts", help="Path to prompts file"),
    token: str | None = typer.Option(
        None, "--token", "-t", help="Crowdin API token", envvar="CROWDIN_TOKEN"
    ),
    gemini_token: str | None = typer.Option(
        None, "--gemini-token", "-g", help="Gemini API token", envvar="GEMINI_TOKEN"
    ),
    no_download: bool = typer.Option(
        False, "--no-download", help="Skip downloading latest translations"
    ),
    no_gemini: bool = typer.Option(False, "--no-gemini", help="Skip Gemini AI translation"),
):
    """Upload translations to Crowdin with optional Gemini AI translation."""
    cfg = get_config()

    # Select profile
    if profile:
        if profile not in cfg.profiles:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            raise typer.Exit(1)
        cfg.active_profile = profile

    p = cfg.current_profile

    # Override with CLI options
    api_token = token or p.crowdin_token
    g_token = gemini_token or p.gemini_token
    proj_id = project_id or p.project_id
    d_path = data_path or p.data_path
    k_path = key_path or p.key_path
    pr_path = prompts_path or p.prompts_path

    if not api_token:
        console.print("[red]Error: Crowdin API token not configured.[/red]")
        raise typer.Exit(1)

    if not no_gemini and not g_token:
        console.print(
            "[yellow]Warning: Gemini token not configured. Skipping AI translation.[/yellow]"
        )
        no_gemini = True

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Uploading translations...", total=100)

            # Download first if not skipped
            if not no_download:
                progress.update(task, description="Downloading latest...", completed=10)
                api = CrowdinAPI(api_token, proj_id)
                build_id = api.initiate_build()
                api.check_build_status(build_id)
                zip_path = api.download_build(build_id)
                extract_and_replace_files(zip_path, d_path)
                process_language_files(d_path, p.result_path)
                console.print("[green]Downloaded latest translations[/green]")

            # Initialize upload API
            progress.update(task, description="Initializing...", completed=30)
            upload_api = CrowdinUploadAPI(
                api_token=api_token,
                project_id=proj_id,
                gemini_api_key=g_token or "",
                key_file_path=k_path,
                prompt_file_path=pr_path,
                data_path=d_path,
                log_callback=lambda msg: console.print(f"[dim]{msg}[/dim]"),
            )

            # Translate with Gemini
            if not no_gemini:
                progress.update(task, description="Translating with Gemini...", completed=50)
                translations = upload_api.translate_missing_with_gemini()
                if translations:
                    console.print(f"[green]Translated {len(translations)} languages[/green]")

            # Add keys
            progress.update(task, description="Adding keys...", completed=70)
            added = upload_api.add_keys()
            console.print(f"[green]Added {len(added)} new keys[/green]")

            # Add translations
            progress.update(task, description="Adding translations...", completed=85)
            upload_api.add_translations()

            progress.update(task, description="Complete!", completed=100)

        console.print("\n[bold green]✅ Upload complete![/bold green]")

    except CrowdinError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("show")
def config_show():
    """Show current configuration."""
    cfg = get_config()

    console.print(f"\n[bold]Config file:[/bold] {get_config_path()}")
    console.print(f"[bold]Active profile:[/bold] {cfg.active_profile}\n")

    table = Table(title="Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Project ID")
    table.add_column("Data Path")
    table.add_column("Result Path")
    table.add_column("Crowdin Token")
    table.add_column("Gemini Token")

    for name, profile in cfg.profiles.items():
        active = "* " if name == cfg.active_profile else "  "
        table.add_row(
            f"{active}{name}",
            profile.project_id,
            profile.data_path,
            profile.result_path,
            "[green]Yes[/green]" if profile.crowdin_token else "[red]No[/red]",
            "[green]Yes[/green]" if profile.gemini_token else "[red]No[/red]",
        )

    console.print(table)


@config_app.command("set-profile")
def config_set_profile(
    name: str = typer.Argument(..., help="Profile name to activate"),
):
    """Set the active profile."""
    cfg = get_config()

    if name not in cfg.profiles:
        console.print(f"[red]Profile '{name}' not found[/red]")
        raise typer.Exit(1)

    cfg.active_profile = name
    cfg.save()
    console.print(f"[green]Active profile set to: {name}[/green]")


@config_app.command("create-profile")
def config_create_profile(
    name: str = typer.Argument(..., help="New profile name"),
    project_id: str = typer.Option("577773", "--project-id", help="Crowdin project ID"),
):
    """Create a new profile."""
    cfg = get_config()

    if name in cfg.profiles:
        console.print(f"[red]Profile '{name}' already exists[/red]")
        raise typer.Exit(1)

    profile = Profile(name=name, project_id=project_id)
    cfg.add_profile(profile)
    cfg.save()
    console.print(f"[green]Created profile: {name}[/green]")


@config_app.command("delete-profile")
def config_delete_profile(
    name: str = typer.Argument(..., help="Profile name to delete"),
):
    """Delete a profile."""
    cfg = get_config()

    if name == "default":
        console.print("[red]Cannot delete the default profile[/red]")
        raise typer.Exit(1)

    if cfg.delete_profile(name):
        cfg.save()
        console.print(f"[green]Deleted profile: {name}[/green]")
    else:
        console.print(f"[red]Profile '{name}' not found[/red]")
        raise typer.Exit(1)


@config_app.command("set-token")
def config_set_token(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Profile to update"),
    crowdin: str | None = typer.Option(None, "--crowdin", help="Crowdin API token"),
    gemini: str | None = typer.Option(None, "--gemini", help="Gemini API token"),
):
    """Set API tokens for a profile (stored in config file)."""
    cfg = get_config()

    if profile:
        if profile not in cfg.profiles:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            raise typer.Exit(1)
        cfg.active_profile = profile

    p = cfg.current_profile

    if crowdin:
        p.crowdin_token = crowdin
        cfg.save()
        console.print(f"[green]Crowdin token set for profile: {p.name}[/green]")

    if gemini:
        p.gemini_token = gemini
        cfg.save()
        console.print(f"[green]Gemini token set for profile: {p.name}[/green]")

    if not crowdin and not gemini:
        console.print("[yellow]No tokens provided. Use --crowdin or --gemini[/yellow]")


@config_app.command("set")
def config_set(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Profile to update"),
    project_id: str | None = typer.Option(None, "--project-id", help="Project ID"),
    data_path: str | None = typer.Option(None, "--data-path", help="Data path"),
    result_path: str | None = typer.Option(None, "--result-path", help="Result path"),
    key_path: str | None = typer.Option(None, "--key-path", help="Keys file path"),
    prompts_path: str | None = typer.Option(None, "--prompts-path", help="Prompts file path"),
):
    """Set configuration values for a profile."""
    cfg = get_config()

    if profile:
        if profile not in cfg.profiles:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            raise typer.Exit(1)
        cfg.active_profile = profile

    p = cfg.current_profile
    updated = []

    if project_id:
        p.project_id = project_id
        updated.append("project_id")

    if data_path:
        p.data_path = data_path
        updated.append("data_path")

    if result_path:
        p.result_path = result_path
        updated.append("result_path")

    if key_path:
        p.key_path = key_path
        updated.append("key_path")

    if prompts_path:
        p.prompts_path = prompts_path
        updated.append("prompts_path")

    if updated:
        cfg.save()
        console.print(f"[green]Updated {', '.join(updated)} for profile: {p.name}[/green]")
    else:
        console.print("[yellow]No values provided to update[/yellow]")


@config_app.command("path")
def config_path():
    """Show the config file path."""
    console.print(f"Config file: {get_config_path()}")


def cli_main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    cli_main()
