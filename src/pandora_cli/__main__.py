"""Command line interface for pandora."""
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import Any

import questionary
import typer
from pandora.errors import ErrorMessage
from pandora.offline import env
from pandora.platforms import detect_platform
from pandora.platforms.base import OSType
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Utilities for managing Pandora environments.")
console: Any = Console()


def _print_banner() -> None:
    """Print a welcome banner with the package version."""
    version = importlib.metadata.version("pandora")
    console.print(f"[bold magenta]Pandora[/] v{version}")


env_app = typer.Typer()
app.add_typer(env_app, name="env")


def version_callback(value: bool) -> bool:
    if value:
        _print_banner()
        raise typer.Exit()
    return value


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        help="Show version and exit.",
        is_eager=True,
    ),
) -> None:
    """Pandora command line interface."""
    return


@env_app.command("apply")
def apply(
    file: Path = typer.Option(..., "--file", "-f", help="Path to env var file."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without writing."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Apply without confirmation."),
) -> None:
    """Apply environment variables from a file."""
    data = env.config_reader(file)
    if isinstance(data, ErrorMessage):
        console.print(f"[bold red]{data.msg}[/]")
        raise typer.Exit(1)

    table: Any = Table(title="Planned Changes")
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


if __name__ == "__main__":
    app()
