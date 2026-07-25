"""Tests de los prompts interactivos."""

from typing import Optional
from unittest.mock import MagicMock

import pytest

from simple_file_renamer.ui.prompts import select_folder


def test_select_folder_uses_native_dialog_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.prompts.select_folder_native",
        lambda title: "/native/path",
    )
    # Aseguramos que no se intenta abrir Tkinter.
    monkeypatch.setattr(
        "simple_file_renamer.ui.prompts.filedialog.askdirectory",
        lambda **kwargs: pytest.fail("Tkinter no debería usarse cuando el nativo funciona"),
    )

    result = select_folder()
    assert result == "/native/path"


def test_select_folder_falls_back_to_tkinter_when_native_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.prompts.select_folder_native",
        lambda title: None,
    )
    monkeypatch.setattr(
        "simple_file_renamer.ui.prompts.filedialog.askdirectory",
        lambda **kwargs: "/tkinter/path",
    )
    # Neutralizamos la creación de ventana Tkinter.
    monkeypatch.setattr("simple_file_renamer.ui.prompts.tk.Tk", MagicMock)

    result = select_folder()
    assert result == "/tkinter/path"


def test_select_folder_returns_none_when_user_cancels_both(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "simple_file_renamer.ui.prompts.select_folder_native",
        lambda title: None,
    )
    monkeypatch.setattr(
        "simple_file_renamer.ui.prompts.filedialog.askdirectory",
        lambda **kwargs: "",
    )
    monkeypatch.setattr("simple_file_renamer.ui.prompts.tk.Tk", MagicMock)

    result = select_folder()
    assert result is None
