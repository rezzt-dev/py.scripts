"""Fixtures y utilidades compartidas para los tests."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def temp_folder(tmp_path: Path) -> Path:
    """Crea una carpeta temporal vacía para los tests."""
    return tmp_path


@pytest.fixture
def sample_files(temp_folder: Path) -> Path:
    """Crea una carpeta temporal con varios archivos de ejemplo."""
    (temp_folder / "file1.txt").write_text("content1")
    (temp_folder / "file2.txt").write_text("content2")
    (temp_folder / "doc.docx").write_text("content3")
    (temp_folder / "subfolder").mkdir()
    return temp_folder


def list_files(folder: Path) -> list[str]:
    """Devuelve los nombres de los archivos de una carpeta."""
    return sorted(f.name for f in folder.iterdir() if f.is_file())


def read_file(folder: Path, name: str) -> str:
    """Lee el contenido de un archivo de una carpeta."""
    return (folder / name).read_text()
