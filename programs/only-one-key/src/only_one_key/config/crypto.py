 # crypto config ->
 # la clave fernet nunca se guarda en disco. se genera en memoria a partir de la
 # contrasena maestra usando pbkdf2-hmac-sha256 y una sal almacenada.

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from only_one_key.config.settings import DATA_DIR, SALT_FILE, SALT_LENGTH, PBKDF2_ITERATIONS

__all__ = ["ensureDataDir", "loadOrCreateSalt", "deriveFernetKey"]


def ensureDataDir() -> None:
  """crea el directorio de datos con permisos restrictivos si no existe."""
  DATA_DIR.mkdir(parents=True, exist_ok=True)
   # restringir acceso en sistemas unix ->
  try:
    DATA_DIR.chmod(0o700)
  except (OSError, NotImplementedError):
    pass


def loadOrCreateSalt() -> bytes:
  """carga la sal para pbkdf2 o genera una nueva si no existe.

  la sal no necesita ser secreta, pero debe ser unica y estable para que la misma
  contrasena maestra genere siempre la misma clave fernet.
  """
  ensureDataDir()

  if SALT_FILE.exists():
    return SALT_FILE.read_bytes()

  salt = os.urandom(SALT_LENGTH)
  SALT_FILE.write_bytes(salt)
   # restringir lectura al propietario ->
  try:
    SALT_FILE.chmod(0o600)
  except (OSError, NotImplementedError):
    pass
  return salt


def deriveFernetKey(masterPassword: str, salt: bytes) -> bytes:
  """genera una clave url-safe base64 valida para fernet a partir de la maestra."""
  kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=PBKDF2_ITERATIONS,
  )
  rawKey = kdf.derive(masterPassword.encode("utf-8"))
   # fernet espera 32 bytes codificados en base64 url-safe ->
  return base64.urlsafe_b64encode(rawKey)
