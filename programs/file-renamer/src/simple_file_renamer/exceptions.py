"""Excepciones de dominio del renombrador."""


class SimpleFileRenamerError(Exception):
    """Excepción base para la herramienta."""


class FolderNotFoundError(SimpleFileRenamerError):
    """La carpeta indicada no existe o no es accesible."""


class RenameError(SimpleFileRenamerError):
    """Error al renombrar un archivo concreto."""

    def __init__(self, original_name: str, message: str) -> None:
        super().__init__(message)
        self.original_name = original_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.original_name}: {self.message}"
