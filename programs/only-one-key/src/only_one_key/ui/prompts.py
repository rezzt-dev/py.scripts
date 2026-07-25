 # reusable user prompts ->

from __future__ import annotations

from only_one_key.ui import console
from only_one_key.utils.validators import parseYesNo, validateMinLength

__all__ = [
  "askInput",
  "askSecret",
  "askYesNo",
  "askPasswordWithConfirmation",
  "askMasterPassword",
  "askPositiveNumber",
  "askCredentialId",
]


def askInput(prompt: str, *, required: bool = True, minLength: int = 1) -> str:
  """pide una cadena de texto al usuario."""
  while True:
    value = console.ask(prompt).strip()
    if not required:
      return value
    try:
      return validateMinLength(value, minLength, fieldName=prompt.lower())
    except ValueError as exc:
      console.printError(str(exc))


def askSecret(prompt: str) -> str:
  """pide un valor secreto sin eco."""
  return console.askSecret(prompt)


def askYesNo(prompt: str, default: bool = False) -> bool:
  """pide una respuesta s/n."""
  while True:
    value = console.ask(f"{prompt} [{'S/n' if default else 's/N'}]").strip()
    if not value:
      return default
    try:
      return parseYesNo(value)
    except ValueError as exc:
      console.printError(str(exc))


def askPasswordWithConfirmation(prompt: str = "contrasena maestra") -> str:
  """pide una contrasena y su confirmacion hasta que coincidan."""
  while True:
    password = askSecret(f"introduce {prompt.lower()}")
    try:
      validateMinLength(password, 8, fieldName=prompt.lower())
    except ValueError as exc:
      console.printError(str(exc))
      continue

    confirmation = askSecret(f"repite {prompt.lower()}")
    if password == confirmation:
      return password
    console.printError("las contrasenas no coinciden.")


def askMasterPassword() -> str:
  """pide la contrasena maestra."""
  return askSecret("contrasena maestra")


def askPositiveNumber(prompt: str, minimum: int = 1) -> int:
  """pide un numero entero positivo al usuario."""
  while True:
    try:
      return console.askInt(prompt, minimum=minimum)
    except ValueError as exc:
      console.printError(str(exc))


def askCredentialId(credentials: list, prompt: str = "id de la credencial") -> int:
  """pide un id valido de la lista de credenciales."""
  if not credentials:
    raise ValueError("no hay credenciales disponibles.")

  while True:
    try:
      value = console.askInt(prompt, minimum=1)
      if value > len(credentials):
        raise ValueError(f"el id debe estar entre 1 y {len(credentials)}.")
      return value
    except ValueError as exc:
      console.printError(str(exc))


