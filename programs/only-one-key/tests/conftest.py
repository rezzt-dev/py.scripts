 # shared fixtures for tests ->

from __future__ import annotations

import pytest

from only_one_key import config
from only_one_key.core import auth, vault


@pytest.fixture
def tempDataDir(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
  """redirige todos los ficheros de datos a un directorio temporal."""
  dataDir = tmp_path / "data"
  dataDir.mkdir()

  monkeypatch.setattr(config.settings, "DATA_DIR", dataDir)
  monkeypatch.setattr(config.settings, "LOCK_FILE", dataDir / "lock.argon2")
  monkeypatch.setattr(config.settings, "SALT_FILE", dataDir / "salt.bin")
  monkeypatch.setattr(config.settings, "VAULT_FILE", dataDir / "vault.rzt")

   # los modulos core tienen los paths importados; actualizamos las referencias ->
  monkeypatch.setattr(auth, "LOCK_FILE", dataDir / "lock.argon2")
  monkeypatch.setattr(vault, "VAULT_FILE", dataDir / "vault.rzt")
  monkeypatch.setattr(config.crypto, "DATA_DIR", dataDir)
  monkeypatch.setattr(config.crypto, "SALT_FILE", dataDir / "salt.bin")
