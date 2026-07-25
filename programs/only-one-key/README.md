# ONLY ONE KEY

gestor de contrasenas personal para consola con interfaz interactiva minimalista.

## CARACTERISTICAS

- interfaz interactiva en consola compatible con la mayoria de terminales.
- estilo minimalista inspirado en rezzt.dev: fondo oscuro, texto blanco/gris y
  acento coral solo para acciones destructivas.
- menu principal con numeros, alternancia de visibilidad de contrasenas y opcion `Q` para salir.
- alternar visibilidad (`0`) muestra las credenciales directamente con el nuevo estado.
- operaciones sensibles piden la contrasena maestra; si el vault esta vacio se evita la solicitud innecesaria.
- generacion de contrasenas seguras parametrizables con copia al portapapeles multiplataforma.
- analisis de fortaleza de contrasenas con penalizacion para claves cortas.
- almacenamiento encriptado de credenciales con escritura atomica y sincronizada del vault.
- consulta, busqueda, modificacion y eliminacion de credenciales guardadas.
- modificacion y eliminacion por id de fila (no es necesario escribir pagina y usuario).
- autenticacion con contrasena maestra usando argon2id.
- clave de cifrado derivada de la contrasena maestra (nunca se almacena en disco).
- cambio de contrasena maestra con recifrado completo del vault.
- copias de seguridad automaticas del vault antes de cada modificacion.
- arquitectura limpia separada en configuracion, modelos, core, ui y utilidades.
- tests unitarios con `pytest`.

## INSTALACION

```bash
cd programs/only-one-key
pip install -r requirements.txt
```

para un entorno de desarrollo completo con tests:

```bash
pip install -e ".[dev]"
```

## USO

iniciar la interfaz interactiva:

```bash
python -m only_one_key
```

o, desde la raiz del proyecto:

```bash
python src/only_one_key/app.py
```

mostrar la version:

```bash
python -m only_one_key --version
```

## DATOS DEL USUARIO

la aplicacion almacena sus datos en `~/.only_one_key/`:

- `lock.argon2` — hash argon2id de la contrasena maestra.
- `salt.bin` — sal publica para derivar la clave de cifrado.
- `vault.rzt` — credenciales encriptadas (una por linea).
- `vault.rzt.bak` — copia de seguridad del vault.

## TESTS

```bash
pytest
```

## SEGURIDAD

- el hash maestro usa argon2id con parametros robustos.
- la clave fernet se deriva en memoria con pbkdf2-hmac-sha256 a partir de la
  contrasena maestra y la sal almacenada; no se guarda nunca en disco.
- cada credencial se serializa como json y se encripta individualmente con fernet,
  evitando problemas con separadores como `:` en los campos.
- el vault se respalda automaticamente antes de cualquier modificacion.
- si el cambio de contrasena maestra falla, se restaura el backup del vault.

## LICENCIA

uso personal. consulta el autor antes de redistribuir.
