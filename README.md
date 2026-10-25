# VERA · web pública de solo lectura

Portal de informes de evaluación de medicamentos.
Esta carpeta se publica tal cual con Cloudflare Pages: no hay que compilar nada.

- `index.html`: portada con buscador y carpetas por especialidad.
- `informes/`: un informe completo por fármaco (PDF y Word descargables desde cada uno).
- `_headers` y `robots.txt`: evitan que los buscadores indexen la web.
- App instalable (PWA): `manifest.webmanifest`, `sw.js` (copia sin conexión; las páginas se piden primero a la red, así que se actualizan solas), `pwa.js` (registro y aviso de instalación en la portada), iconos `icon-*.png`.
- `instalar.html`: página para compartir con el equipo (instrucciones para Android e iPhone y código QR `qr-vera.svg`).

Los archivos los genera Claude a partir de los artefactos de VERA; no se editan a mano aquí.
