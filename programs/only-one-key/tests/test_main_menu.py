 # integration tests for main menu ->

from __future__ import annotations

import pytest
from unittest.mock import patch

from cryptography.fernet import Fernet

from only_one_key.config.crypto import deriveFernetKey, loadOrCreateSalt
from only_one_key.core import vault
from only_one_key.models.credential import Credential
from only_one_key.ui import console, main_menu


@pytest.fixture
def crypter(tempDataDir) -> Fernet:
  """crea un cifrador fernet con una clave derivada de una contrasena de prueba."""
  salt = loadOrCreateSalt()
  key = deriveFernetKey("test-master-password", salt)
  return Fernet(key)


class TestMainMenu:
  def test_optionZeroTogglesPasswordVisibility(self):
    inputs = ["0\n", "9\n"]
    idx = 0

    def fakeAsk(prompt, **kwargs):
      nonlocal idx
      value = inputs[idx]
      idx += 1
      return value

    with patch.object(console, "ask", fakeAsk):
      with patch.object(main_menu, "__generatePassword") as mockGenerate:
        with patch.object(main_menu, "__togglePasswords") as mockToggle:
          with patch.object(main_menu, "__waitForContinue"):
            getattr(main_menu, "__mainMenu")(Fernet(Fernet.generate_key()))

    mockToggle.assert_called_once()
    mockGenerate.assert_not_called()

  def test_optionOneCallsGeneratePassword(self):
    inputs = ["1\n", "q\n", "9\n"]
    idx = 0

    def fakeAsk(prompt, **kwargs):
      nonlocal idx
      value = inputs[idx]
      idx += 1
      return value

    with patch.object(console, "ask", fakeAsk):
      with patch.object(console, "promptQuit", return_value=True):
        with patch.object(main_menu, "__generatePassword") as mockGenerate:
          with patch.object(main_menu, "__togglePasswords") as mockToggle:
            with patch.object(main_menu, "__waitForContinue"):
              getattr(main_menu, "__mainMenu")(Fernet(Fernet.generate_key()))

    mockGenerate.assert_called_once()
    mockToggle.assert_not_called()

  def test_optionQQuitsApplication(self):
    inputs = ["q\n"]
    idx = 0

    def fakeAsk(prompt, **kwargs):
      nonlocal idx
      value = inputs[idx]
      idx += 1
      return value

    with patch.object(console, "ask", fakeAsk):
      with patch.object(main_menu, "__generatePassword") as mockGenerate:
        with patch.object(main_menu, "__togglePasswords") as mockToggle:
          with patch.object(main_menu, "__waitForContinue"):
            getattr(main_menu, "__mainMenu")(Fernet(Fernet.generate_key()))

    mockGenerate.assert_not_called()
    mockToggle.assert_not_called()

  def test_toggleVisibilityAffectsCredentialsTable(self, crypter, tempDataDir):
    """comprueba que la opcion 0 alterna el flag y muestra las credenciales directamente."""
    vault.saveCredential(crypter, Credential(page="example.com", username="user", password="secret123"))
    originalState = getattr(main_menu, "_SHOW_PASSWORDS")

    inputs = ["0\n", "9\n"]
    idx = 0

    def fakeAsk(prompt, **kwargs):
      nonlocal idx
      value = inputs[idx]
      idx += 1
      return value

    capturedShow = []

    def fakePrintTable(credentials, *, showPasswords=False, highlightId=None):
      capturedShow.append(showPasswords)

    try:
      with patch.object(console, "ask", fakeAsk):
        with patch.object(console, "promptQuit", return_value=False):
          with patch.object(console, "printCredentialsTable", fakePrintTable):
            with patch.object(main_menu, "__requireMasterPassword", return_value=True):
              with patch.object(main_menu, "__waitForContinue"):
                getattr(main_menu, "__mainMenu")(crypter)
    finally:
      setattr(main_menu, "_SHOW_PASSWORDS", originalState)

    assert capturedShow == [True], "tras alternar visibilidad, la opcion 0 debe mostrar las contrasenas directamente"
