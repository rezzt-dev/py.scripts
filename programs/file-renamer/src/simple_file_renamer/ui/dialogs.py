"""Diálogos nativos de selección de carpeta multiplataforma."""

import platform
import shutil
import subprocess
from typing import Optional


def select_folder_native(title: str = "Selecciona una carpeta") -> Optional[str]:
    """Abre un diálogo nativo de selección de carpeta.

    Soporta:
      - Linux: zenity o kdialog.
      - macOS: osascript (AppleScript).
      - Windows: PowerShell + FolderBrowserDialog.

    Args:
        title: Título del diálogo.

    Returns:
        Ruta seleccionada, o None si el usuario cancela o no hay diálogo nativo disponible.
    """
    system = platform.system()
    try:
        if system == "Linux":
            return _select_folder_linux(title)
        if system == "Darwin":
            return _select_folder_macos(title)
        if system == "Windows":
            return _select_folder_windows(title)
    except Exception:
        return None
    return None


def _select_folder_linux(title: str) -> Optional[str]:
    """Usa zenity o kdialog en Linux."""
    if shutil.which("zenity"):
        result = subprocess.run(
            ["zenity", "--file-selection", "--directory", "--title", title],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            if path:
                return path

    if shutil.which("kdialog"):
        result = subprocess.run(
            ["kdialog", "--getexistingdirectory", ".", title],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            if path:
                return path

    return None


def _select_folder_macos(title: str) -> Optional[str]:
    """Usa osascript en macOS."""
    if not shutil.which("osascript"):
        return None

    script = f'POSIX path of (choose folder with prompt "{title}")'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = result.stdout.strip()
        if path:
            return path
    return None


def _select_folder_windows(title: str) -> Optional[str]:
    """Usa PowerShell con FolderBrowserDialog en Windows."""
    if not shutil.which("powershell"):
        return None

    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "{title}"
$dialog.ShowNewFolderButton = $true
if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {{
    Write-Output $dialog.SelectedPath
}}
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = result.stdout.strip()
        if path:
            return path
    return None
