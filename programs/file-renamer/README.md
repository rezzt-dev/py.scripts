# SimpleFileRenamer

Herramienta de línea de comandos (CLI) escrita en Python para renombrar masivamente todos los archivos de una carpeta, asignándoles un nombre base común y un número secuencial de tres dígitos.

## Ejemplo

```text
antes/                 después/
├── foto1.jpg          ├── viaje-001.jpg
├── foto2.jpg    →     ├── viaje-002.jpg
└── doc.docx             └── viaje-003.docx
```

## Características

- **Modo interactivo**: selección de carpeta con diálogo nativo del sistema (zenity/kdialog en Linux, osascript en macOS, PowerShell en Windows). Si no hay nativo disponible, hace fallback a Tkinter.
- **Modo batch**: ejecución no interactiva vía argumentos `--folder` y `--base`.
- **Seguro**: no sobrescribe archivos existentes; informa de colisiones y errores por archivo.
- **Multiplataforma**: Windows, Linux y macOS.
- **Testeable**: suite de tests con `pytest`.

## Instalación

Clona el repositorio y navega a la raíz del proyecto:

```bash
cd SimpleFileRenamer
pip install -e .
```

Para desarrollo incluyendo las dependencias de test:

```bash
pip install -e ".[test]"
```

> `tkinter` viene incluido en la mayoría de instalaciones de Python. Si no es así, instálalo desde el gestor de paquetes de tu sistema operativo.

## Uso

### Modo interactivo (por defecto)

```bash
# Linux / macOS
./run.sh

:: Windows
run.bat
```

O, si prefieres usar el comando instalado en el entorno virtual:

```bash
simple-file-renamer
```

Se abrirá un diálogo para elegir la carpeta y luego se pedirá el nombre base.

### Modo batch (no interactivo)

```bash
# Linux / macOS
./run.sh --folder /ruta/a/la/carpeta --base viaje

:: Windows
run.bat --folder C:\Users\Tú\Carpeta --base viaje
```

### Mostrar ayuda

```bash
simple-file-renamer --help
```

### Mostrar versión

```bash
simple-file-renamer --version
```

## Desarrollo

Ejecutar todos los tests:

```bash
pytest
```

Ejecutar el paquete sin instalarlo:

```bash
python -m simple_file_renamer
```

## Estructura del proyecto

```
SimpleFileRenamer/
├── pyproject.toml
├── README.md
├── run.sh
├── run.bat
├── src/simple_file_renamer/
│   ├── cli.py
│   ├── core/
│   │   └── renamer.py
│   ├── ui/
│   │   ├── console.py
│   │   ├── dialogs.py
│   │   └── prompts.py
│   └── utils/
│       ├── keyboard.py
│       └── spinner.py
└── tests/
```

## Licencia

MIT
