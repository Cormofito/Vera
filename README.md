# VERA · web pública de solo lectura

Portal de informes de evaluación de medicamentos.
Esta carpeta se publica tal cual con Cloudflare Pages: no hay que compilar nada.

- `index.html`: portada con buscador y carpetas por especialidad.
- `informes/`: un informe completo por fármaco (PDF y Word descargables desde cada uno).
- `_headers` y `robots.txt`: evitan que los buscadores indexen la web.

Los archivos los genera Claude a partir de los artefactos de VERA; no se editan a mano aquí.
