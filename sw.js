/* VERA · service worker
   - Páginas (portada e informes): primero la red, con copia guardada para usar sin conexión.
     Así, cada vez que se publica algo en la web, la app lo muestra en cuanto hay conexión.
   - Resto de archivos propios: copia guardada y se renueva en segundo plano.
   - Librerías y fuentes externas (jsPDF, Google Fonts…): copia guardada.
   - Al instalarse y una vez al día, guarda una copia de todos los informes enlazados
     desde la portada para poder consultarlos sin cobertura.
   Solo hay que cambiar VERSION si se modifica este archivo. */
const VERSION = 'vera-sw-2';
const PAGES = VERSION + '-pages';
const FILES = VERSION + '-files';
const EXTERNAL = VERSION + '-external';
const SHELL = [
  './', './index.html', './instalar.html', './solicitar.html', './manifest.webmanifest',
  './favicon.svg', './favicon-32.png', './apple-touch-icon.png',
  './icon-192.png', './icon-512.png', './icon-maskable-512.png', './qr-vera.svg'
];
const NET_TIMEOUT_MS = 4000;

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const pages = await caches.open(PAGES);
    const files = await caches.open(FILES);
    await Promise.all(SHELL.map(async url => {
      try {
        const res = await fetch(url, { cache: 'no-cache' });
        if (res.ok) await (/\.html$|\/$/.test(url) ? pages : files).put(url, res);
      } catch (e) { /* sin red: se guardará la próxima vez */ }
    }));
    await warmReports();
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keep = [PAGES, FILES, EXTERNAL];
    for (const key of await caches.keys()) if (!keep.includes(key)) await caches.delete(key);
    await self.clients.claim();
  })());
});

self.addEventListener('message', event => {
  if (event.data === 'warm') event.waitUntil(warmReports());
});

// Guarda la versión actual de cada informe enlazado desde la portada.
async function warmReports() {
  try {
    const res = await fetch('./index.html', { cache: 'no-cache' });
    if (!res.ok) return;
    const html = await res.clone().text();
    const pages = await caches.open(PAGES);
    await pages.put('./index.html', res);
    const links = [...new Set(html.match(/informes\/[A-Za-z0-9._-]+\.html/g) || [])];
    await Promise.all(links.map(async link => {
      try {
        const r = await fetch('./' + link, { cache: 'no-cache' });
        if (r.ok) await pages.put('./' + link, r);
      } catch (e) {}
    }));
  } catch (e) {}
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  if (sameOrigin && url.pathname.endsWith('/sw.js')) return;
  const isPage = req.mode === 'navigate' || (sameOrigin && /\.html$|\/$/.test(url.pathname));
  if (isPage && sameOrigin) event.respondWith(networkFirst(event, req));
  else if (sameOrigin) event.respondWith(staleWhileRevalidate(event, req, FILES));
  else if (/fonts\.(googleapis|gstatic)\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|unpkg\.com/.test(url.hostname))
    event.respondWith(staleWhileRevalidate(event, req, EXTERNAL));
});

async function networkFirst(event, req) {
  const cache = await caches.open(PAGES);
  const network = fetch(req);
  event.waitUntil(network.then(res => res.ok ? cache.put(req, res.clone()) : null).catch(() => {}));
  network.catch(() => {});
  const timeout = new Promise(resolve => setTimeout(resolve, NET_TIMEOUT_MS));
  try {
    const res = await Promise.race([network, timeout]);
    if (res) return res;
  } catch (e) {}
  // Sin red o red muy lenta (p. ej. bloqueos): copia guardada.
  const cached = await cache.match(req, { ignoreSearch: true });
  if (cached) return cached;
  try { return await network; } catch (e) {}
  return (await cache.match('./index.html')) || new Response(
    '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<p style="font:16px sans-serif;padding:24px">Sin conexión y esta página aún no está guardada en el teléfono. Vuelve a intentarlo cuando tengas cobertura.</p>',
    { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

async function staleWhileRevalidate(event, req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const network = fetch(req);
  event.waitUntil(network.then(res => (res.ok || res.type === 'opaque') ? cache.put(req, res.clone()) : null).catch(() => {}));
  if (cached) return cached;
  return network;
}
