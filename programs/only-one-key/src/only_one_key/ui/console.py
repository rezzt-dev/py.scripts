 # console presentation helpers ->

from __future__ import annotations

import os
import subprocess

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn

from only_one_key.config.settings import APP_NAME
from only_one_key.models.credential import Credential

__all__ = [
  "console",
  "clearScreen",
  "printHeader",
  "printError",
  "printSuccess",
  "printInfo",
  "printWarning",
  "printMenu",
  "printCredentialsTable",
  "printStrengthBar",
  "ask",
  "askSecret",
  "askInt",
  "promptQuit",
  "copyToClipboard",
]

console = Console()

 # paleta minimalista inspirada en rezzt.dev ->
 # fondo oscuro del terminal, texto blanco/gris, acento coral solo para acciones destructivas ->
STYLE_TITLE = "bold white"
STYLE_SUBTITLE = "dim white"
STYLE_HEADER = "bold white on #1a1a1a"
STYLE_ROW = "white"
STYLE_ROW_DIM = "bright_black"
STYLE_BORDER = "gray27"
STYLE_ACCENT = "white"
STYLE_SUCCESS = "white"
STYLE_ERROR = "bold light_coral"
STYLE_WARNING = "bright_black"
STYLE_INFO = "dim white"
STYLE_PASSWORD_HIDDEN = "gray27"
STYLE_DELETE = "light_coral"


def clearScreen() -> None:
  """limpia la pantalla de forma multiplataforma sin invocar un shell."""
  command = ["cls"] if os.name == "nt" else ["clear"]
  subprocess.run(command, capture_output=True, check=False)


def printHeader() -> None:
  """muestra el titulo de la aplicacion."""
  title = Text(APP_NAME.upper(), style=STYLE_TITLE, justify="left")
  subtitle = Text("gestor de contrasenas personal", style=STYLE_SUBTITLE, justify="left")
  console.print(Panel(title, subtitle=subtitle, border_style=STYLE_BORDER, padding=(1, 2)))


def printError(message: str) -> None:
  """muestra un mensaje de error."""
  console.print(f"[{STYLE_ERROR}]  × {message}[/{STYLE_ERROR}]")


def printSuccess(message: str) -> None:
  """muestra un mensaje de exito."""
  console.print(f"[{STYLE_SUCCESS}]  ✓ {message}[/{STYLE_SUCCESS}]")


def printInfo(message: str) -> None:
  """muestra un mensaje informativo."""
  console.print(f"[{STYLE_INFO}]  {message}[/{STYLE_INFO}]")


def printWarning(message: str) -> None:
  """muestra un mensaje de advertencia."""
  console.print(f"[{STYLE_WARNING}]  {message}[/{STYLE_WARNING}]")


def printMenu() -> None:
  """muestra el menu principal con estilo minimalista."""
  console.print("\n[bold white]MENU[/bold white]", style=STYLE_SUBTITLE)
  console.print(Text("─" * 40, style=STYLE_BORDER))

  actions = [
    ("0", "alternar visibilidad de contrasenas"),
    ("1", "generar contrasena"),
    ("2", "analizar contrasena"),
    ("3", "guardar contrasena"),
    ("4", "mostrar credenciales"),
    ("5", "buscar credenciales"),
    ("6", "modificar credencial"),
    ("7", "eliminar credencial", True),
    ("8", "cambiar contrasena maestra"),
    ("9", "salir"),
  ]

  for item in actions:
    key = item[0]
    action = item[1]
    isDelete = len(item) > 2 and item[2]
    keyStyle = STYLE_DELETE if isDelete else STYLE_ACCENT
    console.print(f"  [{keyStyle}]{key}[/{keyStyle}]  {action}")

  console.print(Text("─" * 40, style=STYLE_BORDER))
  console.print(f"[{STYLE_INFO}]  introduce Q para salir del menu[/]")


def printCredentialsTable(
  credentials: list[Credential],
  *,
  showPasswords: bool = False,
  highlightId: int | None = None,
) -> None:
  """muestra las credenciales en una tabla minimalista."""
  if not credentials:
    console.print("[bright_black]  no hay credenciales guardadas.[/bright_black]")
    return

  table = Table(
    title="CREDENCIALES GUARDADAS",
    title_style=STYLE_SUBTITLE,
    show_header=True,
    header_style=STYLE_HEADER,
    row_styles=[STYLE_ROW, STYLE_ROW_DIM],
    box=box.HEAVY_HEAD,
    border_style=STYLE_BORDER,
  )
  table.add_column("#", justify="right", style="bold white", width=4)
  table.add_column("PAGINA / PROGRAMA", style="white", min_width=20)
  table.add_column("USUARIO", style="bright_white", min_width=15)
  table.add_column("CONTRASENA", style=STYLE_PASSWORD_HIDDEN, min_width=20)

  for idx, credential in enumerate(credentials, start=1):
    passwordText = credential.password if showPasswords else "•" * min(len(credential.password), 18)
    if highlightId is not None and idx == highlightId:
      table.add_row(
        f"[bold]{idx}[/bold]",
        f"[bold]{credential.page.upper()}[/bold]",
        f"[bold]{credential.username}[/bold]",
        f"[bold {STYLE_PASSWORD_HIDDEN}]{passwordText}[/bold {STYLE_PASSWORD_HIDDEN}]",
      )
    else:
      table.add_row(
        str(idx),
        credential.page.upper(),
        credential.username,
        passwordText,
      )

  console.print(table)


def printStrengthBar(level: str, score: int) -> None:
  """muestra una barra de fortaleza visual."""
  color = {
    "very safe": "white",
    "safe": "bright_black",
    "weak": "bright_black",
    "very weak": "light_coral",
  }.get(level, "white")

  with Progress(
    TextColumn("[bold white]fortaleza:[/bold white] {task.description}"),
    BarColumn(bar_width=40, complete_style="white", finished_style="white"),
    TextColumn("[bold white]{task.percentage:>3.0f}%[/bold white]"),
    console=console,
    transient=True,
  ) as progress:
    task = progress.add_task(f"[{color}]{level}[/{color}]", total=100, completed=score)
    progress.update(task, completed=score)

  console.print(f"nivel: [bold {color}]{level}[/bold {color}] — puntuacion: [bold white]{score}/100[/bold white]")


def ask(prompt: str, *, default: str = "", password: bool = False) -> str:
  """pide una cadena al usuario con estilo minimalista."""
  if password:
    return Prompt.ask(f"[bold white]{prompt}[/bold white]", password=True, default=default)
  return Prompt.ask(f"[bold white]{prompt}[/bold white]", default=default)


def askInt(prompt: str, *, default: int | None = None, minimum: int | None = None) -> int:
  """pide un numero entero al usuario con estilo."""
  value = IntPrompt.ask(f"[bold white]{prompt}[/bold white]", default=default)
  if minimum is not None and value < minimum:
    raise ValueError(f"debe ser mayor o igual a {minimum}.")
  return value


def askSecret(prompt: str) -> str:
  """pide un secreto sin mostrarlo en pantalla."""
  return Prompt.ask(f"[bold white]{prompt}[/bold white]", password=True)


def promptQuit() -> bool:
  """pregunta si el usuario quiere volver atras introduciendo Q.

  returns:
    true si la respuesta empieza por Q, false para cualquier otra cosa.
  """
  console.print(f"[{STYLE_INFO}]  [introduce Q para volver, otra tecla para continuar][/{STYLE_INFO}]")
  value = ask("tu opcion").strip().lower()
  return value.startswith("q")


def copyToClipboard(text: str) -> bool:
  """copia el texto al portapapeles usando herramientas nativas sin exponerlo en argumentos."""
  try:
    if os.name == "nt":
      subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", "$OutputEncoding = New-Object System.Text.UTF8Encoding; $input | Set-Clipboard"],
        input=text,
        text=True,
        check=True,
        capture_output=True,
      )
      return True
    if os.name == "posix":
      for command in [
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
        ["pbcopy"],
      ]:
        try:
          subprocess.run(command, input=text, text=True, check=True, capture_output=True)
          return True
        except (FileNotFoundError, subprocess.CalledProcessError):
          continue
    return False
  except Exception:
    return False
