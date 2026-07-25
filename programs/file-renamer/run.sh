#!/usr/bin/env bash
# Lanza SimpleFileRenamer usando el entorno virtual local sin necesidad de activarlo manualmente.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
ENTRYPOINT="$VENV_DIR/bin/simple-file-renamer"

if [ ! -d "$VENV_DIR" ]; then
    echo "[ERROR] No se encontró el entorno virtual en: $VENV_DIR"
    echo "Crea e instala el proyecto con:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -e ."
    exit 1
fi

if [ ! -f "$ENTRYPOINT" ]; then
    echo "[ERROR] El paquete no está instalado en el entorno virtual."
    echo "Instálalo con:"
    echo "  source venv/bin/activate"
    echo "  pip install -e ."
    exit 1
fi

exec "$ENTRYPOINT" "$@"
