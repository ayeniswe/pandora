from pathlib import Path

import questionary
import typer
from pandora.errors import ErrorMessage
from pandora.offline import env
from pandora.platforms import detect_platform
from pandora.platforms.base import OSType
from rich.console import Console
from rich.table import Table


def apply(
    file: Path,
    dry_run: bool,
    verbose: bool,
    yes: bool,
    console: Console,
) -> None:
    """Apply environment variables from a file."""
    data = env.config_reader(file)
    if isinstance(data, ErrorMessage):
        console.print(f"[bold red]{data.msg}[/]")
        raise typer.Exit(1)

    table = Table(title="Planned Changes")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")
    for key, value in data.items():
        table.add_row(key, value)
    console.print(table)

    if not yes:
        confirm: bool = bool(questionary.confirm("Apply these changes?", default=False).ask())
        if not confirm:
            console.print("[yellow]Aborted by user.[/]")
            raise typer.Exit(0)

    if dry_run:
        console.print("[yellow]Dry run mode: no changes applied.[/]")
        raise typer.Exit(0)

    info = detect_platform()
    if verbose:
        console.print(f"Detected platform: {info}", style="dim")

    with console.status("Applying environment variables...", spinner="dots"):
        result = env.setup_vars(info, data)

    if isinstance(result, ErrorMessage):
        console.print(f"[bold red]{result.msg}[/]")
        raise typer.Exit(1)

    console.print("[bold green]Environment variables applied successfully.[/]")
    hint = (
        "Open a new terminal to see changes."
        if info.os == OSType.WINDOWS
        else "Restart your shell to see changes."
    )
    console.print(f"[cyan]{hint}[/]")
