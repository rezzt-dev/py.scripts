"""Animación de spinner en segundo plano."""

import threading
import time
from typing import Optional

from rich.console import Console

from simple_file_renamer.config import SPINNER_DELAY, SPINNER_ICONS


def loading_animation(
    stop_event: threading.Event,
    message: str = "Renombrando archivos...",
    console: Optional[Console] = None,
) -> None:
    """Muestra un spinner en la consola hasta que se active el evento de parada.

    Args:
        stop_event: Evento de threading que detiene la animación.
        message: Mensaje que acompaña al spinner.
        console: Instancia de Rich Console; si es None, se crea una nueva.
    """
    console = console or Console()
    icons = SPINNER_ICONS
    idx = 0
    while not stop_event.is_set():
        console.print(
            f"[bold blue]\r  [{icons[idx]}] {message} [/bold blue]",
            end="\r",
        )
        idx = (idx + 1) % len(icons)
        time.sleep(SPINNER_DELAY)
    console.print(" " * 70, end="\n\n")
