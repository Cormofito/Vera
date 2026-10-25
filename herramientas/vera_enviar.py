#!/usr/bin/env python3
"""VERA · envía un informe automático por correo a través del script de Google Apps.

Uso: VERA_URL=... VERA_CLAVE=... python3 vera_enviar.py correo "Fármaco" "Indicación" informe.pdf informe.docx [cc]
"""
import base64, html, json, os, subprocess, sys, tempfile

para, farmaco, indicacion, pdf, docx = sys.argv[1:6]
cc = sys.argv[6] if len(sys.argv) > 6 else ''
url, clave = os.environ['VERA_URL'], os.environ['VERA_CLAVE']

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vera_correo import plantilla
import datetime
fecha = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).strftime('%d/%m/%Y')
asunto, cuerpo, texto = plantilla('informe', farmaco, indicacion, fecha)

adj = []
for path, tipo in ((pdf, 'application/pdf'),
                   (docx, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')):
    adj.append({'nombre': os.path.basename(path), 'tipo': tipo,
                'base64': base64.b64encode(open(path, 'rb').read()).decode()})

body = {'clave': clave, 'para': para, 'cc': cc, 'asunto': asunto,
        'html': cuerpo, 'texto': texto, 'adjuntos': adj}
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
    json.dump(body, f); tmp = f.name
r = subprocess.run(['curl', '-sSL', '-m', '120', '-H', 'Content-Type: application/json', '--data-binary', '@' + tmp, url],
                   capture_output=True, text=True)
os.unlink(tmp)
print(r.stdout or r.stderr)
res = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {'ok': False}
sys.exit(0 if res.get('ok') else 1)
