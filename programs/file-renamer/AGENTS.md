# AGENTS.md — SimpleFileRenamer

> Este archivo está dirigido a agentes de código de IA. Describe la arquitectura, convenciones y detalles prácticos del proyecto para que cualquier agente pueda trabajar sobre el código sin suposiciones.

---

## 1. Visión general del proyecto

**SimpleFileRenamer** es una herramienta de línea de comandos (CLI) escrita en Python que permite renombrar de forma masiva todos los archivos de una carpeta seleccionada, asignándoles un nombre base común y un número secuencial con tres dígitos (por ejemplo: `fichero-001.docx`, `fichero-002.docx`, …).

La interfaz es una aplicación de terminal interactiva que utiliza:
- **Tkinter** (`filedialog`) para que el usuario elija la carpeta objetivo mediante un explorador gráfico.
- **Rich** para mostrar textos coloreados y con estilos en la consola.
- **Typer** como lanzador del punto de entrada principal.

El proyecto sigue una estructura de paquete Python estándar con `pyproject.toml`, código bajo `src/simple_file_renamer/` y tests bajo `tests/`.

---

## 2. Tecnologías y dependencias

| Dependencia | Uso |
|-------------|-----|
| `typer`     | Punto de entrada CLI y argumentos (`--folder`, `--base`, `--interactive`) |
| `rich`      | Salida formateada y coloreada en terminal |
| `tkinter`   | Diálogo gráfico de selección de carpeta |
| `msvcrt`    | Lectura de tecla en Windows (`wait_key`) |
| `termios`, `tty` | Lectura de tecla en Linux/macOS (`wait_key`) |
| `platform`  | Detección del sistema operativo para importaciones condicionales |
| `threading`, `time`, `os`, `pathlib` | Lógica del programa (animación de carga, renombrado, utilidades) |
| `pytest`    | Framework de tests (dependencia opcional `test`) |

**Compatibilidad:** El código detecta el SO en tiempo de ejecución mediante `platform.system()`. En Windows se importa `msvcrt`; en Linux/macOS se importan `termios` y `tty`. Si alguna librería no está disponible, `wait_key()` hace fallback a `input()`.

Las dependencias están declaradas en `pyproject.toml` (fuente canónica). `requirements.txt` se mantiene como referencia rápida.

```bash
pip install -e .
pip install -e ".[test]"  # incluye pytest
```

(`tkinter` suele venir incluido con la instalación estándar de Python.)

---

## 3. Estructura del código

```
SimpleFileRenamer/
├── pyproject.toml                # Empaquetado, metadatos, entry point y dependencias
├── README.md                     # Documentación de uso/instalación/desarrollo
├── requirements.txt              # Referencia rápida de dependencias
├── run.sh                        # Lanzador para Linux/macOS: ejecuta el comando usando venv/ sin activarlo
├── run.bat                       # Lanzador para Windows: ejecuta el comando usando venv\ sin activarlo
├── .gitignore                    # Ignora venv, __pycache__, dist, etc.
├── src/simple_file_renamer/      # Paquete principal
│   ├── __init__.py               # Versión y exports públicos
│   ├── __main__.py               # Punto de entrada `python -m simple_file_renamer`
│   ├── cli.py                    # Comandos Typer, opciones CLI
│   ├── config.py                 # Constantes globales
│   ├── exceptions.py               # Excepciones de dominio
│   ├── core/
│   │   ├── __init__.py
│   │   └── renamer.py            # Lógica pura de renombrado masivo
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── console.py            # Presentación con Rich
│   │   ├── dialogs.py            # Diálogos nativos de selección de carpeta (zenity, kdialog, osascript, PowerShell)
│   │   └── prompts.py            # Diálogo de carpeta (nativo + fallback Tkinter), preguntas, espera de tecla
│   └── utils/
│       ├── __init__.py
│       ├── keyboard.py           # Lectura de tecla multiplataforma
│       └── spinner.py            # Animación de carga en hilo
└── tests/                        # Suite de tests con pytest
    ├── __init__.py
    ├── conftest.py
    ├── test_renamer.py
    ├── test_keyboard.py
    └── test_cli.py
```

### Descripción de módulos

- **`src/simple_file_renamer/cli.py`**
  - Define la aplicación Typer y el comando principal.
  - Soporta modo interactivo (por defecto cuando faltan argumentos) y modo batch (`--folder` + `--base` + `--no-interactive`).
  - Muestra resultados y errores mediante `ui/console.py`.
  - Gestiona el spinner durante la operación.

- **`src/simple_file_renamer/core/renamer.py`**
  - Contiene `rename_files(folder, base_name, ...)`.
  - Filtra únicamente archivos (`pathlib.Path.is_file()`), ignorando subcarpetas.
  - Preserva la extensión de cada archivo y genera un nombre nuevo con formato `{base}-{n:03d}{ext}`.
  - Valida colisiones de nombres antes de renombrar; si el destino ya existe, registra el error y continúa.
  - Maneja errores por archivo individual (`try/except` interno); un archivo fallido no detiene el resto.
  - Devuelve un `RenameResult` con `count`, `renamed` y `errors`.

- **`src/simple_file_renamer/ui/console.py`**
  - Helpers de impresión con Rich: título, limpieza de pantalla, resumen y errores.

- **`src/simple_file_renamer/ui/dialogs.py`**
  - `select_folder_native()`: abre el diálogo nativo del sistema operativo para seleccionar una carpeta.
  - En Linux usa `zenity` o `kdialog`; en macOS `osascript`; en Windows `powershell` con `FolderBrowserDialog`.
  - Si no hay herramienta nativa disponible o el usuario cancela, devuelve `None`.

- **`src/simple_file_renamer/ui/prompts.py`**
  - `select_folder()`: intenta usar `select_folder_native()`; si falla, hace fallback al diálogo de Tkinter.
  - `ask_base_name()`: solicita el nombre base por consola.
  - `ask_continue()`: pregunta si se desea repetir el proceso.
  - `wait_for_key()`: espera una pulsación de tecla.

- **`src/simple_file_renamer/utils/keyboard.py`**
  - `wait_key()`: lectura de tecla sin Enter, cross-platform.
  - `parse_yes_no()`: normaliza respuestas de sí/no.

- **`src/simple_file_renamer/utils/spinner.py`**
  - `loading_animation()`: spinner en hilo secundario.

- **`src/simple_file_renamer/exceptions.py`**
  - Excepciones de dominio: `SimpleFileRenamerError`, `FolderNotFoundError`, `RenameError`.

---

## 4. Convenciones de código

- **Idioma:** Los textos de la interfaz y los comentarios docstring están en español; los nombres de módulos, clases y funciones principales siguen la convención Python estándar.
- **Estilo de nombres:**
  - Funciones y variables: `snake_case`.
  - Clases: `PascalCase`.
  - Constantes: `UPPER_CASE`.
  - Módulos: `snake_case`.
- **Imports:** Usar imports absolutos y evitar `from module import *`. No se usa `sys.path.append`.
- **Type hints:** Se recomienda añadir anotaciones de tipo en funciones públicas.
- **Manejo de errores:** Usar excepciones de dominio definidas en `exceptions.py`. No capturar excepciones genéricas silenciosamente.

---

## 5. Cómo ejecutar el proyecto

Desde la raíz del repositorio, con el entorno activado y el paquete instalado en editable:

```bash
pip install -e .
simple-file-renamer
```

Con el lanzador `run.sh` (Linux/macOS) o `run.bat` (Windows) no es necesario activar el entorno virtual manualmente:

```bash
# Linux / macOS
./run.sh
./run.sh --folder /ruta/a/carpeta --base fichero
```

```batch
:: Windows
run.bat
run.bat --folder C:\Users\Tú\Carpeta --base fichero
```

Modo no interactivo:

```bash
simple-file-renamer --folder /ruta/a/carpeta --base fichero
```

Sin instalar, como módulo:

```bash
python -m simple_file_renamer
```

---

## 6. Pruebas

La suite de tests usa `pytest`:

```bash
pip install -e ".[test]"
pytest
```

Archivos de test:
- `tests/test_renamer.py`: renombrado correcto, carpetas vacías, colisiones, extensiones, secuencias de ancho variable.
- `tests/test_keyboard.py`: normalización de respuestas sí/no.
- `tests/test_cli.py`: argumentos CLI, ayuda, versión, modo batch con `CliRunner`.

---

## 7. Consideraciones de seguridad y portabilidad

- **Renombrado seguro:** Se validan colisiones de nombres antes de cada `rename`. Si el destino ya existe, se registra un error y se continúa con el siguiente archivo. No se sobrescriben archivos.
- **Permisos:** Si algún archivo está abierto por otro proceso o el usuario carece de permisos de escritura, el error se captura a nivel de archivo individual. El resto de archivos siguen procesándose.
- **Portabilidad Windows/Linux/macOS:** `wait_key()` detecta el SO y utiliza `msvcrt.getch()` en Windows o `termios`/`tty` en Unix. Si ninguna está disponible, hace fallback a `input()`.
- **Rutas:** El código usa `pathlib.Path`, compatible con separadores de Windows y Unix.

---

## 8. Notas para el mantenimiento

- Al añadir nuevas dependencias, regístralas en `pyproject.toml` y actualiza `requirements.txt` y este archivo.
- Si se añaden nuevos módulos, mantener la estructura bajo `src/simple_file_renamer/` y exportar símbolos públicos en `__init__.py` cuando sea apropiado.
- Mantener los tests actualizados con cualquier cambio de comportamiento del CLI o del renombrador.
