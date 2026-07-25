"""Lógica pura de renombrado masivo de archivos."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from simple_file_renamer.config import SEQUENCE_WIDTH
from simple_file_renamer.exceptions import FolderNotFoundError, RenameError


@dataclass
class RenameResult:
    """Resultado de una operación de renombrado."""

    renamed: list[tuple[str, str]] = field(default_factory=list)
    errors: list[RenameError] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.renamed)


def rename_files(
    folder: str | Path,
    base_name: str,
    *,
    sequence_width: int = SEQUENCE_WIDTH,
    include_hidden: bool = True,
) -> RenameResult:
    """Renombra todos los archivos de una carpeta con un nombre base y secuencia.

    Args:
        folder: Carpeta objetivo.
        base_name: Nombre base para los archivos renombrados.
        sequence_width: Número de dígitos de la secuencia (por defecto 3).
        include_hidden: Si es False, omite archivos cuyo nombre empiece por punto.

    Returns:
        RenameResult con la lista de renombrados y errores.

    Raises:
        FolderNotFoundError: Si la carpeta no existe o no es un directorio.
        ValueError: Si el nombre base está vacío.
    """
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        raise FolderNotFoundError(f"La carpeta '{folder}' no existe o no es accesible.")

    base_name = base_name.strip()
    if not base_name:
        raise ValueError("El nombre base no puede estar vacío.")

    result = RenameResult()
    counter = 1

    # Orden determinista: listdir ordenado alfabéticamente.
    items: Iterable[Path] = sorted(folder_path.iterdir(), key=lambda p: p.name.lower())

    for item in items:
        if not item.is_file():
            continue
        if not include_hidden and item.name.startswith("."):
            continue

        extension = item.suffix
        new_name = f"{base_name}-{counter:0{sequence_width}d}{extension}"
        new_path = folder_path / new_name

        # Colisión con un archivo ya existente.
        if new_path.exists():
            result.errors.append(
                RenameError(item.name, f"El nombre destino '{new_name}' ya existe.")
            )
            counter += 1
            continue

        try:
            item.rename(new_path)
            result.renamed.append((item.name, new_name))
            counter += 1
        except OSError as exc:
            result.errors.append(RenameError(item.name, str(exc)))

    return result
