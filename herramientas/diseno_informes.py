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


def aplicar(t):
    if MARCA in t:
        return t, False
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
    return t, True


if __name__ == '__main__':
    for p in sys.argv[1:]:
        t = open(p, encoding='utf-8').read()
        t, cambiado = aplicar(t)
        if cambiado:
            open(p, 'w', encoding='utf-8').write(t)
        print(('aplicado ' if cambiado else 'ya estaba ') + p)
