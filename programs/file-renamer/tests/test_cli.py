"""Tests del CLI con Typer CliRunner."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from simple_file_renamer.cli import app

runner = CliRunner()


def test_help_shows_usage() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Renombra" in result.output
    assert "OPTIONS" in result.output


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_batch_rename_success(temp_folder: Path) -> None:
    (temp_folder / "a.txt").write_text("a")
    (temp_folder / "b.txt").write_text("b")

    result = runner.invoke(app, ["--folder", str(temp_folder), "--base", "file"])

    assert result.exit_code == 0, result.output
    files = sorted(f.name for f in temp_folder.iterdir() if f.is_file())
    assert files == ["file-001.txt", "file-002.txt"]


def test_batch_rename_requires_folder() -> None:
    result = runner.invoke(app, ["--base", "file", "--no-interactive"])
    assert result.exit_code != 0
    assert "--folder" in result.output


def test_batch_rename_requires_base() -> None:
    result = runner.invoke(app, ["--folder", "/tmp", "--no-interactive"])
    assert result.exit_code != 0
    assert "--base" in result.output


def test_batch_rename_reports_error_for_missing_folder() -> None:
    result = runner.invoke(app, ["--folder", "/non/existent/folder", "--base", "file", "--no-interactive"])
    assert result.exit_code == 1
    assert "no existe" in result.output
