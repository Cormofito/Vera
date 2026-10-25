"""VERA · plantilla HTML de los correos (acuse de recibo e informe enviado).

Diseño pensado para clientes de correo: tablas, estilos en línea, anchura 600 px,
imágenes alojadas en la web de VERA. El script de Google Apps tiene una copia en JS
(función plantilla) para el acuse; si cambias el diseño, cambia los dos.
"""
import html as _h

WEB = 'https://vera-fharma.github.io/Vera/'
LOGO = WEB + 'icon-192.png'
AZUL, AZUL_OSC, TINTA, GRIS, LINEA, FONDO, SUAVE = '#1f4e79', '#163a5c', '#1b2430', '#5b6675', '#d9dde3', '#eef1f4', '#e3ecf5'
ROJO, ROJO_BG, VERDE = '#a3302a', '#fbeceb', '#1d6b45'
SERIF = "Georgia,'Times New Roman',serif"
SANS = "'Segoe UI',Calibri,Arial,Helvetica,sans-serif"


def _e(s):
    return _h.escape(str(s))


def _pasos(hechos):
    nombres = ['Recibida', 'En preparación', 'Enviada']
    celdas = []
    for i, n in enumerate(nombres):
        ok = i < hechos
        actual = i == hechos
        circ_bg = AZUL if ok else ('#ffffff' if not actual else SUAVE)
        circ_bd = AZUL if (ok or actual) else LINEA
        circ_tx = '#ffffff' if ok else (AZUL if actual else '#9aa5b4')
        simbolo = '&#10003;' if ok else str(i + 1)
        color_txt = TINTA if (ok or actual) else '#9aa5b4'
        celdas.append(
            f'<td align="center" valign="top" style="width:33%;padding:0 4px">'
            f'<div style="width:30px;height:30px;line-height:30px;border-radius:50%;background:{circ_bg};border:2px solid {circ_bd};'
            f'color:{circ_tx};font:bold 14px {SANS};text-align:center;margin:0 auto">{simbolo}</div>'
            f'<div style="font:{"bold" if (ok or actual) else "normal"} 12px {SANS};color:{color_txt};margin-top:6px">{n}</div></td>')
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 4px">'
            f'<tr>{"".join(celdas)}</tr></table>')


def _filas(datos):
    out = []
    for i, (k, v) in enumerate(datos):
        borde = '' if i == len(datos) - 1 else f'border-bottom:1px solid #d3deeb;'
        out.append(f'<tr><td style="padding:10px 0;{borde}font:12px {SANS};color:{GRIS};text-transform:uppercase;letter-spacing:.06em;width:38%" valign="top">{_e(k)}</td>'
                   f'<td style="padding:10px 0;{borde}font:15px {SANS};color:{TINTA}" valign="top">{v}</td></tr>')
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:{SUAVE};border-radius:10px;padding:6px 18px">{"".join(out)}</table>')


def plantilla(tipo, farmaco, indicacion='', fecha='', plazo='', solo_proponer=False):
    """tipo: 'acuse' o 'informe'. Devuelve (asunto, html, texto)."""
    F, I = _e(farmaco), _e(indicacion)
    if tipo == 'acuse':
        if solo_proponer:
            eyebrow, titulo = 'Propuesta recibida', 'Gracias por tu propuesta'
            lead = (f'Hemos recibido tu propuesta de <b>{F}</b>. El equipo de VERA la revisará y, si procede, '
                    'publicará el informe en la web, ya verificado.')
            datos = [('Fármaco', F), ('Indicación', I or '—'), ('Recibida', _e(fecha))]
            pasos = ''
        else:
            eyebrow, titulo = 'Solicitud recibida', 'Estamos preparando tu informe'
            lead = (f'Hemos recibido tu solicitud de <b>{F}</b>. Te enviaremos el informe a este correo, '
                    'en PDF y en Word, en cuanto esté listo.')
            datos = [('Fármaco', F), ('Indicación', I or '—'), ('Recibida', _e(fecha)), ('Plazo estimado', f'<b>{_e(plazo)}</b>')]
            pasos = _pasos(1)
        asunto = f'VERA · Hemos recibido tu {"propuesta" if solo_proponer else "solicitud"} de {farmaco}'
        boton = ('Ver cómo funciona', WEB + 'solicitar.html')
        nota = ('Te avisaremos cuando esté publicado.' if solo_proponer else
                'Si hay muchas solicitudes, puede tardar algo más. No hace falta que hagas nada: te llegará solo.')
    else:
        eyebrow, titulo = 'Tu informe está listo', f'{F}'
        lead = (f'Aquí tienes el informe de evaluación de <b>{F}</b>{(" en " + I) if I else ""}. '
                'Lo encontrarás adjunto en dos formatos.')
        datos = [('Fármaco', F), ('Indicación', I or '—'), ('Adjuntos', 'Informe en <b>PDF</b> y en <b>Word</b> editable'), ('Enviado', _e(fecha))]
        pasos = _pasos(3)
        asunto = f'VERA · Tu informe de {farmaco}' + (f' ({indicacion})' if indicacion else '')
        boton = ('Ir a VERA', WEB)
        nota = 'El Word se puede editar: por ejemplo, para completar los precios de tu centro en el área económica.'

    aviso = ('<b style="color:%s">Informe automático, no revisado por VERA.</b> Se genera automáticamente a partir de los '
             'documentos que aportaste y de fuentes públicas. Cada cifra indica su fuente y su página: verificar los datos '
             'antes de usar el informe es responsabilidad tuya. No sustituye el criterio de la Comisión de Farmacia y Terapéutica.') % ROJO
    if tipo == 'acuse' and solo_proponer:
        aviso = ''

    pie = ('Recibes este correo porque propusiste un fármaco a VERA. Tu correo solo se usa para avisarte sobre tu propuesta.'
           if (tipo == 'acuse' and solo_proponer) else
           'Recibes este correo porque solicitaste un informe en VERA. Tu correo solo se usa para enviarte el informe; '
           'los documentos y los datos de la solicitud se eliminan tras el envío.')
    html = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>{_e(asunto)}</title></head>
<body style="margin:0;padding:0;background:{FONDO}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{_e(titulo if tipo == 'acuse' else 'Tu informe de ' + farmaco + ' está listo, en PDF y Word.')}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{FONDO}"><tr><td align="center" style="padding:28px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid {LINEA}">
  <tr><td style="background:{AZUL};background-image:linear-gradient(135deg,{AZUL} 0%,{AZUL_OSC} 100%);padding:26px 32px">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td valign="middle" style="padding-right:14px"><img src="{LOGO}" width="48" height="48" alt="VERA" style="display:block;border:0;border-radius:50%;background:#ffffff"></td>
      <td valign="middle"><div style="font:bold 26px {SERIF};letter-spacing:.18em;color:#ffffff;line-height:1">VERA</div>
        <div style="font:12px {SANS};color:#c9d9ea;margin-top:5px;letter-spacing:.02em">Valoración de la Evidencia y Relevancia Asistencial</div></td>
    </tr></table></td></tr>
  <tr><td style="padding:32px 32px 8px">
    <div style="font:bold 12px {SANS};color:{AZUL};text-transform:uppercase;letter-spacing:.12em">{_e(eyebrow)}</div>
    <div style="font:bold 28px {SERIF};color:{TINTA};line-height:1.2;margin:8px 0 14px">{titulo}</div>
    <div style="font:16px/1.6 {SANS};color:#3a4552">{lead}</div>
  </td></tr>
  {f'<tr><td style="padding:18px 32px 0">{pasos}</td></tr>' if pasos else ''}
  <tr><td style="padding:20px 32px 0">{_filas(datos)}</td></tr>
  {f'<tr><td style="padding:20px 32px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="background:{ROJO_BG};border-left:4px solid {ROJO};border-radius:0 8px 8px 0;padding:14px 16px;font:14px/1.55 {SANS};color:{TINTA}">{aviso}</td></tr></table></td></tr>' if aviso else ''}
  <tr><td style="padding:18px 32px 0;font:14px/1.6 {SANS};color:{GRIS}">{_e(nota)}</td></tr>
  <tr><td align="left" style="padding:24px 32px 30px">
    <a href="{boton[1]}" style="display:inline-block;background:{AZUL};color:#ffffff;text-decoration:none;font:bold 15px {SANS};padding:13px 26px;border-radius:9px">{_e(boton[0])} &rarr;</a>
  </td></tr>
  <tr><td style="padding:0 32px"><div style="border-top:1px solid {LINEA}"></div></td></tr>
  <tr><td style="padding:22px 32px 26px">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td valign="top" style="padding-right:12px"><img src="{LOGO}" width="38" height="38" alt="" style="display:block;border:0;border-radius:50%"></td>
      <td valign="top"><div style="font:bold 15px {SANS};color:{TINTA}">Equipo VERA</div>
        <div style="font:13px {SANS};color:{GRIS};margin-top:2px">Informes de evaluación de medicamentos</div>
        <div style="font:13px {SANS};margin-top:4px"><a href="{WEB}" style="color:{AZUL};text-decoration:none">vera-fharma.github.io/Vera</a></div></td>
    </tr></table></td></tr>
</table>
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px"><tr><td style="padding:16px 24px;font:12px/1.5 {SANS};color:#8a94a3;text-align:center">
  {pie}<br>
  Este mensaje se envía automáticamente. Si tienes dudas, puedes responder a este correo.
</td></tr></table>
</td></tr></table></body></html>'''

    if tipo == 'acuse':
        texto = (f'Hemos recibido tu solicitud de {farmaco}. ' +
                 ('El equipo de VERA la revisará.' if solo_proponer else f'Te enviaremos el informe {plazo}.') +
                 '\n\nVERA · ' + WEB)
    else:
        texto = (f'Tu informe de {farmaco} ({indicacion}) está listo, en PDF y Word.\n\n'
                 'Informe automático, no revisado por VERA: verificar los datos es responsabilidad tuya.\n\nVERA · ' + WEB)
    return asunto, html, texto
