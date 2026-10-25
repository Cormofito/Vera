#!/usr/bin/env python3
"""VERA · envía un informe automático por correo a través del script de Google Apps.

Uso: VERA_URL=... VERA_CLAVE=... python3 vera_enviar.py correo "Fármaco" "Indicación" informe.pdf informe.docx [cc]
"""
import base64, html, json, os, subprocess, sys, tempfile

para, farmaco, indicacion, pdf, docx = sys.argv[1:6]
cc = sys.argv[6] if len(sys.argv) > 6 else ''
url, clave = os.environ['VERA_URL'], os.environ['VERA_CLAVE']

F, I = html.escape(farmaco), html.escape(indicacion)
cuerpo = f"""<div style="font-family:Calibri,Arial,sans-serif;font-size:14px;color:#1b2430;max-width:620px">
<p style="font-size:22px;font-weight:bold;color:#1f4e79;margin:0 0 4px">VERA</p>
<p style="color:#5b6675;margin:0 0 18px">Valoración de la Evidencia y Relevancia Asistencial</p>
<p>Hola:</p>
<p>Te enviamos el informe de evaluación que solicitaste de <b>{F}</b> ({I}), en PDF y en Word.</p>
<div style="border:1.5px solid #a3302a;background:#f8e3e1;border-radius:6px;padding:10px 14px;margin:16px 0">
<b style="color:#a3302a">Informe automático: no revisado por VERA</b><br>
Se ha generado automáticamente a partir de los documentos que aportaste y de fuentes públicas.
Cada cifra indica su fuente y su página para que puedas comprobarla. Verificar los datos antes de usar el informe
es responsabilidad tuya; no sustituye el criterio de la Comisión de Farmacia y Terapéutica.</div>
<p>El Word se puede editar: por ejemplo, para completar los precios de tu centro en el área económica.</p>
<p>Los documentos que adjuntaste y los datos de la solicitud se eliminan tras este envío.</p>
<p style="color:#5b6675;font-size:12px;margin-top:24px">VERA · <a href="https://vera-fharma.github.io/Vera/">vera-fharma.github.io/Vera</a> · Este correo se envía automáticamente; si tienes dudas, puedes responder a este mensaje.</p>
</div>"""
texto = (f"VERA · Informe de evaluación de {farmaco} ({indicacion}), en PDF y Word.\n\n"
         "Informe automático: no revisado por VERA. Se ha generado automáticamente a partir de los documentos "
         "que aportaste y de fuentes públicas. Verificar los datos antes de usarlo es responsabilidad tuya.\n\n"
         "Los documentos y los datos de la solicitud se eliminan tras este envío.\n\nVERA · https://vera-fharma.github.io/Vera/")

adj = []
for path, tipo in ((pdf, 'application/pdf'),
                   (docx, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')):
    adj.append({'nombre': os.path.basename(path), 'tipo': tipo,
                'base64': base64.b64encode(open(path, 'rb').read()).decode()})

body = {'clave': clave, 'para': para, 'cc': cc, 'asunto': f'VERA · Informe de {farmaco} ({indicacion})',
        'html': cuerpo, 'texto': texto, 'adjuntos': adj}
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
    json.dump(body, f); tmp = f.name
r = subprocess.run(['curl', '-sSL', '-m', '120', '-H', 'Content-Type: application/json', '--data-binary', '@' + tmp, url],
                   capture_output=True, text=True)
os.unlink(tmp)
print(r.stdout or r.stderr)
res = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {'ok': False}
sys.exit(0 if res.get('ok') else 1)
