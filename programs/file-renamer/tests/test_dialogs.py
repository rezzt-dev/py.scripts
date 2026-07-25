"""Tests de los diálogos nativos de selección de carpeta."""

from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

from simple_file_renamer.ui.dialogs import select_folder_native


@pytest.fixture
def no_native_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simula que ninguna herramienta de diálogo nativo está disponible."""
    monkeypatch.setattr("simple_file_renamer.ui.dialogs.shutil.which", lambda _cmd: None)


@pytest.fixture
def linux_platform(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simula que la plataforma es Linux."""
    monkeypatch.setattr("simple_file_renamer.ui.dialogs.platform.system", lambda: "Linux")


def test_select_folder_native_returns_none_when_no_tools_available(
    linux_platform, no_native_tools
) -> None:
    result = select_folder_native()
    assert result is None


def test_select_folder_native_uses_zenity(
    monkeypatch: pytest.MonkeyPatch, linux_platform
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.dialogs.shutil.which",
        lambda cmd: "/usr/bin/zenity" if cmd == "zenity" else None,
    )

    def fake_run(cmd: list[str], **kwargs) -> MagicMock:
        output = MagicMock()
        output.returncode = 0
        output.stdout = "/home/user/docs\n"
        return output

    monkeypatch.setattr("simple_file_renamer.ui.dialogs.subprocess.run", fake_run)

    result = select_folder_native(title="Elegir carpeta")
    assert result == "/home/user/docs"


def test_select_folder_native_falls_back_to_kdialog(
    monkeypatch: pytest.MonkeyPatch, linux_platform
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.dialogs.shutil.which",
        lambda cmd: "/usr/bin/kdialog" if cmd == "kdialog" else None,
    )

    def fake_run(cmd: list[str], **kwargs) -> MagicMock:
        output = MagicMock()
        output.returncode = 0
        output.stdout = "/home/user/projects\n"
        return output

    monkeypatch.setattr("simple_file_renamer.ui.dialogs.subprocess.run", fake_run)

    result = select_folder_native()
    assert result == "/home/user/projects"


def test_select_folder_native_returns_none_on_cancel(
    monkeypatch: pytest.MonkeyPatch, linux_platform
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.dialogs.shutil.which",
        lambda cmd: "/usr/bin/zenity" if cmd == "zenity" else None,
    )

    def fake_run(cmd: list[str], **kwargs) -> MagicMock:
        output = MagicMock()
        output.returncode = 1  # Cancelado por el usuario
        output.stdout = ""
        return output

    monkeypatch.setattr("simple_file_renamer.ui.dialogs.subprocess.run", fake_run)

    result = select_folder_native()
    assert result is None


def test_select_folder_native_catches_subprocess_errors(
    monkeypatch: pytest.MonkeyPatch, linux_platform
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.dialogs.shutil.which",
        lambda cmd: "/usr/bin/zenity" if cmd == "zenity" else None,
    )
    monkeypatch.setattr(
        "simple_file_renamer.ui.dialogs.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    result = select_folder_native()
    assert result is None


def test_select_folder_native_ignores_empty_stdout(
    monkeypatch: pytest.MonkeyPatch, linux_platform
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.dialogs.shutil.which",
        lambda cmd: "/usr/bin/zenity" if cmd == "zenity" else None,
    )

    def fake_run(cmd: list[str], **kwargs) -> MagicMock:
        output = MagicMock()
        output.returncode = 0
        output.stdout = "   \n"
        return output

    monkeypatch.setattr("simple_file_renamer.ui.dialogs.subprocess.run", fake_run)

    result = select_folder_native()
    assert result is None
