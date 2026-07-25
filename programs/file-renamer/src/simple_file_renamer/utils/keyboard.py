"""Utilidades de consola multiplataforma."""

import platform
import sys
from typing import Optional

# Importaciones condicionales según el sistema operativo.
_SYSTEM = platform.system()

if _SYSTEM == "Windows":
    import msvcrt

    termios = None  # type: ignore
    tty = None  # type: ignore
else:
    msvcrt = None  # type: ignore
    try:
        import termios
        import tty
    except ImportError:
        termios = None  # type: ignore
        tty = None  # type: ignore


def wait_key() -> str:
    """Espera a que el usuario pulse una tecla y devuelve el carácter leído.

    Usa ``msvcrt`` en Windows, ``termios``/``tty`` en Unix, o ``input()`` como fallback.
    """
    if msvcrt is not None:
        try:
            return msvcrt.getch().decode("utf-8", errors="ignore")
        except Exception:  # pragma: no cover - fallback defensivo
            return input()

    if termios is not None and tty is not None:
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                return sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:  # pragma: no cover - fallback defensivo
            return input()

    return input()


def parse_yes_no(value: str, default: bool = False) -> bool:
    """Normaliza una respuesta de sí/no.

    Args:
        value: Cadena introducida por el usuario.
        default: Valor por defecto cuando la cadena está vacía.

    Returns:
        True para respuestas afirmativas, False para negativas.
    """
    normalized = value.strip().lower()
    if normalized == "":
        return default
    if normalized in ("s", "si", "yes", "y"):
        return True
    if normalized in ("n", "no"):
        return False
    return default
