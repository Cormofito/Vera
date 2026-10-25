#!/usr/bin/env python3
"""VERA · avisa a quien propuso un fármaco de que su informe ya está publicado en la web.

Uso: VERA_URL=... VERA_CLAVE=... python3 vera_avisar.py correo "Fármaco" "Indicación" url_del_informe [fecha_propuesta] [fecha_publicacion]

La lista de informes publicados está en https://vera-fharma.github.io/Vera/publicados.json
(la genera build_site.py; desde aquí se lee en
https://raw.githubusercontent.com/Vera-fharma/Vera/main/publicados.json). Envía a través del mismo script de Google Apps que los informes.
"""
import datetime, json, os, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vera_correo import plantilla


def main():
    para, farmaco, indicacion, url = sys.argv[1:5]
    propuesta = sys.argv[5] if len(sys.argv) > 5 else ''
    fecha = sys.argv[6] if len(sys.argv) > 6 else \
        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).strftime('%d/%m/%Y')
    asunto, cuerpo, texto = plantilla('publicado', farmaco, indicacion, fecha, url=url, propuesta=propuesta)
    if os.environ.get('VERA_SOLO_VISTA'):
        open('aviso_publicado.html', 'w', encoding='utf-8').write(cuerpo)
        print(asunto); return
    body = {'clave': os.environ['VERA_CLAVE'], 'para': para, 'asunto': asunto, 'html': cuerpo, 'texto': texto}
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(body, f); tmp = f.name
    r = subprocess.run(['curl', '-sSL', '-m', '60', '-H', 'Content-Type: application/json', '--data-binary', '@' + tmp,
                        os.environ['VERA_URL']], capture_output=True, text=True)
    os.unlink(tmp)
    print(r.stdout or r.stderr)
    res = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {'ok': False}
    sys.exit(0 if res.get('ok') else 1)


if __name__ == '__main__':
    main()
