"""Tests de la lógica pura de renombrado."""

from pathlib import Path

import pytest

from simple_file_renamer.core.renamer import rename_files
from simple_file_renamer.exceptions import FolderNotFoundError, RenameError


def test_rename_multiple_files(sample_files: Path) -> None:
    result = rename_files(sample_files, "document")

    assert result.count == 3
    assert result.errors == []
    assert list_files(sample_files) == [
        "document-001.docx",
        "document-002.txt",
        "document-003.txt",
    ]


def test_preserves_file_content(sample_files: Path) -> None:
    original = {f.name: f.read_text() for f in sample_files.iterdir() if f.is_file()}

    rename_files(sample_files, "backup")

    renamed = {f.name: f.read_text() for f in sample_files.iterdir() if f.is_file()}
    assert set(original.values()) == set(renamed.values())


def test_empty_folder(temp_folder: Path) -> None:
    result = rename_files(temp_folder, "empty")

    assert result.count == 0
    assert result.errors == []


def test_folder_does_not_exist() -> None:
    with pytest.raises(FolderNotFoundError):
        rename_files("/non/existent/folder", "document")


def test_empty_base_name(sample_files: Path) -> None:
    with pytest.raises(ValueError, match="nombre base no puede estar vacío"):
        rename_files(sample_files, "   ")


def test_collision_is_reported_as_error(sample_files: Path) -> None:
    # Forzamos una colisión creando el archivo destino antes del renombrado.
    # Con orden alfabético: doc.docx → document-001.docx, file1.txt → document-002.txt, ...
    (sample_files / "document-002.txt").write_text("collision")

    result = rename_files(sample_files, "document")

    assert result.count == 3
    assert len(result.errors) == 1
    error = result.errors[0]
    assert isinstance(error, RenameError)
    assert "document-002.txt" in error.message
    assert "document-004.txt" in [new_name for _, new_name in result.renamed]


def test_different_sequence_width(sample_files: Path) -> None:
    result = rename_files(sample_files, "img", sequence_width=5)

    assert result.count == 3
    assert list_files(sample_files) == [
        "img-00001.docx",
        "img-00002.txt",
        "img-00003.txt",
    ]


def test_ignores_hidden_files_when_configured(sample_files: Path) -> None:
    (sample_files / ".hidden.txt").write_text("secret")

    result = rename_files(sample_files, "doc", include_hidden=False)

    renamed_names = [new_name for _, new_name in result.renamed]
    assert ".hidden.txt" not in renamed_names
    assert ".hidden.txt" in [f.name for f in sample_files.iterdir() if f.is_file()]
    assert result.count == 3


# Helpers locales (no reexportados desde conftest para mantener tests explícitos).
def list_files(folder: Path) -> list[str]:
    return sorted(f.name for f in folder.iterdir() if f.is_file())
