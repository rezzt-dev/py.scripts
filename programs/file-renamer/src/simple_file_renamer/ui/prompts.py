"""Prompts interactivos: selección de carpeta, preguntas y lectura de teclado."""

from typing import Optional

import tkinter as tk
from tkinter import filedialog

from simple_file_renamer.ui.dialogs import select_folder_native
from simple_file_renamer.utils.keyboard import parse_yes_no, wait_key


def select_folder(title: str = "Selecciona la carpeta") -> Optional[str]:
    """Abre un diálogo para elegir una carpeta.

    Intenta usar primero el diálogo nativo del sistema operativo (zenity, kdialog,
    osascript o PowerShell). Si no está disponible, hace fallback a Tkinter.

    Args:
        title: Título del diálogo.

    Returns:
        Ruta de la carpeta seleccionada, o None si el usuario cancela.
    """
    selected = select_folder_native(title=title)
    if selected is not None and str(selected).strip() != "":
        return str(selected).strip()
    return _select_folder_tkinter(title=title)


def _select_folder_tkinter(title: str = "Selecciona la carpeta") -> Optional[str]:
    """Abre el diálogo de selección de carpeta de Tkinter."""
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)

    selected = filedialog.askdirectory(title=title)
    root.destroy()

    if selected is None or str(selected).strip() == "":
        return None
    return str(selected)


def ask_base_name() -> str:
    """Solicita el nombre base al usuario.

    Returns:
        Nombre base introducido, vacío si el usuario no escribe nada.
    """
    return input(
        " -> Introduce el nuevo nombre de los ficheros (ejemplo: 'fichero'-001.docx): "
    ).strip()


def ask_continue(default: bool = False) -> bool:
    """Pregunta al usuario si desea repetir el proceso.

    Args:
        default: Valor por defecto si el usuario pulsa Enter.

    Returns:
        True si el usuario quiere continuar, False en caso contrario.
    """
    default_text = "s" if default else "n"
    answer = input(f"  -> ¿Quieres renombrar más ficheros? s/n (default: {default_text}): ")
    return parse_yes_no(answer, default=default)


def wait_for_key(message: str = "Pulsa cualquier tecla para cerrar el programa...") -> None:
    """Muestra un mensaje y espera a que el usuario pulse una tecla."""
    print(f"\n{message}")
    wait_key()
