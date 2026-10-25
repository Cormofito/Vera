# VERA · web pública de solo lectura

Portal de informes de evaluación de medicamentos.
Esta carpeta se publica tal cual con Cloudflare Pages: no hay que compilar nada.

- `index.html`: portada con buscador y carpetas por especialidad.
- `informes/`: un informe completo por fármaco (PDF y Word descargables desde cada uno).
- `_headers` y `robots.txt`: evitan que los buscadores indexen la web.
- App instalable (PWA): `manifest.webmanifest`, `sw.js` (copia sin conexión; las páginas se piden primero a la red, así que se actualizan solas), `pwa.js` (registro y aviso de instalación en la portada), iconos `icon-*.png`.
- `solicitar.html` y `solicitar.js`: sección «Solicitar un informe» (proceso, aviso y enlace al formulario de Google); `solicitar.js` añade los accesos en la barra superior, la portada, las listas y las búsquedas sin resultados.
- `herramientas/`: generador de informes automáticos (`vera_auto.py`), envío por correo (`vera_enviar.py`) y plantilla del script de Google Apps (sin la clave).
- `instalar.html`: página para compartir con el equipo (instrucciones para Android e iPhone y código QR `qr-vera.svg`).

Los archivos los genera Claude a partir de los artefactos de VERA; no se editan a mano aquí.
