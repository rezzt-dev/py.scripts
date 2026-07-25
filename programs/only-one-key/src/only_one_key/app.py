 # main entry point ->

from __future__ import annotations

import sys

import typer

from only_one_key import __version__
from only_one_key.ui import console
from only_one_key.ui.main_menu import run


app = typer.Typer(help="only one key - gestor de contrasenas personal en consola.")


@app.callback(invoke_without_command=True)
def entryPoint(
  version: bool = typer.Option(False, "--version", "-v", help="muestra la version y sale."),
) -> None:
  """punto de entrada principal. arranca el menu interactivo si no se pide la version."""
  if version:
    console.console.print(f"[bold white]only one key[/bold white] version {__version__}")
    raise typer.Exit()

  try:
    run()
  except KeyboardInterrupt:
    console.clearScreen()
    console.printWarning("operacion cancelada por el usuario.")
    sys.exit(0)
  except Exception as exc:
    console.printError(f"error critico: {exc}")
    sys.exit(1)


 # secure function boot ->
if __name__ == "__main__":
  app()
