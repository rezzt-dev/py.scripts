 # tests for credential vault ->

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from only_one_key.config.crypto import deriveFernetKey, loadOrCreateSalt
from only_one_key.core import vault
from only_one_key.models.credential import Credential


@pytest.fixture
def crypter(tempDataDir) -> Fernet:
  """crea un cifrador fernet con una clave derivada de una contrasena de prueba."""
  salt = loadOrCreateSalt()
  key = deriveFernetKey("test-master-password", salt)
  return Fernet(key)


@pytest.fixture
def otherCrypter(tempDataDir) -> Fernet:
  """crea un segundo cifrador con otra contrasena de prueba."""
  salt = loadOrCreateSalt()
  key = deriveFernetKey("other-test-password", salt)
  return Fernet(key)


class TestVault:
  def test_saveAndListCredential(self, crypter: Fernet):
    credential = Credential(page="example.com", username="user", password="pass")
    vault.saveCredential(crypter, credential)

    credentials = vault.listCredentials(crypter)
    assert len(credentials) == 1
    assert credentials[0] == credential

  def test_duplicateCredentialRaises(self, crypter: Fernet):
    credential = Credential(page="example.com", username="user", password="pass")
    vault.saveCredential(crypter, credential)

    with pytest.raises(vault.DuplicateCredentialError):
      vault.saveCredential(crypter, credential)

  def test_modifyCredential(self, crypter: Fernet):
    credential = Credential(page="example.com", username="user", password="old")
    vault.saveCredential(crypter, credential)

    vault.modifyCredential(crypter, "example.com", "user", "new")
    credentials = vault.listCredentials(crypter)
    assert credentials[0].password == "new"

  def test_modifyMissingCredentialRaises(self, crypter: Fernet):
    with pytest.raises(vault.VaultError, match="no se encontro"):
      vault.modifyCredential(crypter, "missing.com", "user", "new")

  def test_deleteCredential(self, crypter: Fernet):
    credential = Credential(page="example.com", username="user", password="pass")
    vault.saveCredential(crypter, credential)

    vault.deleteCredential(crypter, "example.com", "user")
    credentials = vault.listCredentials(crypter)
    assert credentials == []

  def test_deleteMissingCredentialRaises(self, crypter: Fernet):
    with pytest.raises(vault.VaultError, match="no se encontro"):
      vault.deleteCredential(crypter, "missing.com", "user")

  def test_findCredentials(self, crypter: Fernet):
    vault.saveCredential(crypter, Credential(page="example.com", username="user", password="p1"))
    vault.saveCredential(crypter, Credential(page="test.org", username="admin", password="p2"))
    vault.saveCredential(crypter, Credential(page="example.io", username="other", password="p3"))

    results = vault.findCredentials(crypter, "example")
    assert len(results) == 2

    results = vault.findCredentials(crypter, "admin")
    assert len(results) == 1
    assert results[0].page == "test.org"

  def test_specialCharactersInFieldsPreserved(self, crypter: Fernet):
    credential = Credential(page="page:with:colons", username="user::name", password="p:a:s:s")
    vault.saveCredential(crypter, credential)

    credentials = vault.listCredentials(crypter)
    assert credentials[0] == credential

  def test_wrongKeyFailsToDecrypt(self, crypter: Fernet, tempDataDir):
    credential = Credential(page="example.com", username="user", password="pass")
    vault.saveCredential(crypter, credential)

    salt = loadOrCreateSalt()
    wrongKey = deriveFernetKey("different-password", salt)
    wrongCrypter = Fernet(wrongKey)

    with pytest.raises(vault.CorruptVaultError, match="clave maestra es incorrecta"):
      vault.listCredentials(wrongCrypter)

  def test_corruptVaultLineRaises(self, crypter: Fernet, tempDataDir):
    vault.saveCredential(crypter, Credential(page="example.com", username="user", password="pass"))
     # anadir una linea invalida al vault ->
    with open(vault.VAULT_FILE, "a", encoding="utf-8") as file:
      file.write("this-is-not-a-token\n")

    with pytest.raises(vault.CorruptVaultError, match="lineas afectadas"):
      vault.listCredentials(crypter)

  def test_backupCreatedOnModify(self, crypter: Fernet, tempDataDir):
    credential = Credential(page="example.com", username="user", password="old")
    vault.saveCredential(crypter, credential)

    vault.modifyCredential(crypter, "example.com", "user", "new")
    backup = vault.VAULT_FILE.with_suffix(".rzt.bak")
    assert backup.exists()

  def test_changeVaultKey(self, crypter: Fernet, otherCrypter: Fernet):
    credential = Credential(page="example.com", username="user", password="pass")
    vault.saveCredential(crypter, credential)

    vault.changeVaultKey(crypter, otherCrypter)

    credentials = vault.listCredentials(otherCrypter)
    assert len(credentials) == 1
    assert credentials[0] == credential

    with pytest.raises(vault.CorruptVaultError):
      vault.listCredentials(crypter)

  def test_restoreBackup(self, crypter: Fernet, tempDataDir):
    credential = Credential(page="example.com", username="user", password="pass")
    vault.saveCredential(crypter, credential)
    vault._createBackup()

     # simular corrupcion ->
    vault.VAULT_FILE.write_text("corrupt-data", encoding="utf-8")

    vault._restoreBackup()
    credentials = vault.listCredentials(crypter)
    assert len(credentials) == 1

  def test_hasCredentialsIsFalseWhenVaultIsEmpty(self, tempDataDir):
    assert vault.hasCredentials() is False

  def test_hasCredentialsIsTrueAfterSaveAndFalseAfterDelete(self, crypter: Fernet, tempDataDir):
    credential = Credential(page="example.com", username="user", password="pass")
    assert vault.hasCredentials() is False

    vault.saveCredential(crypter, credential)
    assert vault.hasCredentials() is True

    vault.deleteCredential(crypter, credential.page, credential.username)
    assert vault.hasCredentials() is False
