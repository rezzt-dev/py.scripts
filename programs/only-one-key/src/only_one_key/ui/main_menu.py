 # main menu loop ->

from __future__ import annotations

from cryptography.fernet import Fernet

from only_one_key.config.crypto import deriveFernetKey, loadOrCreateSalt
from only_one_key.core import auth, password, vault
from only_one_key.models.credential import Credential
from only_one_key.ui import console, prompts
from only_one_key.utils.validators import validateMenuOption

__all__ = ["run"]

_MAX_ATTEMPTS = 3
_SHOW_PASSWORDS = False


def run() -> None:
  """arranca la aplicacion: autenticacion + menu principal."""
  console.clearScreen()
  console.printHeader()

  masterPassword = __authenticate()
  if masterPassword is None:
    console.printError("autenticacion fallida. cerrando aplicacion.")
    return

  salt = loadOrCreateSalt()
  key = deriveFernetKey(masterPassword, salt)
  crypter = Fernet(key)

  console.clearScreen()
  __mainMenu(crypter)


def __authenticate() -> str | None:
  """gestiona el lock maestro: creacion o verificacion."""
  if not auth.hasLock():
    console.printWarning("primera ejecucion detectada. crea una contrasena maestra.")
    masterPassword = prompts.askPasswordWithConfirmation("contrasena maestra")
    auth.createLock(masterPassword)
    console.printSuccess("contrasena maestra creada correctamente.")
    return masterPassword

  attempts = 0
  while attempts < _MAX_ATTEMPTS:
    masterPassword = prompts.askMasterPassword()
    if auth.verifyLock(masterPassword):
      return masterPassword
    attempts += 1
    remaining = _MAX_ATTEMPTS - attempts
    if remaining > 0:
      console.printError(f"contrasena incorrecta. te quedan {remaining} intentos.")
    else:
      console.printError("contrasena incorrecta. no quedan intentos.")

  return None


def __mainMenu(crypter: Fernet) -> None:
  """bucle del menu principal."""
  global _SHOW_PASSWORDS

  while True:
    console.printHeader()
    console.printMenu()
    option = console.ask("elige una opcion").strip()

    if option.lower() == "q":
      console.printSuccess("hasta pronto.")
      return

    try:
      choice = validateMenuOption(option, range(0, 10))
    except ValueError as exc:
      console.printError(str(exc))
      __waitForContinue()
      continue

    console.clearScreen()
    console.printHeader()

    try:
      match choice:
        case 0:
          __togglePasswords()
          __showCredentials(crypter)
        case 1:
          __generatePassword(crypter)
        case 2:
          __analyzePassword()
        case 3:
          __savePassword(crypter)
        case 4:
          __showCredentials(crypter)
        case 5:
          __searchPassword(crypter)
        case 6:
          __modifyCredential(crypter)
        case 7:
          __deleteCredential(crypter)
        case 8:
          crypter = __changeMasterPassword(crypter) or crypter
        case 9:
          console.printSuccess("hasta pronto.")
          return
    except Exception as exc:
       # capturar errores inesperados para no mostrar tracebacks al usuario ->
      console.printError(f"error inesperado: {exc}")

    __waitForContinue()


def __waitForContinue() -> None:
  """pausa hasta que el usuario pulse intro."""
  console.console.input("\n[dim]pulsa intro para continuar...[/dim]")
  console.clearScreen()


def __togglePasswords() -> None:
  """alterna la visibilidad de las contrasenas en la tabla."""
  global _SHOW_PASSWORDS
  _SHOW_PASSWORDS = not _SHOW_PASSWORDS
  state = "visibles" if _SHOW_PASSWORDS else "ocultas"
  console.printInfo(f"contrasenas {state}.")


def __generatePassword(crypter: Fernet) -> None:
  """genera una contrasena y opcionalmente la guarda."""
  if console.promptQuit():
    return

  length = prompts.askPositiveNumber("longitud de la contrasena (minimo 8)", minimum=8)

  useUpper = prompts.askYesNo("incluir mayusculas", default=True)
  useLower = prompts.askYesNo("incluir minusculas", default=True)
  useDigits = prompts.askYesNo("incluir digitos", default=True)
  usePunct = prompts.askYesNo("incluir signos de puntuacion", default=True)

  try:
    generated = password.passwordGenerator(
      length,
      useUppercase=useUpper,
      useLowercase=useLower,
      useDigits=useDigits,
      usePunctuation=usePunct,
    )
  except ValueError as exc:
    console.printError(str(exc))
    return

  console.console.print(f"contrasena generada: [bold white]{generated}[/bold white]")

  if console.copyToClipboard(generated):
    console.printSuccess("contrasena copiada al portapapeles.")
  else:
    console.printInfo("no se pudo copiar al portapapeles. copiala manualmente.")

  if prompts.askYesNo("deseas guardarla", default=False):
    page = prompts.askInput("pagina / programa")
    username = prompts.askInput("usuario")
    __saveCredential(crypter, Credential(page=page, username=username, password=generated))


def __analyzePassword() -> None:
  """pide una contrasena y muestra su analisis."""
  if console.promptQuit():
    return

  value = prompts.askSecret("contrasena a analizar")
  if not value:
    console.printError("la contrasena no puede estar vacia.")
    return

  level, score = password.passwordAnalyzer(value)
  console.printStrengthBar(level, score)


def __savePassword(crypter: Fernet) -> None:
  """guarda una credencial introducida manualmente."""
  if console.promptQuit():
    return

  page = prompts.askInput("pagina / programa")
  username = prompts.askInput("usuario")
  passValue = prompts.askSecret("contrasena")
  if not passValue:
    console.printError("la contrasena no puede estar vacia.")
    return

  __saveCredential(crypter, Credential(page=page, username=username, password=passValue))


def __saveCredential(crypter: Fernet, credential: Credential) -> None:
  """guarda una credencial en el vault, manejando duplicados."""
  try:
    vault.saveCredential(crypter, credential)
    console.printSuccess("credencial guardada correctamente.")
  except vault.DuplicateCredentialError as exc:
    console.printError(str(exc))
    if prompts.askYesNo("deseas sobrescribirla", default=False):
      try:
        vault.modifyCredential(crypter, credential.page, credential.username, credential.password)
        console.printSuccess("credencial actualizada correctamente.")
      except vault.VaultError as innerExc:
        console.printError(str(innerExc))


def __showCredentials(crypter: Fernet) -> None:
  """muestra todas las credenciales guardadas."""
  if not vault.hasCredentials():
    console.printWarning("no hay credenciales guardadas.")
    return

  if console.promptQuit():
    return

  masterPassword = __requireMasterPassword()
  if masterPassword is None:
    return

  try:
    credentials = vault.listCredentials(crypter)
    console.printCredentialsTable(credentials, showPasswords=_SHOW_PASSWORDS)
  except vault.VaultError as exc:
    console.printError(str(exc))


def __searchPassword(crypter: Fernet) -> None:
  """busca credenciales por pagina o usuario."""
  if not vault.hasCredentials():
    console.printWarning("no hay credenciales guardadas.")
    return

  if console.promptQuit():
    return

  masterPassword = __requireMasterPassword()
  if masterPassword is None:
    return

  query = prompts.askInput("termino de busqueda", required=False)
  if not query:
    console.printInfo("mostrando todas las credenciales.")

  try:
    credentials = vault.findCredentials(crypter, query)
    if not credentials:
      console.printWarning("no se encontraron credenciales.")
      return
    console.printCredentialsTable(credentials, showPasswords=_SHOW_PASSWORDS)
  except vault.VaultError as exc:
    console.printError(str(exc))


def __modifyCredential(crypter: Fernet) -> None:
  """modifica la contrasena de una credencial seleccionada por id."""
  if not vault.hasCredentials():
    console.printWarning("no hay credenciales para modificar.")
    return

  if console.promptQuit():
    return

  masterPassword = __requireMasterPassword()
  if masterPassword is None:
    return

  try:
    credentials = vault.listCredentials(crypter)
  except vault.VaultError as exc:
    console.printError(str(exc))
    return

  if not credentials:
    console.printWarning("no hay credenciales para modificar.")
    return

  console.printCredentialsTable(credentials, showPasswords=_SHOW_PASSWORDS)
  credentialId = prompts.askCredentialId(credentials, "id de la credencial a modificar")
  selected = credentials[credentialId - 1]

  newPassword = prompts.askSecret("nueva contrasena")
  if not newPassword:
    console.printError("la contrasena no puede estar vacia.")
    return

  if not prompts.askYesNo(f"modificar credencial #{credentialId} ({selected.page}/{selected.username})", default=False):
    console.printInfo("operacion cancelada.")
    return

  try:
    vault.modifyCredential(crypter, selected.page, selected.username, newPassword)
    console.printSuccess("contrasena modificada correctamente.")
  except vault.VaultError as exc:
    console.printError(str(exc))


def __deleteCredential(crypter: Fernet) -> None:
  """elimina una credencial seleccionada por id."""
  if not vault.hasCredentials():
    console.printWarning("no hay credenciales para eliminar.")
    return

  if console.promptQuit():
    return

  masterPassword = __requireMasterPassword()
  if masterPassword is None:
    return

  try:
    credentials = vault.listCredentials(crypter)
  except vault.VaultError as exc:
    console.printError(str(exc))
    return

  if not credentials:
    console.printWarning("no hay credenciales para eliminar.")
    return

  console.printCredentialsTable(credentials, showPasswords=_SHOW_PASSWORDS)
  credentialId = prompts.askCredentialId(credentials, "id de la credencial a eliminar")
  selected = credentials[credentialId - 1]

  if not prompts.askYesNo(f"eliminar credencial #{credentialId} ({selected.page}/{selected.username})", default=False):
    console.printInfo("operacion cancelada.")
    return

  try:
    vault.deleteCredential(crypter, selected.page, selected.username)
    console.printSuccess("credencial eliminada correctamente.")
  except vault.VaultError as exc:
    console.printError(str(exc))


def __changeMasterPassword(crypter: Fernet) -> Fernet | None:
  """cambia la contrasena maestra y recifra el vault.

  returns:
    el nuevo cifrador si el cambio fue correcto, None si fallo.
  """
  if console.promptQuit():
    return None

  oldPassword = __requireMasterPassword()
  if oldPassword is None:
    return None

  newPassword = prompts.askPasswordWithConfirmation("nueva contrasena maestra")
  if newPassword == oldPassword:
    console.printWarning("la nueva contrasena es igual a la actual. no se realiza ningun cambio.")
    return None

  if not prompts.askYesNo("esta accion recifrara todas las credenciales. continuar", default=False):
    console.printInfo("operacion cancelada.")
    return None

  try:
    salt = loadOrCreateSalt()
    newKey = deriveFernetKey(newPassword, salt)
    newCrypter = Fernet(newKey)
    vault.changeVaultKey(crypter, newCrypter)

    if not auth.changeMasterPassword(oldPassword, newPassword):
      console.printError("no se pudo actualizar el lock maestro.")
      vault._restoreBackup()
      return None

    console.printSuccess("contrasena maestra cambiada correctamente.")
    return newCrypter
  except Exception as exc:
    console.printError(f"error al cambiar la contrasena maestra: {exc}")
    vault._restoreBackup()
    return None


def __requireMasterPassword() -> str | None:
  """pide la contrasena maestra para operaciones sensibles.

  returns:
    la contrasena introducida si es correcta, None si falla.
  """
  masterPassword = prompts.askMasterPassword()
  if auth.verifyLock(masterPassword):
    return masterPassword
  console.printError("contrasena maestra incorrecta.")
  return None
