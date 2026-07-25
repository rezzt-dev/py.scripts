 # master password authentication with argon2id ->
 # el hash argon2id se usa solo para verificar la contrasena maestra.
 # la clave de cifrado de las credenciales se genera por separado con pbkdf2.

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from only_one_key.config.crypto import ensureDataDir
from only_one_key.config.settings import LOCK_FILE

__all__ = ["hasLock", "createLock", "verifyLock", "changeMasterPassword"]

 # hasher con parametros equilibrados (~0.5s en hardware moderno) ->
_HASHER = PasswordHasher(
  time_cost=3,
  memory_cost=64_000,
  parallelism=1,
  hash_len=32,
  salt_len=16,
)


def hasLock() -> bool:
  """indica si ya existe un lock maestro creado."""
  return LOCK_FILE.exists()


def createLock(masterPassword: str) -> None:
  """crea el fichero de lock con el hash argon2id de la contrasena maestra."""
  ensureDataDir()
  hashed = _HASHER.hash(masterPassword)
  LOCK_FILE.write_text(hashed, encoding="utf-8")
  try:
    LOCK_FILE.chmod(0o600)
  except (OSError, NotImplementedError):
    pass


def verifyLock(masterPassword: str) -> bool:
  """verifica la contrasena maestra contra el hash almacenado."""
  if not LOCK_FILE.exists():
    return False

  storedHash = LOCK_FILE.read_text(encoding="utf-8").strip()
  try:
    _HASHER.verify(storedHash, masterPassword)
     # re-hash si los parametros de argon2 han cambiado ->
    if _HASHER.check_needs_rehash(storedHash):
      createLock(masterPassword)
    return True
  except VerifyMismatchError:
    return False
  except Exception:
    return False


def changeMasterPassword(oldPassword: str, newPassword: str) -> bool:
  """cambia el lock maestro si la contrasena actual es correcta.

  returns:
    true si el cambio se realizo correctamente, false si la actual es incorrecta.
  """
  if not verifyLock(oldPassword):
    return False

  createLock(newPassword)
  return True
