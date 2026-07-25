"""Punto de entrada CLI de SimpleFileRenamer."""

from __future__ import annotations

import threading
import time
from typing import Optional

import typer
from rich.console import Console

from simple_file_renamer import __version__
from simple_file_renamer.config import APP_NAME
from simple_file_renamer.core.renamer import RenameResult, rename_files
from simple_file_renamer.exceptions import FolderNotFoundError
from simple_file_renamer.ui.console import (
    clear_screen,
    get_console,
    print_errors,
    print_result,
    print_title,
)
from simple_file_renamer.ui.prompts import ask_base_name, ask_continue, select_folder, wait_for_key
from simple_file_renamer.utils.spinner import loading_animation

app = typer.Typer(help=f"{APP_NAME}: renombra masivamente los archivos de una carpeta.")


def _version_callback(value: bool) -> None:
    """Callback de la opción --version. Muestra la versión y termina."""
    if value:
        typer.echo(f"{APP_NAME} {__version__}")
        raise typer.Exit()


@app.command()
def main(
    folder: Optional[str] = typer.Option(
        None,
        "--folder",
        "-f",
        help="Carpeta objetivo. Si no se indica, se abre el diálogo de selección.",
    ),
    base: Optional[str] = typer.Option(
        None,
        "--base",
        "-b",
        help="Nombre base para los archivos renombrados. Si no se indica, se pregunta.",
    ),
    interactive: Optional[bool] = typer.Option(
        None,
        "--interactive/--no-interactive",
        "-i/-I",
        help="Modo interactivo. Por defecto se infiere de los argumentos proporcionados.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Muestra la versión y sale.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Renombra masivamente los archivos de una carpeta.

    En modo interactivo (por defecto cuando faltan argumentos) se abre un diálogo
    gráfico de selección de carpeta y se solicita el nombre base por consola.
    En modo no interactivo se usan los valores de --folder y --base.
    """
    console = get_console()

    # Determinar modo: interactivo si no se han dado ambos argumentos y no se forzó --no-interactive.
    if interactive is None:
        interactive_mode = folder is None or base is None
    else:
        interactive_mode = interactive

    if interactive_mode:
        _run_interactive(console)
    else:
        if folder is None:
            raise typer.BadParameter("--folder es obligatorio en modo no interactivo.")
        if base is None:
            raise typer.BadParameter("--base es obligatorio en modo no interactivo.")
        _run_batch(folder, base, console)


def _run_batch(folder: str, base: str, console: Console) -> None:
    """Ejecuta una operación de renombrado no interactiva."""
    try:
        result = _rename_with_spinner(folder, base, console)
    except FolderNotFoundError as exc:
        console.print(f"[bold red] [!] {exc} [/bold red]")
        raise typer.Exit(code=1) from exc

    print_result(result, console)
    print_errors(result, console)

    if len(result.errors) > 0:
        raise typer.Exit(code=2)


def _run_interactive(console: Console) -> None:
    """Ejecuta el bucle interactivo de la aplicación."""
    while True:
        clear_screen()
        print_title(console)

        console.print("[bold white] [*] Selecciona la carpeta que contiene los ficheros: [/bold white]")
        selected_folder = select_folder()

        if selected_folder is None:
            console.print(
                "[bold yellow] [!] No se seleccionó ninguna carpeta. Volviendo al inicio... [/bold yellow]"
            )
            time.sleep(1.5)
            continue

        console.print(f"[bold green]  => Carpeta seleccionada: {selected_folder}[/bold green]")

        base_name = ask_base_name()
        if base_name == "":
            console.print(
                "[bold yellow] [!] El nombre base no puede estar vacío. Volviendo al inicio... [/bold yellow]"
            )
            time.sleep(1.5)
            continue

        try:
            result = _rename_with_spinner(selected_folder, base_name, console)
        except FolderNotFoundError as exc:
            console.print(f"[bold red] [!] {exc} [/bold red]")
            time.sleep(1.5)
            continue
        except Exception as exc:
            console.print(f"[bold red] [!] ERROR CRÍTICO: {exc} [/bold red]")
            time.sleep(1.5)
            continue

        print_result(result, console)
        print_errors(result, console)

        if not ask_continue(default=False):
            console.print("\n[bold yellow] [+] Pulsa cualquier tecla para cerrar el programa...[/bold yellow]")
            wait_for_key()
            break


def _rename_with_spinner(folder: str, base: str, console: Console) -> RenameResult:
    """Ejecuta el renombrado mostrando una animación de carga."""
    stop_event = threading.Event()
    animation_thread = threading.Thread(
        target=loading_animation,
        args=(stop_event,),
        kwargs={"message": "Renombrando archivos...", "console": console},
    )
    animation_thread.start()

    try:
        result = rename_files(folder, base)
    finally:
        stop_event.set()
        animation_thread.join()

    return result


if __name__ == "__main__":
    app()
