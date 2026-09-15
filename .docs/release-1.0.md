# release 1.0.0

## titulo

py.scripts v1.0.0 — primera release publica

## descripcion

primera version estable de la coleccion personal de scripts, utilidades y pequenos programas en python. el repositorio queda organizado en tres areas: programas empaquetados con instalacion propia, scripts sueltos de uso rapido, y documentacion para agentes de ia.

### incluye

**programas (`programs/`)**
- `file-renamer` (simplefilerenamer): cli multiplataforma para renombrado masivo de archivos, con modo interactivo y modo batch. incluye suite de tests con pytest. licencia mit propia.
- `only-one-key`: gestor de contrasenas en consola con almacenamiento encriptado (fernet), autenticacion con argon2id, generador/analizador de fortaleza de contrasenas y copias de seguridad automaticas del vault.

**scripts (`scripting/`)**
- codigos de barras y qr: generacion y extraccion de codigos upc y qr.
- web scraping: extraccion de precios/stock, descarga de imagenes y auditoria tecnica seo.
- web y seguridad: analisis de formularios/enlaces, busqueda web via google custom search y verificacion de urls con virustotal.
- scripts educativos de seguridad (inyeccion sql, analisis de malware, verificacion de qr) para uso exclusivo en entornos de prueba autorizados.

**documentacion (`agent-docs/`)**
- skills y guias de referencia para agentes de ia (seo, ayuda de only-one-key).

**legal**
- terminos de licencia formalizados bajo derecho espanol (rdleg 1/1996) y el convenio de berna, con exencion de garantia y limitacion de responsabilidad. licencia general del repositorio: todos los derechos reservados, salvo excepciones ya publicadas (`file-renamer` con licencia mit).

> nota: varios scripts son educativos o de prueba de concepto. revisalos antes de ejecutarlos en entornos reales y configura tus propias claves de api mediante variables de entorno.
