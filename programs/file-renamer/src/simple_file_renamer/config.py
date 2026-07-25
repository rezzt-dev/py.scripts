"""Configuración global de la herramienta."""

import os

APP_NAME = "SimpleFileRenamer"
VERSION = "1.0.0"

# Formato de secuencia: número de dígitos usados para enumerar archivos.
SEQUENCE_WIDTH = 3

# Iconos del spinner de carga.
SPINNER_ICONS = ["◸", "◹", "◿", "◺"]
SPINNER_DELAY = 0.2

# Limpieza de pantalla.
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
