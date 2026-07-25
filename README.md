# PY.SCRIPTS

coleccion personal de scripts, utilidades y pequenos programas en python. el repositorio esta organizado en tres areas principales: programas empaquetados con su propia instalacion, scripts de scripting rapido y documentacion para agentes de ia.

> nota: este repositorio es principalmente un espacio de trabajo personal. algunos scripts son educativos o de prueba de concepto; revisalos antes de ejecutarlos en entornos reales.

---

## ESTRUCTURA DEL REPOSITORIO

```text
py.scripts/
├── agent-docs/          # documentacion y skills para agentes de ia
├── programs/            # programas empaquetados con pyproject.toml
│   ├── file-renamer/    # renombrador masivo de archivos
│   └── only-one-key/    # gestor de contrasenas en consola
├── scripting/           # scripts sueltos para tareas concretas
│   ├── codebars-qrcodes/
│   ├── web-scraping/
│   ├── web-scripts/
│   ├── default-sql-injection.py
│   ├── malware-analysis.py
│   └── secure-qrcode-tester.py
├── .gitignore
└── README.md
```

---

## PROGRAMAS

### `programs/file-renamer` — simplefilerenamer

herramienta cli para renombrar masivamente los archivos de una carpeta, asignandoles un nombre base comun y un numero secuencial de tres digitos.

- modo interactivo (explorador grafico) y modo batch (`--folder`, `--base`).
- no sobrescribe archivos existentes.
- multiplataforma: windows, linux y macos.
- tiene su propia suite de tests con `pytest`.

```bash
cd programs/file-renamer
pip install -e .
simple-file-renamer --help
```

mas detalles en [`programs/file-renamer/README.md`](programs/file-renamer/README.md).

### `programs/only-one-key` — gestor de contrasenas

gestor de contrasenas personal para consola con interfaz interactiva minimalista.

- almacenamiento encriptado de credenciales con fernet.
- autenticacion con contrasena maestra mediante argon2id.
- generacion y analisis de fortaleza de contrasenas.
- copias de seguridad automaticas del vault.

```bash
cd programs/only-one-key
pip install -r requirements.txt
python -m only_one_key
```

mas detalles en [`programs/only-one-key/README.md`](programs/only-one-key/README.md).

---

## SCRIPTS DE `SCRIPTING/`

estos scripts son utilidades sueltas para tareas puntuales. la mayoria usan `typer` para la cli y `rich` para la salida en consola.

### codigos de barras y qr (`codebars-qrcodes/`)

| script | proposito |
|--------|-----------|
| `create-codebar.py` | genera un codigo de barras upc a partir de 12 digitos. |
| `create-qrcode.py` | genera una imagen qr a partir de una url o texto. |
| `extract-codebar.py` | decodifica un codigo de barras desde una imagen. |
| `extract-qrcode.py` | decodifica un codigo qr desde una imagen. |

### web scraping (`web-scraping/`)

| script | proposito |
|--------|-----------|
| `scrap-prices-stock.py` | extrae precios, disponibilidad y sku de una pagina de productos y genera reportes json/csv. |
| `scrap-web-images.py` | descarga las imagenes de una pagina web y las renombra secuencialmente. |
| `seo-tech-audit.py` | rastrea un sitio y genera un informe tecnico de seo (titulos, meta descriptions, encabezados, imagenes sin alt, etc.). |

### web y seguridad (`web-scripts/`)

| script | proposito |
|--------|-----------|
| `search-web-defeats.py` | analiza formularios y enlaces de una url en busca de patrones potencialmente inseguros (xss/sqli basico). **solo para pruebas autorizadas.** |
| `search-words-web.py` | busca urls que contengan una palabra usando la api de google custom search. |
| `secure-web-analyzer.py` | consulta virustotal para determinar si una url es segura. |

### scripts sueltos

| script | proposito |
|--------|-----------|
| `default-sql-injection.py` | demostracion educativa de inyeccion sql vs. consulta segura con prepared statements en mysql. **solo para entornos de prueba locales.** |
| `malware-analysis.py` | sube un archivo a virustotal y obtiene su reporte de analisis. |
| `secure-qrcode-tester.py` | decodifica un qr, extrae la url y consulta virustotal para verificar si es segura. |

---

## REQUISITOS GENERALES

cada programa tiene sus propias dependencias en `pyproject.toml` o `requirements.txt`. para los scripts sueltos, las dependencias mas comunes son:

- `typer`
- `rich`
- `requests`
- `beautifulsoup4`
- `pillow`
- `pyzbar`
- `qrcode`
- `python-barcode`
- `mysql-connector-python`
- `google-api-python-client`

puedes instalar las dependencias de un script concreto segun sus imports, o crear un entorno virtual en la raiz:

```bash
python -m venv .venv
source .venv/bin/activate  # windows: .venv\scripts\activate
pip install -r requirements.txt  # si existe en el subproyecto
```

---

## SEGURIDAD Y USO RESPONSABLE

- **claves api:** varios scripts incluyen claves de api publicas de ejemplo. configura tus propias claves mediante variables de entorno (por ejemplo, `vt_api_key`, `google_api_key`) antes de usarlos en serio. nunca subas claves reales al repositorio.
- **scripts de seguridad:** `default-sql-injection.py` y `search-web-defeats.py` son herramientas de prueba de concepto. usalos **solo** en entornos que te pertenezcan o con autorizacion explicita por escrito. el uso no autorizado de estas tecnicas puede ser ilegal.
- **web scraping:** respeta los terminos de servicio de los sitios web, el archivo `robots.txt` y la carga de los servidores. algunos scripts ya incluyen retrasos y verificacion de `robots.txt`.

---

## LICENCIA

- `programs/file-renamer`: mit.
- `programs/only-one-key`: uso personal; consulta al autor antes de redistribuir.
- los scripts sueltos y la documentacion de agentes: consulta los archivos individuales o asume uso personal segun la intencion del autor.

---

## AUTOR

rezzt.dev
