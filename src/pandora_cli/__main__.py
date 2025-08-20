# pylint: disable=invalid-name
"""Command line interface for pandora."""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import List

import typer
from pandora.common import Status
from pandora.errors import ErrorMessage
from pandora.online.ide import IDE
from rich.console import Console

from pandora_cli import env, ide


def version_callback(value: bool) -> bool:
    if value:
        version = importlib.metadata.version("pandora")
        console.print(f"[bold magenta]Pandora[/] v{version}")
        raise typer.Exit()
    return value


console = Console()

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
cli.add_typer(cli_env, name="env", help="Configure environment variables")


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
cli.add_typer(cli_ide, name="ide", help="Install and configure IDEs")


@cli_ide.command("vscode")
def vscode(
    extension: List[str] = typer.Option(
        None,
        "--ext",
        help="Optional extensions to install. Use --ext [id|path] multiple times for multiple "
        "extensions",
    ),
) -> None:
    """Install/Modify Visual Studio Code with optional extensions."""
    console.print("Setting up Visual Studio Code")

    try:
        status = ide.setup(IDE.VSCODE, extension)
    except ErrorMessage as e:
        console.print(f"[bold red]{e}[/]", highlight=False)
        return

    if status == Status.Success:
        console.print("[green]Visual Studio Code setup completed successfully[/]")
    else:
        console.print("[red]Visual Studio Code setup failed[/]")


# @cli_ide.command("idea")
# def idea(
#     extension: List[str] = typer.Option(
#         None,
#         "--plg",
#         help="Optional plugin(s) to install (comma-separated for multiple)"),
# ) -> None:
#     """Install/Modify IntelliJ IDEA with optional plugins."""
#     console.print("Setting up Intellij IDEA")
#     if ide.setup(IDE.INTELLIJ, extension):
#         console.print("Intellij IDEA setup completed successfully")
#     else:
#         console.print("Intellij IDEA setup failed")


@cli_ide.command("vs")
def vs(
    extension: List[str] = typer.Option(
        None, "--ext", help="Optional extension(s) to install (comma-separated for multiple)"
    ),
) -> None:
    """Install/Modify Visual Studio Community Edition with optional extensions."""
    console.print("Setting up Visual Studio Community")

    try:
        status = ide.setup(IDE.VS, extension)
    except ErrorMessage as e:
        console.print(f"[bold red]{e}[/]", highlight=False)
        return

    if status == Status.Success:
        console.print("[green]Visual Studio Community setup completed successfully[/]")
    else:
        console.print("[red]Visual Studio Community setup failed[/]")


if __name__ == "__main__":
    cli()
