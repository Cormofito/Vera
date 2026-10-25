/* VERA · app instalable
   Registra el service worker (copia sin conexión y actualización automática) y,
   en la portada (script con data-banner), ofrece instalar VERA en el móvil. */
(function () {
  var me = document.currentScript;
  var base = new URL('./', me && me.src ? me.src : location.href);
  var showBanner = !!(me && me.hasAttribute('data-banner'));

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
  var deferred = null;

  var css = document.createElement('style');
  css.textContent =
    '.vera-install{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:1000;' +
    'max-width:520px;margin:0 auto;display:flex;gap:12px;align-items:center;padding:12px 12px 12px 14px;border-radius:12px;' +
    'background:var(--bg,#f6f7f8);color:var(--fg,#1b2430);border:1px solid var(--line,#d9dde3);' +
    'box-shadow:0 6px 24px rgba(0,0,0,.18);font:14px/1.4 "IBM Plex Sans",-apple-system,BlinkMacSystemFont,sans-serif}' +
    '.vera-install img{width:40px;height:40px;flex:none;border-radius:50%}' +
    '.vera-install .t{flex:1;min-width:0}.vera-install b{display:block;font-weight:600}' +
    '.vera-install .s{color:var(--muted,#5b6675);font-size:13px}' +
    '.vera-install button{font:inherit;cursor:pointer;border-radius:8px}' +
    '.vera-install .go{background:var(--accent,#1f4e79);color:#fff;border:0;padding:9px 14px;font-weight:600}' +
    '@media (prefers-color-scheme:dark){.vera-install .go{color:#12161c}}' +
    '.vera-install .x{background:none;border:0;color:var(--muted,#5b6675);font-size:20px;line-height:1;padding:6px 8px}';
  document.head.appendChild(css);

  function banner(text, sub, action) {
    if (document.querySelector('.vera-install')) return;
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

  // Android y Chrome/Edge de escritorio: el navegador ofrece la instalación.
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferred = e;
    banner('Instala VERA en tu móvil', 'Icono en la pantalla de inicio, funciona sin conexión y se actualiza sola.', function () {
      var box = document.querySelector('.vera-install');
      deferred.prompt();
      deferred.userChoice.then(function () { deferred = null; if (box) box.remove(); });
    });
  });
  window.addEventListener('appinstalled', function () {
    var box = document.querySelector('.vera-install');
    if (box) box.remove();
  });

  // iPhone/iPad: no hay botón de instalación; se explica el paso.
  if (isIOS) {
    window.addEventListener('load', function () {
      setTimeout(function () {
        banner('Instala VERA en tu iPhone',
          'Toca <b style="display:inline">Compartir</b> ' +
          '<svg width="13" height="15" viewBox="0 0 13 15" aria-hidden="true" style="vertical-align:-2px"><path d="M6.5 1v9M3 4.5 6.5 1 10 4.5M1.5 7v6.5h10V7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
          ' y luego <b style="display:inline">Añadir a pantalla de inicio</b>.', null);
      }, 1500);
    });
  }
})();
