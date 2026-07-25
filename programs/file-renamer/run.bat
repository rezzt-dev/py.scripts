@echo off
setlocal enabledelayedexpansion

rem Lanzador de SimpleFileRenamer para Windows.
rem Usa el entorno virtual local (venv\) sin necesidad de activarlo manualmente.

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "ENTRYPOINT=%VENV_DIR%\Scripts\simple-file-renamer.exe"

if not exist "%VENV_DIR%" (
    echo [ERROR] No se encontro el entorno virtual en: %VENV_DIR%
    echo Crea e instala el proyecto con:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -e .
    exit /b 1
)

if not exist "%ENTRYPOINT%" (
    echo [ERROR] El paquete no esta instalado en el entorno virtual.
    echo Instalalo con:
    echo   venv\Scripts\activate
    echo   pip install -e .
    exit /b 1
)

"%ENTRYPOINT%" %*
