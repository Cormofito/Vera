/* VERA · Solicitar un informe (web pública)
   Enlaza el formulario de Google donde el usuario adjunta el EPAR o el ensayo publicado.
   Se carga desde la cabecera de index.html, que el regenerado de la web conserva. */
(function () {
  var FORM = 'https://forms.gle/VDJCY6Z9N5afV3Us5';
  var TXT = 'Adjunta el EPAR o el ensayo publicado y recibirás en tu correo, en menos de 24 horas, un informe automático en PDF y Word. ' +
    'No está revisado por VERA: verificar los datos es responsabilidad tuya. También puedes proponer que VERA lo revise y lo publique.';

  function link(cls, text) {
    var a = document.createElement('a');
    a.className = cls; a.href = FORM; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = text;
    return a;
  }

  function init() {
    // 1. Recuadro al final de la lista de resultados.
    var cta = document.querySelector('#lvList .cta');
    if (cta) {
      cta.innerHTML = '<div><b>¿No está el fármaco que buscas?</b><span></span></div>';
      cta.querySelector('span').textContent = TXT;
      cta.appendChild(link('btn primary', 'Solicitar un informe'));
    }
    // 2. Línea discreta en la portada, bajo las especialidades.
    var esps = document.querySelector('#lvHome .esps');
    if (esps && !document.getElementById('solHome')) {
      var p = document.createElement('p');
      p.id = 'solHome'; p.className = 'note';
      p.style.cssText = 'text-align:center;margin-top:18px';
      p.appendChild(document.createTextNode('¿No encuentras un fármaco? '));
      p.appendChild(link('', 'Solicita un informe'));
      esps.appendChild(p);
    }
    // 3. Búsquedas sin resultados.
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
