/* VERA · Solicitar un informe (web pública)
   Da acceso a solicitar.html (proceso explicado y enlace al formulario de Google) desde
   la barra superior, la portada, el final de cada lista y las búsquedas sin resultados.
   Se carga desde la cabecera de index.html, que el regenerado de la web conserva. */
(function () {
  var PAGE = 'solicitar.html';
  var TXT = 'Adjunta el EPAR o el ensayo publicado y recibirás en tu correo, normalmente en pocas horas, un informe de evaluación en PDF y Word. ' +
    'Se genera automáticamente y no está revisado por VERA: verificar los datos es responsabilidad tuya.';

  function link(cls, text) {
    var a = document.createElement('a');
    a.className = cls; a.href = PAGE; a.textContent = text;
    return a;
  }

  function css() {
    var s = document.createElement('style');
    s.textContent =
      '.sol-nav{margin-left:auto;font-size:14px;font-weight:600;color:var(--accent);text-decoration:none;padding:7px 12px;border:1px solid var(--accent);border-radius:8px;white-space:nowrap}' +
      '.sol-nav:hover{background:var(--accent-soft,rgba(31,78,121,.08))}' +
      '.sol-home{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:center;max-width:760px;width:100%;margin:0 auto;' +
      'padding:14px 18px;border:1px dashed var(--line);border-radius:12px;font-size:14px;color:var(--muted);text-align:left}' +
      '.sol-home b{color:var(--fg)}' +
      '@media (max-width:520px){.sol-nav{padding:6px 10px;font-size:13px}.sol-home{justify-content:flex-start}}';
    document.head.appendChild(s);
  }

  function init() {
    css();
    // 1. Botón en la barra superior.
    var nav = document.querySelector('.nav .nav-in');
    if (nav && !nav.querySelector('.sol-nav')) nav.appendChild(link('sol-nav', 'Solicitar informe'));
    // 2. Recuadro en la portada, bajo el buscador.
    var box = document.querySelector('#lvHome .searchbox');
    if (box && !document.getElementById('solHome')) {
      var d = document.createElement('div');
      d.id = 'solHome'; d.className = 'sol-home';
      d.innerHTML = '<span><b>¿No está el fármaco que buscas?</b> Pide un informe con su EPAR o su ensayo.</span>';
      d.appendChild(link('btn', 'Solicitar un informe'));
      box.parentNode.insertBefore(d, box.nextSibling);
    }
    // 3. Recuadro al final de la lista de resultados.
    var cta = document.querySelector('#lvList .cta');
    if (cta) {
      cta.innerHTML = '<div><b>¿No está el fármaco que buscas?</b><span></span></div>';
      cta.querySelector('span').textContent = TXT;
      cta.appendChild(link('btn primary', 'Solicitar un informe'));
    }
    // 4. Búsquedas sin resultados.
    var res = document.getElementById('results');
    if (res && window.MutationObserver) {
      var addToEmpty = function () {
        var empty = res.querySelector('.empty');
        if (empty && !empty.querySelector('.sol-link')) {
          var s = document.createElement('span');
          s.className = 'sol-link';
          s.appendChild(document.createTextNode('Si no está en VERA, '));
          s.appendChild(link('', 'solicita un informe'));
          s.appendChild(document.createTextNode(' con su EPAR o ensayo.'));
          empty.appendChild(s);
        }
      };
      new MutationObserver(addToEmpty).observe(res, { childList: true });
      addToEmpty();
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
