#!/usr/bin/env python3
"""VERA · regenera la web pública (GitHub Pages) a partir de los artefactos de claude.ai.

Uso:
    python3 herramientas/build_site.py FUENTES [--salida .] [--fecha 25/10/2026] [--comprobar]

FUENTES es una carpeta con el código de los artefactos y sus datos:

    FUENTES/portal.html                 código del portal (Artifact read, path index.html)
    FUENTES/portal.docs.json            datos del portal: {"control/linea_base": {...}}
    FUENTES/informes/<slug>.html        código de cada informe
    FUENTES/informes/<slug>.docs.json   (opcional) {"informe/verificacion": {...}, "informe/conclusion": {...}}

Qué hace:
  - index.html = cabecera de la web (PWA, solicitar.js, sustituto de solo lectura de
    window.claude con los datos incrustados) + cuerpo del portal desde <title>VERA</title>,
    con los enlaces a artefactos cambiados por informes/<slug>.html y los textos de subida
    y solicitud adaptados a la web.
  - informes/<slug>.html = cabecera de informe + código del artefacto desde <meta charset=utf8>.
  - No toca el resto de archivos (sw.js, pwa.js, solicitar.*, iconos, manifest...).

Con --comprobar no escribe nada: compara con lo que hay en --salida y muestra las diferencias.
Si aparece un enlace a un artefacto que no está en MAPA, se detiene: añade el informe a MAPA.
"""
import argparse
import datetime as dt
import difflib
import json
import pathlib
import re
import sys

PORTAL_ID = '82F9DBpQWW9Nio5RFFQ2a1'
# id del artefacto en claude.ai -> nombre del archivo en informes/
MAPA = {
    'UWL6WzM6wATJJDPnsEQZRd': 'sacituzumab-pembrolizumab',
    'BYp6orvjVGbFYyvwC73N1Y': 'ribociclib-adyuvante',
    'TwbRRU5c4L4FM52ZmJ2GoH': 'elacestrant',
    'UT4JmhENPRdJ8kbggywFD3': 'trastuzumab-deruxtecan-her2-low',
    'AzgDx2ZTsEhigAxh16Uf2u': 'enfortumab-vedotina-pembrolizumab',
    'QPudhkxjSJuKCtFwtMDohF': 'ribociclib-metastasico',
    'M6m9FwG8acvfR8b5AANnC3': 'guselkumab-colitis-ulcerosa',
    'L1ApC3ZWR5ukYg6EmsyoDV': 'guselkumab-crohn',
    'MZYWE6nxp4CB9qynRiqPhk': 'belantamab-mafodotina',
    'XmvioBPJv3sJ7zR1fZEsZ3': 'isatuximab-vrd',
    '7VZ1gZy3wnoXwgFHdpWeGu': 'datopotamab-deruxtecan',
    '4xXNJPJZnNSmjgt8MYBh22': 'nerandomilast',
}
SOLICITAR_ABS = 'https://vera-fharma.github.io/Vera/solicitar.html'
ART = re.compile(r'https://claude\.ai/(?:code/)?artifact/([A-Za-z0-9-]+)')

# Sustituto de solo lectura de window.claude (los datos van incrustados en DOCS).
SUSTITUTO = '''<script>/* VERA web: entorno de solo lectura (exportado el {fecha}) */
(function(){{
  const DOCS={docs};
  const snap=(id,data)=>({{id,exists:data!=null,data:()=>data}});
  const doc=p=>({{onSnapshot(cb){{setTimeout(()=>cb(snap(p.split('/').pop(),DOCS[p]??null)),0);return()=>{{}};}},
    get:async()=>snap(p.split('/').pop(),DOCS[p]??null),
    set:async()=>{{throw new Error('Solo lectura');}},update:async()=>{{throw new Error('Solo lectura');}}}});
  const col=c=>({{onSnapshot(cb){{const ds=Object.keys(DOCS).filter(k=>k.startsWith(c+'/')&&k.split('/').length===c.split('/').length+1).map(k=>snap(k.split('/').pop(),DOCS[k]));
    setTimeout(()=>cb({{docs:ds,size:ds.length,empty:!ds.length}}),0);return()=>{{}};}}}});
  const caps={{
    db:{{doc,collection:col}},
    user:{{isOwner:async()=>false,id:async()=>null}},
    downloads:{{save:async({{filename,data}})=>{{const u=URL.createObjectURL(data);const a=document.createElement('a');a.href=u;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);}}}}
  }};
  window.claude={{use:async n=>{{if(caps[n])return caps[n];throw new Error('No disponible en la web');}}}};
}})();</script>'''

CABECERA_PORTAL = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{{box-sizing:border-box}}body{{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}}img{{max-width:100%}}[hidden]:not([hidden=until-found i]){{display:none!important}}</style>
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#1f4e79">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="VERA">
<script src="pwa.js" data-banner defer></script>
<style>.nav-menu,.nav-toggle{{display:none!important}}</style>
<script src="solicitar.js" defer></script>
{sustituto}
</head>
<body>
'''

CABECERA_INFORME = '''<!doctype html><html><head>
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="icon" href="../favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="manifest" href="../manifest.webmanifest">
<meta name="theme-color" content="#1f4e79">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="VERA">
<script src="../pwa.js" defer></script>
{sustituto}'''
PIE_INFORME = ('<p style="max-width:960px;margin:24px auto;padding:0 16px;font:12px/1.5 system-ui,sans-serif;color:#777">'
               'Versión web de solo lectura de VERA, exportada el {fecha}. <a href="../index.html">Volver a VERA</a></p>\n')

# Textos del portal que en la web no tienen sentido (no hay subida ni cuenta de Claude).
LOCKS = [
    ("lock('La subida de documentos no está disponible aquí','Abre VERA desde Claude para aportar un EPAR.')",
     "lock('La subida de documentos llegará con la versión completa de la web','Mientras tanto, envía el EPAR a la responsable de VERA.')"),
    ("lock('Inicia sesión para aportar documentos','Necesitas una cuenta de Claude con acceso a VERA.')",
     "lock('La subida de documentos llegará con la versión completa de la web','Mientras tanto, envía el EPAR a la responsable de VERA.')"),
]
# solicitar.js añade su propio enlace en las búsquedas sin resultados: se quita el del portal.
FRASE_VACIO = re.compile(r' Si el fármaco no está, <a [^>]*>(?:solicita un informe|aporta su EPAR)</a>[^<]*?\.(?=</span>)')


def docs_json(ruta):
    if not ruta.exists():
        return '{}'
    return json.dumps(json.loads(ruta.read_text(encoding='utf-8')), ensure_ascii=False)


def enlaces(texto, desde_informe):
    def sub(m):
        i = m.group(1)
        if i == PORTAL_ID:
            return '../index.html' if desde_informe else 'index.html'
        if i in MAPA:
            return (MAPA[i] if desde_informe else 'informes/' + MAPA[i]) + '.html'
        sys.exit(f'ERROR: enlace a un artefacto que no está en MAPA: {m.group(0)}\n'
                 '       Añádelo a MAPA en build_site.py con su nombre de archivo.')
    return ART.sub(sub, texto)


def portal(fuentes, fecha):
    src = (fuentes / 'portal.html').read_text(encoding='utf-8')
    if '<title>VERA</title>' not in src:
        sys.exit('ERROR: portal.html no contiene <title>VERA</title>')
    cuerpo = src[src.index('<title>VERA</title>'):]
    cuerpo = enlaces(cuerpo, False)
    cuerpo = cuerpo.replace('href="${esc(d.url)}" target="_blank" rel="noopener">Abrir informe completo',
                            'href="${esc(d.url)}">Abrir informe completo')
    cuerpo = FRASE_VACIO.sub('', cuerpo)
    cuerpo = cuerpo.replace(f'href="{SOLICITAR_ABS}" target="_blank" rel="noopener"', 'href="solicitar.html"')
    cuerpo = cuerpo.replace(SOLICITAR_ABS, 'solicitar.html')
    for a, b in LOCKS:
        cuerpo = cuerpo.replace(a, b)
    cuerpo = cuerpo.rstrip()
    if cuerpo.endswith('</body></html>'):
        cuerpo = cuerpo[:-len('</body></html>')] + '</body>\n</html>'
    sust = SUSTITUTO.format(fecha=fecha, docs=docs_json(fuentes / 'portal.docs.json'))
    return CABECERA_PORTAL.format(sustituto=sust) + cuerpo + '\n'


def informe(ruta, fecha):
    src = ruta.read_text(encoding='utf-8')
    if '<meta charset=utf8>' not in src:
        sys.exit(f'ERROR: {ruta.name} no contiene <meta charset=utf8>')
    cuerpo = enlaces(src[src.index('<meta charset=utf8>'):], True)
    sust = SUSTITUTO.format(fecha=fecha, docs=docs_json(ruta.with_suffix('.docs.json')))
    if 'Volver a VERA</a></p>' not in cuerpo and '</body>' in cuerpo:
        k = cuerpo.rindex('</body>')
        cuerpo = cuerpo[:k] + PIE_INFORME.format(fecha=fecha) + cuerpo[k:]
    return CABECERA_INFORME.format(sustituto=sust) + cuerpo


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('fuentes', type=pathlib.Path)
    ap.add_argument('--salida', type=pathlib.Path, default=pathlib.Path('.'))
    ap.add_argument('--fecha', default=dt.date.today().strftime('%d/%m/%Y'))
    ap.add_argument('--comprobar', action='store_true')
    a = ap.parse_args()

    salidas = {'index.html': portal(a.fuentes, a.fecha)}
    for r in sorted((a.fuentes / 'informes').glob('*.html')):
        if r.stem not in MAPA.values():
            print(f'AVISO: {r.name} no está en MAPA (el portal no enlazará a él)')
        salidas[f'informes/{r.name}'] = informe(r, a.fecha)
    faltan = set(MAPA.values()) - {pathlib.Path(k).stem for k in salidas if k.startswith('informes/')}
    if faltan:
        print('AVISO: faltan fuentes de: ' + ', '.join(sorted(faltan)) + ' (se conserva lo publicado)')

    cambios = 0
    for nombre, txt in salidas.items():
        dest = a.salida / nombre
        viejo = dest.read_text(encoding='utf-8') if dest.exists() else ''
        if viejo == txt:
            continue
        cambios += 1
        if a.comprobar:
            d = list(difflib.unified_diff(viejo.splitlines(), txt.splitlines(), nombre, nombre + ' (nuevo)', n=0, lineterm=''))
            print(f'== {nombre}: {len(d)} líneas de diferencia')
            for l in d[:40]:
                print('   ' + (l if len(l) < 220 else l[:220] + '…'))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(txt, encoding='utf-8')
            print(f'escrito {nombre}')
    print(f'{len(salidas)} páginas, {cambios} con cambios' + (' (sin escribir)' if a.comprobar else ''))


if __name__ == '__main__':
    main()
