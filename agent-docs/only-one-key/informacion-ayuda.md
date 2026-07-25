# Documentación de Only One Key

> **Proyecto**: Only One Key — Gestor de contraseñas en consola  
> **Autor**: rezzt.dev  
> **Fecha de análisis**: 2026-07-24  
> **Repositorio**: `/home/rezzt/repositorios/desktop-projects/python-projects/py-scripting/simple-programms/only_one_key`

---

## 1. Resumen del proyecto

**Only One Key** es una aplicación de escritorio ejecutada por línea de comandos (CLI) que funciona como gestor de contraseñas personales. Permite:

- Generar contraseñas seguras de forma parametrizable.
- Analizar la fortaleza de una contraseña.
- Guardar credenciales (página/programa, usuario y contraseña) de forma encriptada.
- Consultar, modificar y eliminar credenciales guardadas.
- Proteger el acceso con una contraseña maestra ("lock password").

La aplicación está escrita en **Python 3** y organiza el código siguiendo una estructura inspirada en el patrón **MVC** (Modelo-Vista-Controlador), aunque simplificada.

---

## 2. Estructura del proyecto

```text
only_one_key/
├── README.md                         # Descripción corta del proyecto
└── app/
    ├── app.py                        # Punto de entrada de la aplicación
    ├── config/
    │   └── generalConfig.py          # Configuración general y clave Fernet
    ├── controller/
    │   ├── generalController.py      # Menú principal y enrutamiento de opciones
    │   └── functionsController.py    # Lógica de interacción con cada funcionalidad
    ├── libraries/
    │   └── imports.py                # Importaciones comunes de librerías
    ├── model/
    │   ├── accountModel.py           # Gestión de la contraseña maestra (lock)
    │   ├── helpModel.py              # Utilidades de conversión de respuestas s/n
    │   └── passwordModel.py          # Lógica de generación, análisis y CRUD de contraseñas
    └── view/
        └── mainWindow.py             # Pantalla de inicio y autenticación
```

---

## 3. Dependencias

El proyecto utiliza únicamente librerías estándar de Python y unas pocas dependencias externas. Las importaciones se centralizan en `app/libraries/imports.py`:

| Librería | Uso |
|----------|-----|
| `typer` | Lanzamiento de la aplicación desde línea de comandos (`typer.run`). |
| `time`, `datetime` | Disponibles, aunque no se usan en la versión actual. |
| `base64`, `secrets`, `string`, `hashlib` | Generación de contraseñas y hashing de la clave maestra. |
| `rich` y `rich.table`, `rich.console` | Impresión de texto con estilos y tablas en consola. |
| `pathlib` | Manejo de rutas de forma multiplataforma. |
| `cryptography.fernet.Fernet` | Encriptación simétrica de las credenciales guardadas. |
| `cryptography.hazmat.primitives` | Disponibles para derivación de claves (KDF), aunque no se usan actualmente. |
| `os`, `sys` | Rutas del sistema, limpieza de pantalla y manipulación de `sys.path`. |

Para instalar las dependencias externas necesarias:

```bash
pip install typer rich cryptography
```

---

## 4. Funcionamiento del programa

### 4.1. Punto de entrada (`app/app.py`)

El archivo `app.py` es el arranque de la aplicación. Sus responsabilidades son:

1. Ajustar `sys.path` para que Python pueda importar módulos de la carpeta `app` sin importar desde dónde se ejecute el script.
2. Importar la ventana principal desde `view.mainWindow`.
3. Llamar a `_mainWindow()` dentro de `typer.run(_main)`, lo que permite ejecutar la aplicación como un comando CLI.

Ejecución:

```bash
cd app
python app.py
```

o desde la raíz del proyecto:

```bash
python app/app.py
```

### 4.2. Ventana principal y autenticación (`app/view/mainWindow.py`)

`_mainWindow()` realiza lo siguiente:

1. **Carga la configuración criptográfica** llamando a `configLoader()`.
2. **Limpia la pantalla**.
3. **Comprueba si existe un fichero de bloqueo** (`lock.xrp`) en `~/onlyOneKey/`:
   - Si **no existe**, pide al usuario que cree una contraseña maestra. La almacena hasheada con `SHA-256` en `lock.xrp`.
   - Si **existe**, pide la contraseña maestra y permite **3 intentos** antes de cerrar. Utiliza `comprobeLock()` para comparar el hash `SHA-256` introducido con el guardado.
4. Tras superar la autenticación, limpia la pantalla y lanza `executeGeneralController()`, que muestra el menú principal.

### 4.3. Configuración criptográfica (`app/config/generalConfig.py`)

Define dos rutas importantes en el directorio personal del usuario:

```text
~/onlyOneKey/
├── shadow.key      # Clave simétrica de Fernet para encriptar/desencriptar credenciales
├── lock.xrp        # Hash SHA-256 de la contraseña maestra de acceso
└── phantom.rzt     # Fichero binario con las credenciales encriptadas (una por línea)
```

Comportamiento:

- `keyLoader()`: si `shadow.key` no existe, crea la carpeta `onlyOneKey`, genera una clave Fernet aleatoria y la guarda. Si ya existe, la lee.
- `configLoader()`: carga la clave Fernet desde `shadow.key`.
- `baseKey` y `crypter`: se exponen globalmente para que el resto de módulos puedan encriptar y desencriptar.

### 4.4. Menú principal (`app/controller/generalController.py`)

`executeGeneralController()` muestra un menú interactivo en bucle:

```text
-| Only One Key |-
 1. Generate a new Password.
 2. Analyze a Password.
 3. Save a Password.
 4. Print the Saved Password.
 5. Modify a Saved Password.
 6. Delete a Saved Password.
 7. Exit.
```

Según la opción seleccionada, delega la acción en la función correspondiente de `functionsController.py`. Si el usuario introduce una opción no válida, muestra un error y vuelve a pedir la opción.

### 4.5. Funciones de cada opción (`app/controller/functionsController.py`)

#### 4.5.1. Generar una nueva contraseña (`_generatePassword`)

- Pide la longitud deseada (mínimo 8 caracteres).
- Pregunta si debe incluir mayúsculas, minúsculas, dígitos y signos de puntuación (respuesta `s/n`).
- Llama a `passwordGenerator()` del modelo para generar la contraseña.
- Muestra la contraseña generada.
- Pregunta si se desea guardarla asociada a una página/programa y un usuario.
  - Si la respuesta es afirmativa, llama a `_saveGeneratedPassword()`, que recopila los datos y llama a `savePassword()` del modelo.

#### 4.5.2. Analizar una contraseña (`_analyzePassword`)

- Pide una contraseña por teclado.
- Llama a `passwordAnalyzer()` del modelo.
- Muestra el nivel de seguridad y una puntuación de 0 a 100 con una barra de progreso visual.

#### 4.5.3. Guardar una contraseña (`_savePassword`)

- Pide página/programa, usuario y contraseña.
- Llama a `savePassword()` del modelo para almacenar la línea encriptada en `phantom.rzt`.

#### 4.5.4. Mostrar contraseñas guardadas (`_showPassword`)

- Pide la contraseña maestra de la aplicación (3 intentos).
- Si la clave es correcta, llama a `printPasswords()` del modelo para mostrar una tabla con todas las credenciales desencriptadas.

#### 4.5.5. Modificar una contraseña guardada (`_modifyPassword`)

- Muestra todas las credenciales.
- Pide página/programa, usuario y nueva contraseña.
- Llama a `modifyPassword()` del modelo, que reescribe `phantom.rzt` actualizando la entrada correspondiente.

#### 4.5.6. Eliminar una contraseña guardada (`_deletePassword`)

- Muestra todas las credenciales.
- Pide página/programa y usuario.
- Llama a `deletePassword()` del modelo, que reescribe `phantom.rzt` omitiendo la entrada indicada.

### 4.6. Modelos (`app/model/`)

#### 4.6.1. `accountModel.py` — Contraseña maestra

- `existLockFile()`: comprueba si existe `~/onlyOneKey/lock.xrp`.
- `createLockKey(password)`: crea el fichero `lock.xrp` con el hash `SHA-256` de la contraseña.
- `returnLockKey()`: devuelve el contenido de `lock.xrp`.
- `comprobeLock(password)`: compara el hash de la contraseña introducida con el hash almacenado.

#### 4.6.2. `helpModel.py` — Utilidades

- `_testQuestion(response)`: convierte una respuesta `s/n` en un valor booleano. Si la respuesta no es válida, asume `True` (sí) por defecto.

#### 4.6.3. `passwordModel.py` — Lógica de contraseñas

- **`passwordGenerator(length, uppercase, lowercase, digits, punctuation)`**: genera una contraseña aleatoria usando `secrets.choice()`. Asegura que cada tipo de carácter solicitado aparezca al menos una vez mediante un bucle de validación.
- **`passwordAnalyzer(password)`**: evalúa 5 criterios (longitud ≥ 8, mayúsculas, minúsculas, dígitos, signos de puntuación). Devuelve un nivel de seguridad (`very safe`, `safe`, `weak`, `very weak`) y una puntuación sobre 100.
- **`savePassword(crypter, page, username, password)`**: encripta la cadena `page:username:password` con Fernet y la añade a `phantom.rzt` en modo binario append (`ab`).
- **`printPasswords()`**: lee `phantom.rzt`, desencripta cada línea, separa los campos por `:` y muestra los resultados en una tabla con `rich`.
- **`modifyPassword(crypter, page, username, newPassword)`**: lee todo el fichero, desencripta línea a línea, busca la coincidencia por página y usuario, re-encripta la entrada con la nueva contraseña y reescribe el fichero.
- **`deletePassword(crypter, page, username)`**: similar a `modifyPassword`, pero omite la entrada coincidente y reescribe el fichero sin ella.

---

## 5. Flujo completo de uso

1. El usuario ejecuta `python app/app.py`.
2. La aplicación carga o genera la clave Fernet en `~/onlyOneKey/shadow.key`.
3. Si es la primera ejecución, pide crear una contraseña maestra y la guarda hasheada en `~/onlyOneKey/lock.xrp`.
4. Si ya existía la contraseña maestra, pide introducirla (3 intentos).
5. Tras autenticarse, aparece el menú principal.
6. El usuario elige generar, analizar, guardar, consultar, modificar o eliminar contraseñas.
7. Las credenciales guardadas se almacenan encriptadas en `~/onlyOneKey/phantom.rzt`.
8. Para consultar, modificar o eliminar credenciales, se vuelve a pedir la contraseña maestra.
9. Al elegir "7. Exit", el programa finaliza.

---

## 6. Datos almacenados en el sistema

La aplicación guarda todos sus datos en el directorio del usuario:

```text
~/onlyOneKey/
├── shadow.key      # Clave de encriptación de credenciales (Fernet, 32 bytes en base64)
├── lock.xrp        # Hash SHA-256 de la contraseña maestra
└── phantom.rzt     # Credenciales encriptadas en formato binario (líneas separadas por \n)
```

> **Importante**: estos ficheros contienen información sensible. El directorio `~/onlyOneKey` debería protegerse adecuadamente a nivel de sistema operativo.

---

## 7. Observaciones y recomendaciones de seguridad

Aunque el programa cumple con un objetivo funcional básico, conviene conocer los siguientes aspectos:

1. **Contraseña maestra en SHA-256**: el fichero `lock.xrp` almacena un hash SHA-256 sin sal (salt) ni iteraciones. Esto facilita ataques de fuerza bruta con tablas arcoíris si alguien accede al fichero. Una mejora sería usar `bcrypt`, `scrypt` o `Argon2`.
2. **Clave Fernet en disco**: `shadow.key` es la clave real de cifrado. Si un atacante obtiene `shadow.key` y `phantom.rzt`, puede desencriptar todas las credenciales sin conocer la contraseña maestra. La contraseña maestra solo protege la interfaz de consulta, no el cifrado del almacenamiento. Idealmente, la clave debería derivarse de la contraseña maestra (por ejemplo, con PBKDF2).
3. **Persistencia en `append`**: `savePassword()` abre el fichero en modo `ab` (append binario), lo cual es correcto para añadir entradas, pero no verifica duplicados.
4. **Separador de campos**: los datos se concatenan con `:` antes de cifrar. Si el usuario introduce `:` en la página, el usuario o la contraseña, el desencriptado con `.split(":")` fallará o generará resultados incorrectos.
5. **Entrada numérica no validada**: `generalController.py` convierte directamente la opción del menú a `int` sin manejo previo de errores, aunque la excepción se captura dentro del bloque `match`.
6. **No hay persistencia de configuración adicional**: la aplicación no usa `config.toml`, `.env` ni bases de datos; toda la persistencia son los tres ficheros de `~/onlyOneKey`.

---

## 8. Posibles mejoras futuras

- Reemplazar SHA-256 por un algoritmo de hashing de contraseñas lento y con sal (Argon2, bcrypt).
- Derivar la clave de cifrado Fernet a partir de la contraseña maestra en lugar de guardarla en un fichero independiente.
- Añadir confirmación antes de eliminar o modificar una entrada.
- Evitar que los campos de entrada contengan el carácter `:` o escaparlo adecuadamente.
- Implementar un sistema de búsqueda o filtrado de credenciales.
- Añadir un `requirements.txt` para facilitar la instalación de dependencias.
- Incluir tests unitarios para `passwordGenerator`, `passwordAnalyzer`, `savePassword`, `modifyPassword` y `deletePassword`.
- Mejorar la gestión de excepciones para ofrecer mensajes más descriptivos.

---

## 9. Instrucciones de ejecución

1. Clonar o colocar el proyecto en la ruta deseada.
2. Instalar las dependencias:

```bash
pip install typer rich cryptography
```

3. Ejecutar la aplicación:

```bash
python app/app.py
```

4. Seguir las instrucciones en pantalla para crear la contraseña maestra (primera ejecución) o iniciar sesión (ejecuciones posteriores).

---

## 10. Conclusión

**Only One Key** es un gestor de contraseñas de consola funcional, con una arquitectura clara separada en configuración, modelos, controladores y vista. Es útil como proyecto de aprendizaje o como herramienta personal básica, aunque requiere endurecer el modelo de seguridad si se pretende usar con credenciales reales de alto valor.
