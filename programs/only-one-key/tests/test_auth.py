 # tests for master password authentication ->

from __future__ import annotations

from only_one_key.core import auth


class TestAuth:
  def test_createAndVerifyLock(self, tempDataDir):
    assert auth.hasLock() is False
    auth.createLock("my-master-password")
    assert auth.hasLock() is True

    assert auth.verifyLock("my-master-password") is True
    assert auth.verifyLock("wrong-password") is False

  def test_verifyWithoutLockReturnsFalse(self, tempDataDir):
    assert auth.verifyLock("any-password") is False

  def test_rehashOnParametersChange(self, tempDataDir, monkeypatch):
    auth.createLock("my-master-password")
    originalHash = auth.LOCK_FILE.read_text()

     # simular un cambio de parametros forzando rehash ->
    monkeypatch.setattr(auth, "_HASHER", auth.PasswordHasher(time_cost=4, memory_cost=64_000))
    assert auth.verifyLock("my-master-password") is True
    newHash = auth.LOCK_FILE.read_text()
    assert newHash != originalHash

  def test_changeMasterPassword(self, tempDataDir):
    auth.createLock("old-password")
    assert auth.changeMasterPassword("old-password", "new-password") is True
    assert auth.verifyLock("new-password") is True
    assert auth.verifyLock("old-password") is False

  def test_changeMasterPasswordWithWrongCurrentFails(self, tempDataDir):
    auth.createLock("old-password")
    assert auth.changeMasterPassword("wrong-password", "new-password") is False
    assert auth.verifyLock("old-password") is True

  def test_createLockOverwritesExisting(self, tempDataDir):
    auth.createLock("first-password")
    auth.createLock("second-password")
    assert auth.verifyLock("second-password") is True
    assert auth.verifyLock("first-password") is False
