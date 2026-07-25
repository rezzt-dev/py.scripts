 # vault manager for encrypted credentials ->

from __future__ import annotations

import os
import shutil
from typing import Iterable

from cryptography.fernet import Fernet, InvalidToken

from only_one_key.config.crypto import ensureDataDir
from only_one_key.config.settings import VAULT_FILE
from only_one_key.models.credential import Credential

__all__ = [
  "VaultError",
  "DuplicateCredentialError",
  "CorruptVaultError",
  "hasCredentials",
  "saveCredential",
  "listCredentials",
  "findCredentials",
  "modifyCredential",
  "deleteCredential",
  "changeVaultKey",
]


class VaultError(Exception):
  """error generico del vault."""


class DuplicateCredentialError(VaultError):
  """se intento guardar una credencial duplicada."""


class CorruptVaultError(VaultError):
  """el vault contiene entradas corruptas o la clave es incorrecta."""


def _readTokens() -> list[str]:
  """lee todos los tokens del vault, descartando lineas vacias."""
  ensureDataDir()
  if not VAULT_FILE.exists():
    return []
  return [line.strip() for line in VAULT_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]


def _writeTokens(tokens: list[str]) -> None:
  """escribe la lista de tokens en el vault de forma atomica y sincronizada."""
  ensureDataDir()
  content = "\n".join(tokens) + "\n" if tokens else ""
  tempFile = VAULT_FILE.with_suffix(".rzt.tmp")
  try:
    with open(tempFile, "w", encoding="utf-8") as file:
      file.write(content)
      file.flush()
      os.fsync(file.fileno())
    tempFile.replace(VAULT_FILE)
  except Exception:
    if tempFile.exists():
      tempFile.unlink()
    raise
   # restringir lectura al propietario ->
  try:
    VAULT_FILE.chmod(0o600)
  except (OSError, NotImplementedError):
    pass


def hasCredentials() -> bool:
  """indica si el vault contiene al menos una credencial sin descifrarla."""
  return len(_readTokens()) > 0


def _createBackup() -> None:
  """crea una copia de seguridad del vault antes de modificarlo."""
  if not VAULT_FILE.exists():
    return
  backupPath = VAULT_FILE.with_suffix(".rzt.bak")
  shutil.copy2(VAULT_FILE, backupPath)
  try:
    backupPath.chmod(0o600)
  except (OSError, NotImplementedError):
    pass


def _restoreBackup() -> None:
  """restaura el vault desde la copia de seguridad."""
  backupPath = VAULT_FILE.with_suffix(".rzt.bak")
  if not backupPath.exists():
    return
  shutil.copy2(backupPath, VAULT_FILE)
  try:
    VAULT_FILE.chmod(0o600)
  except (OSError, NotImplementedError):
    pass


def _decryptAll(crypter: Fernet) -> list[Credential]:
  """descifra todas las credenciales del vault."""
  credentials: list[Credential] = []
  corruptLines: list[int] = []

  for index, token in enumerate(_readTokens(), start=1):
    try:
      payload = crypter.decrypt(token.encode("utf-8")).decode("utf-8")
      credentials.append(Credential.fromJson(payload))
    except (InvalidToken, UnicodeDecodeError, KeyError, ValueError):
      corruptLines.append(index)

  if corruptLines:
    raise CorruptVaultError(
      "el vault contiene datos corruptos o la clave maestra es incorrecta. "
      f"lineas afectadas: {corruptLines}."
    )

  return credentials


def saveCredential(crypter: Fernet, credential: Credential) -> None:
  """anade una credencial al vault."""
  credentials = _decryptAll(crypter)
  if any(c.page == credential.page and c.username == credential.username for c in credentials):
    raise DuplicateCredentialError("ya existe una credencial para esa pagina y usuario.")

  _createBackup()
  token = crypter.encrypt(credential.toJson().encode("utf-8")).decode("utf-8")
  tokens = _readTokens()
  tokens.append(token)
  _writeTokens(tokens)


def listCredentials(crypter: Fernet) -> list[Credential]:
  """devuelve todas las credenciales descifradas."""
  return _decryptAll(crypter)


def findCredentials(crypter: Fernet, query: str) -> list[Credential]:
  """busca credenciales cuya pagina o usuario contengan la consulta."""
  queryLower = query.lower()
  return [
    c for c in _decryptAll(crypter)
    if queryLower in c.page.lower() or queryLower in c.username.lower()
  ]


def modifyCredential(crypter: Fernet, page: str, username: str, newPassword: str) -> None:
  """modifica la contrasena de una credencial existente."""
  credentials = _decryptAll(crypter)
  found = False
  newCredentials: list[Credential] = []
  for credential in credentials:
    if credential.page == page and credential.username == username:
      found = True
      newCredentials.append(Credential(page=page, username=username, password=newPassword))
    else:
      newCredentials.append(credential)

  if not found:
    raise VaultError("no se encontro ninguna credencial con esa pagina y usuario.")

  _persistAll(crypter, newCredentials)


def deleteCredential(crypter: Fernet, page: str, username: str) -> None:
  """elimina una credencial del vault."""
  credentials = _decryptAll(crypter)
  newCredentials = [c for c in credentials if not (c.page == page and c.username == username)]

  if len(newCredentials) == len(credentials):
    raise VaultError("no se encontro ninguna credencial con esa pagina y usuario.")

  _persistAll(crypter, newCredentials)


def changeVaultKey(oldCrypter: Fernet, newCrypter: Fernet) -> None:
  """recifra todo el vault con una nueva clave fernet.

  se usa cuando el usuario cambia la contrasena maestra.
  """
  credentials = _decryptAll(oldCrypter)
  _createBackup()
  tokens = [
    newCrypter.encrypt(credential.toJson().encode("utf-8")).decode("utf-8")
    for credential in credentials
  ]
  _writeTokens(tokens)


def _persistAll(crypter: Fernet, credentials: Iterable[Credential]) -> None:
  """reescribe el vault completo a partir de una lista de credenciales."""
  _createBackup()
  tokens = [
    crypter.encrypt(credential.toJson().encode("utf-8")).decode("utf-8")
    for credential in credentials
  ]
  _writeTokens(tokens)
