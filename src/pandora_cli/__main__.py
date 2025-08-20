"""Command line interface for pandora."""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from pandora_cli import env, ide


def version_callback(value: bool) -> bool:
    if value:
        version = importlib.metadata.version("pandora")
        console.print(f"[bold magenta]Pandora[/] v{version}")
        raise typer.Exit()
    return value

console: Any = Console()

#### MAIN CLI
cli = typer.Typer(help="Utilities for managing Pandora environments.")
@cli.callback()
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

#### ENV COMMAND
cli_env = typer.Typer()
cli.add_typer(cli_env, name="env")
@cli_env.command("apply")
def apply(
    file: Path = typer.Option(..., "--file", "-f", help="Path to env var file."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without writing."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Apply without confirmation."),
) -> None:
    env.apply(file, dry_run, verbose, yes, console)

#### IDE COMMAND
cli_ide = typer.Typer()
cli.add_typer(cli_ide, name="ide")
@cli_ide.command("setup")
def setup(
    selection: str = typer.Option(..., "--selection", "-s", help="Selection of ide"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
) -> None:
    ide.setup(selection, verbose, console)

if __name__ == "__main__":
    cli()
