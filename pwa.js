/* VERA · app instalable
   Registra el service worker (copia sin conexión y actualización automática) y ofrece instalar
   VERA con un aviso pequeño que se puede cerrar (×; no vuelve a salir en 30 días):
   - en la portada y en los informes (no en instalar.html ni solicitar.html);
   - Android/Chrome: botón «Instalar» cuando el navegador lo permite; si no lo permite en unos
     segundos (navegadores dentro de WhatsApp, Gmail, Instagram…, Firefox, Samsung Internet),
     explica el paso del menú y remite a instalar.html;
   - iPhone: Safari (Compartir abajo), Chrome (Compartir arriba) o, dentro de otra app, abrir en Safari. */
(function () {
  var me = document.currentScript;
  var base = new URL('./', me && me.src ? me.src : location.href);
  var showBanner = !/\/(instalar|solicitar)\.html$/.test(location.pathname);

  function store(key, val) {
    try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; }
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register(new URL('sw.js', base).href, { scope: base.href }).then(function () {
        // Una vez al día, renovar la copia sin conexión de todos los informes.
        var today = new Date().toISOString().slice(0, 10);
        if (store('vera-warm') !== today) {
          navigator.serviceWorker.ready.then(function (reg) {
            if (reg.active) { reg.active.postMessage('warm'); store('vera-warm', today); }
          });
        }
      }).catch(function () {});
    });
  }

  if (!showBanner) return;
  var standalone = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  if (standalone) return;
  var hidden = Number(store('vera-install-hidden') || 0);
  if (hidden && Date.now() - hidden < 30 * 864e5) return;

  var ua = navigator.userAgent || '';
  var isIOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var isAndroid = /Android/.test(ua);
  // Navegador dentro de otra app: por el agente de usuario o porque la abrió una app Android
  // (WhatsApp, Gmail… abren una pestaña de Chrome con referrer android-app://, sin opción de instalar).
  var inApp = /FBAN|FBAV|FB_IAB|Instagram|LinkedInApp|Line\/|Twitter|MicroMessenger|GSA\/|; wv\)/.test(ua) ||
    /^android-app:/.test(document.referrer || '');
  var help = new URL('instalar.html', base).href;
  var deferred = null;

  var css = document.createElement('style');
  css.textContent =
    '.vera-install{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:1000;' +
    'max-width:520px;margin:0 auto;display:flex;gap:12px;align-items:center;padding:12px 12px 12px 14px;border-radius:12px;' +
    'background:var(--bg,#f6f7f8);color:var(--fg,#1b2430);border:1px solid var(--line,#d9dde3);' +
    'box-shadow:0 6px 24px rgba(0,0,0,.18);font:14px/1.4 "IBM Plex Sans",-apple-system,BlinkMacSystemFont,sans-serif}' +
    '.vera-install img{width:40px;height:40px;flex:none;border-radius:50%}' +
    '.vera-install .t{flex:1;min-width:0}.vera-install b{display:block;font-weight:600}' +
    '.vera-install .s{color:var(--muted,#5b6675);font-size:13px}.vera-install .s b{display:inline}' +
    '.vera-install .s a{color:var(--accent,#1f4e79);font-weight:600}' +
    '.vera-install button{font:inherit;cursor:pointer;border-radius:8px}' +
    '.vera-install .go{background:var(--accent,#1f4e79);color:#fff;border:0;padding:9px 14px;font-weight:600}' +
    '@media (prefers-color-scheme:dark){.vera-install .go{color:#12161c}}' +
    '.vera-install .x{background:none;border:0;color:var(--muted,#5b6675);font-size:20px;line-height:1;padding:6px 8px}';
  document.head.appendChild(css);

  var SHARE = '<svg width="13" height="15" viewBox="0 0 13 15" aria-hidden="true" style="vertical-align:-2px"><path d="M6.5 1v9M3 4.5 6.5 1 10 4.5M1.5 7v6.5h10V7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var DOTS = '<b>⋮</b>';
  var MORE = ' <a href="' + help + '">Ver cómo</a>';

  // Muestra (o sustituye) el aviso.
  function banner(text, sub, action) {
    var old = document.querySelector('.vera-install');
    if (old) old.remove();
    var el = document.createElement('div');
    el.className = 'vera-install';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'Instalar VERA');
    el.innerHTML = '<img src="' + new URL('icon-192.png', base).href + '" alt=""><div class="t"><b></b><span class="s"></span></div>' +
      (action ? '<button class="go" type="button">Instalar</button>' : '') +
      '<button class="x" type="button" aria-label="Ahora no">×</button>';
    el.querySelector('b').textContent = text;
    el.querySelector('.s').innerHTML = sub;
    if (action) el.querySelector('.go').onclick = action;
    el.querySelector('.x').onclick = function () { store('vera-install-hidden', String(Date.now())); el.remove(); };
    document.body.appendChild(el);
  }

  // Android y Chrome/Edge de escritorio: el navegador ofrece la instalación con un botón.
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferred = e;
    banner(isAndroid || isIOS ? 'Instala VERA en tu móvil' : 'Instala VERA en tu ordenador',
      'Icono propio, funciona sin conexión y se actualiza sola.', function () {
        var box = document.querySelector('.vera-install');
        deferred.prompt();
        deferred.userChoice.then(function () { deferred = null; if (box) box.remove(); });
      });
  });
  window.addEventListener('appinstalled', function () {
    var box = document.querySelector('.vera-install');
    if (box) box.remove();
  });

  // Móviles donde el navegador no ofrece el botón: se explica el paso.
  function fallback() {
    if (deferred || document.querySelector('.vera-install')) return;
    if (isIOS) {
      if (inApp || !/Safari\//.test(ua)) {
        banner('Instala VERA en tu iPhone', 'Abre esta página en <b>Safari</b> y toca Compartir ' + SHARE + ' › <b>Añadir a pantalla de inicio</b>.' + MORE, null);
      } else if (/CriOS|EdgiOS|FxiOS/.test(ua)) {
        banner('Instala VERA en tu iPhone', 'Toca Compartir ' + SHARE + ' (arriba a la derecha) › <b>Añadir a pantalla de inicio</b>.' + MORE, null);
      } else {
        banner('Instala VERA en tu iPhone', 'Toca Compartir ' + SHARE + ' y luego <b>Añadir a pantalla de inicio</b>.', null);
      }
    } else if (isAndroid) {
      if (inApp) {
        banner('Instala VERA en tu móvil', 'Toca el menú ' + DOTS + ' › <b>Abrir en Chrome</b> y allí te saldrá el botón para instalarla.' + MORE, null);
      } else if (/SamsungBrowser/.test(ua)) {
        banner('Instala VERA en tu móvil', 'Menú <b>≡</b> › <b>Añadir página a</b> › <b>Pantalla de inicio</b>.' + MORE, null);
      } else if (/Firefox/.test(ua)) {
        banner('Instala VERA en tu móvil', 'Menú ' + DOTS + ' › <b>Instalar</b> o <b>Añadir a pantalla de inicio</b>.' + MORE, null);
      } else {
        banner('Instala VERA en tu móvil', 'Menú ' + DOTS + ' › <b>Añadir a pantalla de inicio</b>. Si no aparece, ábrela en Chrome.' + MORE, null);
      }
    }
  }
  window.addEventListener('load', function () { setTimeout(fallback, isIOS ? 1500 : 4000); });
})();
