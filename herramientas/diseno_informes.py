#!/usr/bin/env python3
"""VERA · aplica el diseño v1 a la fuente de un informe completo (artefacto de claude.ai).

Uso: python3 herramientas/diseno_informes.py informe.html [más.html ...]   (modifica los archivos)

Cambios (idempotente: si el informe ya los tiene, no hace nada):
  - Barra superior con el logo de VERA y «← Buscador», igual que la portada.
  - Sin «prototipo vX» ni «VERA ·» repetido en la cabecera.
  - El contador «Datos verificados frente al EPAR» solo lo ve la propietaria.
  - Tablas compactas: la página del EPAR como etiqueta pequeña junto al dato y lo pendiente de
    verificar como un punto ámbar (con leyenda en la cabecera), en vez de dos líneas más por fila.
  - «Ficha en 30 segundos» sin huecos grises cuando la última fila no se llena.
  - Móvil: el índice pasa a una tira de secciones fija arriba, en vez de ir antes del contenido.
  - v1.3: en oncología y hematología (HR), delta de ESMO-MCBS (0,65) y su inverso (1,54) en discontinuas.
  - v1.2: bajo el diagrama de bosque de la comparación indirecta, «← Favorece a X | Favorece a Y →».
  - v1.1: las tablas (sobre todo la de eficacia) caben enteras en ordenador y tableta; en el móvil
    siguen desplazándose en horizontal.
"""
import re
import sys

MARCA = '/* VERA diseño v1 */'
PORTAL = 'https://claude.ai/artifact/82F9DBpQWW9Nio5RFFQ2a1'
LOGO = ('<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="21"/>'
        '<path d="M13 16 L24 35 L36 11"/></svg>')

CSS = MARCA + '''
.vnav{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--surface);border-bottom:1px solid var(--line);margin-left:calc(-1 * max(16px,env(safe-area-inset-left,0px)));margin-right:calc(-1 * max(16px,env(safe-area-inset-right,0px)));padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.vnav-in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:14px;min-height:56px}
.vnav-brand{display:flex;align-items:center;gap:9px;text-decoration:none;color:var(--fg);font-family:var(--f-display);font-weight:600;letter-spacing:.14em;font-size:20px}
.vnav-brand svg{width:26px;height:26px}
.vnav-brand circle{fill:none;stroke:var(--accent);stroke-width:2.6}
.vnav-brand path{fill:none;stroke:var(--accent);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.vnav-back{margin-left:auto;font-size:14px;font-weight:600;color:var(--accent);text-decoration:none;padding:7px 12px;border:1px solid var(--accent);border-radius:8px;white-space:nowrap}
.vnav-back:hover{background:var(--accent-soft)}
html:not(.owner) .progress{display:none}
nav.toc{top:calc(env(safe-area-inset-top,0px) + 72px)}
section{scroll-margin-top:72px}
td .src{display:inline-block;margin:0 0 0 6px;font-size:11px;line-height:16px;padding:0 6px;border-radius:4px;background:var(--sunk);color:var(--muted);vertical-align:1px;white-space:nowrap}
.read tr.nv>td:first-child::after,.read .tl.nv>span:last-child::after,.vdot{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--warn);margin:0 0 1px 7px;vertical-align:middle}
.vlegend{display:flex;flex-wrap:wrap;gap:4px 18px;align-items:center;font-size:12.5px;color:var(--muted)}
.vlegend .vdot{margin:0 6px 1px 0}
.vlegend .vsrc{display:inline-block;font-size:11px;line-height:16px;padding:0 6px;border-radius:4px;background:var(--sunk);margin-right:6px}
.ficha{background:var(--surface)}
.ficha>div{box-shadow:1px 0 0 var(--line),0 1px 0 var(--line)}
@media (max-width:900px){
  nav.toc{display:block;position:sticky;top:calc(env(safe-area-inset-top,0px) + 56px);z-index:15;background:var(--bg);margin:0 -16px;padding:8px 16px;border-bottom:1px solid var(--line)}
  nav.toc .progress{display:none}
  nav.toc ol{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  nav.toc ol::-webkit-scrollbar{display:none}
  nav.toc a{white-space:nowrap;border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:5px 12px;font-size:13px}
  section{scroll-margin-top:120px}
}
'''

NAV = (f'<nav class="vnav" aria-label="VERA"><div class="vnav-in">'
       f'<a class="vnav-brand" href="{PORTAL}" target="_top">{LOGO}<span>VERA</span></a>'
       f'<a class="vnav-back" href="{PORTAL}" target="_top">← Buscador</a></div></nav>\n')

LEYENDA = ('\n  <div class="vlegend read-only" aria-label="Leyenda"><span><i class="vdot"></i>Pendiente de verificar frente al EPAR</span>'
           '<span><span class="vsrc">p. 108</span>Página del documento fuente</span></div>')


MARCA11 = '/* VERA diseño v1.1 */'
CSS11 = MARCA11 + '''
td.num{white-space:normal;font-size:13.5px}
td{overflow-wrap:break-word}
@media (min-width:701px){table{min-width:0}}
@media (max-width:1100px){th{letter-spacing:.02em;font-size:11.5px}}
td.num .nw{white-space:nowrap}
@media (max-width:1100px){
  .wrap{grid-template-columns:minmax(0,1fr)}
  nav.toc{display:block;position:sticky;top:calc(env(safe-area-inset-top,0px) + 56px);z-index:15;background:var(--bg);margin:0 -16px;padding:8px 16px;border-bottom:1px solid var(--line)}
  nav.toc .progress{display:none}
  nav.toc ol{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}
  nav.toc ol::-webkit-scrollbar{display:none}
  nav.toc a{white-space:nowrap;border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:5px 12px;font-size:13px}
  section{scroll-margin-top:120px}
}
@media (min-width:701px){.tbl th:first-child{width:30%}}
'''
# Mantiene juntos los intervalos de confianza, «HR 0,55», «3,8 m», «p=0,01»… para que la línea solo se parta entre ellos.
# Solo envuelve en <span class="nw">: el texto (y por tanto el PDF y el Word) no cambia.
JS11 = r'''<script>/* VERA diseño v1.1 */(function(){
const RX=/\([^()]*\)|(?:HR|RR|OR|IRR|DM)\s?[−-]?\d[\d.,]*|p\s?[=<>≤]\s?\d[\d.,]*|[−+-]?\d[\d.,]*\s?(?:m|%|meses|mL|días|años|semanas|puntos)(?![\wÀ-ſ])/g;
function fix(td){if(td.dataset.nw)return;td.dataset.nw=1;const w=document.createTreeWalker(td,NodeFilter.SHOW_TEXT);const ns=[];while(w.nextNode())ns.push(w.currentNode);
 ns.forEach(n=>{const t=n.nodeValue;RX.lastIndex=0;if(!RX.test(t))return;RX.lastIndex=0;const f=document.createDocumentFragment();let i=0,m;
  while((m=RX.exec(t))){if(m.index>i)f.appendChild(document.createTextNode(t.slice(i,m.index)));const s=document.createElement('span');s.className='nw';s.textContent=m[0];f.appendChild(s);i=m.index+m[0].length;}
  if(i<t.length)f.appendChild(document.createTextNode(t.slice(i)));n.parentNode.replaceChild(f,n);});}
function run(){document.querySelectorAll('td.num').forEach(fix);}
document.addEventListener('DOMContentLoaded',run);window.addEventListener('load',()=>{run();setTimeout(run,800);});
new MutationObserver(()=>run()).observe(document.documentElement,{childList:true,subtree:true});
})();</script>
'''


MARCA12 = '/* VERA favorece */'
# v1.2: bajo el diagrama de bosque de la comparación indirecta, hacia qué lado se favorece a cada
# tratamiento (A frente a C). El lado sale de la leyenda del propio informe: con HR la izquierda
# favorece al primer tratamiento; con RR o diferencia de medias, la derecha.
JS12 = r'''/* VERA favorece */{const x0=+((g.match(/class="ax" x1="([\d.\-]+)"/)||[0,360])[1]),R=__DER__;
      const izq=R?nC:nA, der=R?nA:nC, mu=css('--muted'), fg=css('--fg');
      const fit=(n,av)=>n.length*6.6>av?` textLength="${av}" lengthAdjust="spacingAndGlyphs"`:'';
      g+=`<line x1="${x0}" y1="130" x2="${x0}" y2="160" stroke="${css('--line')}"/>`;
      g+=`<text x="${x0-10}" y="142" font-size="11.5" text-anchor="end" fill="${mu}">← Favorece a</text>`;
      g+=`<text x="${x0-10}" y="157" font-size="12" font-weight="600" text-anchor="end" fill="${fg}"${fit(izq,x0-20)}>${esc(izq)}</text>`;
      g+=`<text x="${x0+10}" y="142" font-size="11.5" fill="${mu}">Favorece a →</text>`;
      g+=`<text x="${x0+10}" y="157" font-size="12" font-weight="600" fill="${fg}"${fit(der,590-x0)}>${esc(der)}</text>`;}
    '''


MARCA13 = '/* VERA delta */'
# v1.3: en oncología y hematología (comparaciones con HR), delta de relevancia clínica de ESMO-MCBS
# (HR 0,65) y su inverso (1,54) como líneas discontinuas: margen de equivalencia (guía ATE).
JS13 = r'''/* VERA delta */{const D=__D__, mu=css('--muted');
      [[D,'Δ '+fmt(D,2)],[1/D,'1/Δ '+fmt(1/D,2)]].forEach(([v,lab])=>{const x=lx(v);
        g+=`<line x1="${x}" y1="12" x2="${x}" y2="104" stroke="${mu}" stroke-width="1" stroke-dasharray="4 3"/>`;
        g+=`<text x="${x}" y="9" font-size="10" text-anchor="middle" fill="${mu}">${lab}</text>`;});}
    '''
NOTA13 = ('<p class="note" id="bu-leg"></p>\n    <p class="note" id="bu-delta">Líneas discontinuas: delta de relevancia clínica '
          '(HR __DT__, umbral de ESMO-MCBS __FORM__) y su inverso (__INV__). Si el IC 95 % del resultado indirecto queda entero entre '
          'ambas, las dos opciones pueden considerarse equivalentes en eficacia (guía ATE); si cruza una de ellas, '
          'no puede descartarse una diferencia clínicamente relevante.</p>')


# Delta por informe: HR 0,65 por defecto; la adyuvancia (formulario 1) se decide aparte.
DELTA = {}


def aplicar(t, delta=0.65, form=''):
    cambiado = False
    if MARCA not in t:
        t = aplicar_v1(t)
        cambiado = True
    if MARCA11 not in t:
        # v1.1: tablas sin desplazamiento horizontal en ordenador y tableta
        fin = t.index('</style>', t.index(MARCA))
        t = t[:fin] + CSS11 + t[fin:]
        assert t.count('<div class="wrap">') == 1
        t = t.replace('<div class="wrap">', JS11 + '<div class="wrap">')
        cambiado = True
    if MARCA12 not in t and "$('chart-forest').innerHTML=g" in t:
        der = 'a la derecha favorece al primer tratamiento' in t
        assert der or 'a la izquierda favorece al primer tratamiento' in t
        assert t.count("$('chart-forest').innerHTML=g") == 1
        t = t.replace("$('chart-forest').innerHTML=g", JS12.replace('__DER__', 'true' if der else 'false') + "$('chart-forest').innerHTML=g")
        t = t.replace('<svg id="chart-forest" viewBox="0 0 600 130"', '<svg id="chart-forest" viewBox="0 0 600 166"')
        cambiado = True
    if MARCA13 not in t and 'R=false;' in t:
        assert t.count('/* VERA favorece */') == 1 and t.count('<p class="note" id="bu-leg"></p>') == 1
        t = t.replace('/* VERA favorece */', JS13.replace('__D__', repr(delta)) + '/* VERA favorece */')
        es = lambda x: f'{x:.2f}'.replace('.', ',')
        t = t.replace('<p class="note" id="bu-leg"></p>',
                      NOTA13.replace('__DT__', es(delta)).replace('__INV__', es(1 / delta)).replace('__FORM__', form).replace('  ', ' ').replace(' )', ')'))
        cambiado = True
    return t, cambiado


def aplicar_v1(t):
    # 1. CSS al final de la hoja de estilos principal (la que define .wrap)
    k = t.index('.wrap{')
    fin = t.index('</style>', k)
    t = t[:fin] + CSS + t[fin:]
    # 2. Barra superior antes de la cabecera
    assert t.count('<header class="top">') == 1
    t = t.replace('<header class="top">', NAV + '<header class="top">')
    # 3. Sin «prototipo» ni «VERA ·» repetido (ya está en la barra)
    t = re.sub(r'\s*·\s*prototipo v[\d.]+', '', t, flags=re.I)
    t = t.replace('<div class="eyebrow">VERA · Informe de evaluación', '<div class="eyebrow">Informe de evaluación')
    # 4. Leyenda de lectura tras el sello
    sello = '<div class="seal read-only" id="seal"></div>'
    assert t.count(sello) == 1
    t = t.replace(sello, sello + LEYENDA)
    return t


if __name__ == '__main__':
    args = sys.argv[1:]
    delta, form = 0.65, ''
    if args and args[0].startswith('--delta='):
        delta = float(args.pop(0).split('=')[1].replace(',', '.'))
    if args and args[0].startswith('--form='):
        form = args.pop(0).split('=', 1)[1]
    for p in args:
        t = open(p, encoding='utf-8').read()
        t, cambiado = aplicar(t, delta, form)
        if cambiado:
            open(p, 'w', encoding='utf-8').write(t)
        print(('aplicado ' if cambiado else 'ya estaba ') + p)
