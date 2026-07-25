 # input validators ->

from __future__ import annotations

__all__ = ["validateMenuOption", "validateMinLength", "parseYesNo"]


def validateMenuOption(value: str, validOptions: range) -> int:
  """convierte y valida una opcion de menu numerica."""
  try:
    option = int(value)
  except ValueError as exc:
    raise ValueError("debes introducir un numero entero.") from exc

  if option not in validOptions:
    raise ValueError(f"opcion no valida. elige una opcion entre {validOptions.start} y {validOptions.stop - 1}.")

  return option


def validateMinLength(value: str, minLength: int, fieldName: str = "valor") -> str:
  """comprueba que una cadena cumpla una longitud minima."""
  if len(value.strip()) < minLength:
    raise ValueError(f"el {fieldName} debe tener al menos {minLength} caracteres.")
  return value.strip()


def parseYesNo(response: str) -> bool:
  """interpreta una respuesta s/n/yes/no como booleano.

  cualquier valor que empiece por 's' o 'y' se considera afirmativo.
  cualquier valor que empiece por 'n' se considera negativo.
  en caso de respuesta vacia o ambigua, se devuelve false.
  """
  clean = response.strip().lower()
  if not clean:
    return False
  if clean.startswith(("s", "y")):
    return True
  if clean.startswith("n"):
    return False
  raise ValueError("respuesta no valida. introduce 's' para si o 'n' para no.")
