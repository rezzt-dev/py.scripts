"""Presentación en consola con Rich."""

import os
from typing import Optional

from rich.console import Console

from simple_file_renamer.config import APP_NAME, CLEAR_COMMAND
from simple_file_renamer.core.renamer import RenameResult


def get_console() -> Console:
    """Devuelve una instancia de Rich Console."""
    return Console()


def clear_screen() -> None:
    """Limpia la pantalla de la terminal."""
    os.system(CLEAR_COMMAND)


def print_title(console: Optional[Console] = None) -> None:
    """Muestra el título de la aplicación."""
    console = console or get_console()
    console.print(f"[bold purple] -| {APP_NAME} / Python Tool |- [/bold purple]")


def print_result(result: RenameResult, console: Optional[Console] = None) -> None:
    """Muestra el resumen del renombrado."""
    console = console or get_console()
    console.print(
        f"[bold green] [+] {result.count} Ficheros renombrados correctamente. [/bold green]"
    )

    if result.count == 0 and len(result.errors) == 0:
        console.print(
            "[bold yellow] [!] La carpeta no contiene archivos para renombrar. [/bold yellow]"
        )


def print_errors(result: RenameResult, console: Optional[Console] = None) -> None:
    """Muestra los errores producidos durante el renombrado."""
    if not result.errors:
        return

    console = console or get_console()
    console.print("[bold red] [!] Se encontraron errores durante el proceso: [/bold red]")
    for error in result.errors:
        console.print(f"[bold red]    - {error.original_name}: {error.message} [/bold red]")
