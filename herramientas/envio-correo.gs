/**
 * VERA · envío de informes por correo (Google Apps Script, cuenta vera.informes@gmail.com)
 *
 * Recibe por HTTPS (POST, JSON) el informe generado por la tarea diaria y lo envía por Gmail
 * desde la cuenta de VERA, con el PDF y el Word adjuntos.
 *
 * También envía al momento un acuse de recibo a quien rellena el formulario (función acuse,
 * activada con instalarAcuse()).
 *
 * Cuerpo esperado:
 * { "clave": "...", "para": "usuario@correo", "cc": "", "asunto": "...",
 *   "html": "...", "texto": "...",
 *   "adjuntos": [{ "nombre": "x.pdf", "tipo": "application/pdf", "base64": "..." }] }
 */
const CLAVE = 'PEGA_AQUI_LA_CLAVE';

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.clave !== CLAVE) return salida({ ok: false, error: 'clave incorrecta' });
    if (!d.para || !d.asunto) return salida({ ok: false, error: 'faltan destinatario o asunto' });
    const adjuntos = (d.adjuntos || []).map(a =>
      Utilities.newBlob(Utilities.base64Decode(a.base64), a.tipo, a.nombre));
    GmailApp.sendEmail(d.para, d.asunto, d.texto || '', {
      htmlBody: d.html || undefined,
      attachments: adjuntos,
      cc: d.cc || '',
      name: 'VERA'
    });
    return salida({ ok: true, enviados: adjuntos.length });
  } catch (err) {
    return salida({ ok: false, error: String(err) });
  }
}

function doGet() {
  return salida({ ok: true, servicio: 'VERA envío de informes' });
}

function salida(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Ejecútala una vez desde el editor para dar permiso a Gmail. */
function autorizar() {
  GmailApp.sendEmail(Session.getActiveUser().getEmail(), 'VERA · script de envío autorizado',
    'El script de envío de informes de VERA ya tiene permiso para usar Gmail.');
}

/* ---------- Acuse de recibo inmediato ---------- */
const FORMULARIO = '1u48D_iTvMoDx_waHRLCeIHruddtSCIMuy9-jBBizGC8';
const HOJA = '11qcGZjg3hJarLmJTBZHKYJGA7yxiJ-IS00h-aBhR4Hc';
const POR_HORA = 3;          // informes que procesa cada ejecución de la tarea
const HORA_INICIO = 7, HORA_FIN = 23;

/** Ejecútala una vez desde el editor: activa el acuse al enviar el formulario. */
function instalarAcuse() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'acuse')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('acuse').forForm(FORMULARIO).onFormSubmit().create();
}

function acuse(e) {
  const r = e.response;
  const correo = r.getRespondentEmail();
  if (!correo) return;
  let farmaco = '', quiere = '', indicacion = '';
  r.getItemResponses().forEach(ir => {
    const t = ir.getItem().getTitle().toLowerCase();
    if (t.indexOf('principio activo') >= 0) farmaco = String(ir.getResponse());
    if (t.indexOf('qué quieres hacer') >= 0) quiere = String(ir.getResponse());
    if (t.indexOf('indicación') >= 0) indicacion = String(ir.getResponse());
  });
  const soloProponer = /proponer/i.test(quiere) && !/informe autom|las dos/i.test(quiere);

  // Posición en la cola: solicitudes aún sin enviar (incluida esta).
  let cola = 1;
  try {
    const sh = SpreadsheetApp.openById(HOJA).getSheets()[0];
    const datos = sh.getDataRange().getValues();
    const col = datos[0].map(String).findIndex(h => h.trim() === 'Estado');
    if (col >= 0) cola = Math.max(1, datos.slice(1).filter(f => {
      const est = String(f[col]).trim();
      return est === '' || est === 'en proceso';
    }).length);
  } catch (err) {}

  const ahora = new Date();
  const h = Number(Utilities.formatDate(ahora, 'Europe/Madrid', 'H'));
  const horas = Math.ceil(cola / POR_HORA);
  let plazo;
  if (h >= HORA_FIN || h < HORA_INICIO) plazo = 'a partir de las 7:00 de la mañana';
  else if (horas <= 1) plazo = 'en la próxima hora aproximadamente';
  else plazo = 'en unas ' + horas + ' horas, porque hay ' + cola + ' solicitudes en cola';

  const fecha = Utilities.formatDate(ahora, 'Europe/Madrid', "dd/MM/yyyy, HH:mm");
  const m = plantillaAcuse(farmaco || 'tu fármaco', indicacion, fecha, plazo, soloProponer);
  const asunto = m.asunto, texto = m.texto, html = m.html;
  GmailApp.sendEmail(correo, asunto, texto, { htmlBody: html, name: 'VERA' });
}

/* ---------- Plantilla del correo de acuse (misma estética que vera_correo.py) ---------- */
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

function plantillaAcuse(farmaco, indicacion, fecha, plazo, soloProponer) {
  const WEB = 'https://vera-fharma.github.io/Vera/', LOGO = WEB + 'icon-192.png';
  const AZUL = '#1f4e79', AZUL_OSC = '#163a5c', TINTA = '#1b2430', GRIS = '#5b6675', LINEA = '#d9dde3', FONDO = '#eef1f4', SUAVE = '#e3ecf5';
  const ROJO = '#a3302a', ROJO_BG = '#fbeceb';
  const SERIF = "Georgia,'Times New Roman',serif", SANS = "'Segoe UI',Calibri,Arial,Helvetica,sans-serif";
  const F = esc(farmaco), I = esc(indicacion || '—');

  const paso = (n, nombre, estado) => {
    const ok = estado === 'ok', act = estado === 'actual';
    const bg = ok ? AZUL : (act ? SUAVE : '#ffffff'), bd = (ok || act) ? AZUL : LINEA, tx = ok ? '#ffffff' : (act ? AZUL : '#9aa5b4');
    return '<td align="center" valign="top" style="width:33%;padding:0 4px"><div style="width:30px;height:30px;line-height:30px;border-radius:50%;background:' + bg +
      ';border:2px solid ' + bd + ';color:' + tx + ';font:bold 14px ' + SANS + ';text-align:center;margin:0 auto">' + (ok ? '&#10003;' : n) + '</div>' +
      '<div style="font:' + ((ok || act) ? 'bold' : 'normal') + ' 12px ' + SANS + ';color:' + ((ok || act) ? TINTA : '#9aa5b4') + ';margin-top:6px">' + nombre + '</div></td>';
  };
  const pasos = soloProponer ? '' : '<tr><td style="padding:18px 32px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>' +
    paso(1, 'Recibida', 'ok') + paso(2, 'En preparación', 'actual') + paso(3, 'Enviada', '') + '</tr></table></td></tr>';

  const datos = [['Fármaco', F], ['Indicación', I], ['Recibida', esc(fecha)]];
  if (!soloProponer) datos.push(['Plazo estimado', '<b>' + esc(plazo) + '</b>']);
  const filas = datos.map((d, i) => {
    const b = i === datos.length - 1 ? '' : 'border-bottom:1px solid #d3deeb;';
    return '<tr><td valign="top" style="padding:10px 0;' + b + 'font:12px ' + SANS + ';color:' + GRIS + ';text-transform:uppercase;letter-spacing:.06em;width:38%">' + d[0] + '</td>' +
      '<td valign="top" style="padding:10px 0;' + b + 'font:15px ' + SANS + ';color:' + TINTA + '">' + d[1] + '</td></tr>';
  }).join('');

  const eyebrow = soloProponer ? 'Propuesta recibida' : 'Solicitud recibida';
  const titulo = soloProponer ? 'Gracias por tu propuesta' : 'Estamos preparando tu informe';
  const lead = soloProponer
    ? 'Hemos recibido tu propuesta de <b>' + F + '</b>. El equipo de VERA la revisará y, si procede, publicará el informe en la web, ya verificado.'
    : 'Hemos recibido tu solicitud de <b>' + F + '</b>. Te enviaremos el informe a este correo, en PDF y en Word, en cuanto esté listo.';
  const aviso = soloProponer ? '' : '<tr><td style="padding:20px 32px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="background:' + ROJO_BG +
    ';border-left:4px solid ' + ROJO + ';border-radius:0 8px 8px 0;padding:14px 16px;font:14px/1.55 ' + SANS + ';color:' + TINTA + '"><b style="color:' + ROJO +
    '">Informe automático, no revisado por VERA.</b> Se genera automáticamente a partir de los documentos que aportaste y de fuentes públicas. Cada cifra indica su fuente y su página: verificar los datos antes de usar el informe es responsabilidad tuya. No sustituye el criterio de la Comisión de Farmacia y Terapéutica.</td></tr></table></td></tr>';
  const nota = soloProponer ? 'Te avisaremos cuando esté publicado.' : 'Si hay muchas solicitudes, puede tardar algo más. No hace falta que hagas nada: te llegará solo.';

  const html = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"></head>' +
    '<body style="margin:0;padding:0;background:' + FONDO + '"><div style="display:none;max-height:0;overflow:hidden;opacity:0">' + titulo + '</div>' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:' + FONDO + '"><tr><td align="center" style="padding:28px 12px">' +
    '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid ' + LINEA + '">' +
    '<tr><td style="background:' + AZUL + ';background-image:linear-gradient(135deg,' + AZUL + ' 0%,' + AZUL_OSC + ' 100%);padding:26px 32px"><table role="presentation" cellpadding="0" cellspacing="0"><tr>' +
    '<td valign="middle" style="padding-right:14px"><img src="' + LOGO + '" width="48" height="48" alt="VERA" style="display:block;border:0;border-radius:50%;background:#ffffff"></td>' +
    '<td valign="middle"><div style="font:bold 26px ' + SERIF + ';letter-spacing:.18em;color:#ffffff;line-height:1">VERA</div>' +
    '<div style="font:12px ' + SANS + ';color:#c9d9ea;margin-top:5px">Valoración de la Evidencia y Relevancia Asistencial</div></td></tr></table></td></tr>' +
    '<tr><td style="padding:32px 32px 8px"><div style="font:bold 12px ' + SANS + ';color:' + AZUL + ';text-transform:uppercase;letter-spacing:.12em">' + eyebrow + '</div>' +
    '<div style="font:bold 28px ' + SERIF + ';color:' + TINTA + ';line-height:1.2;margin:8px 0 14px">' + titulo + '</div>' +
    '<div style="font:16px/1.6 ' + SANS + ';color:#3a4552">' + lead + '</div></td></tr>' + pasos +
    '<tr><td style="padding:20px 32px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:' + SUAVE + ';border-radius:10px;padding:6px 18px">' + filas + '</table></td></tr>' +
    aviso +
    '<tr><td style="padding:18px 32px 0;font:14px/1.6 ' + SANS + ';color:' + GRIS + '">' + nota + '</td></tr>' +
    '<tr><td align="left" style="padding:24px 32px 30px"><a href="' + WEB + 'solicitar.html" style="display:inline-block;background:' + AZUL + ';color:#ffffff;text-decoration:none;font:bold 15px ' + SANS + ';padding:13px 26px;border-radius:9px">Ver cómo funciona &rarr;</a></td></tr>' +
    '<tr><td style="padding:0 32px"><div style="border-top:1px solid ' + LINEA + '"></div></td></tr>' +
    '<tr><td style="padding:22px 32px 26px"><table role="presentation" cellpadding="0" cellspacing="0"><tr>' +
    '<td valign="top" style="padding-right:12px"><img src="' + LOGO + '" width="38" height="38" alt="" style="display:block;border:0;border-radius:50%"></td>' +
    '<td valign="top"><div style="font:bold 15px ' + SANS + ';color:' + TINTA + '">Equipo VERA</div><div style="font:13px ' + SANS + ';color:' + GRIS + ';margin-top:2px">Informes de evaluación de medicamentos</div>' +
    '<div style="font:13px ' + SANS + ';margin-top:4px"><a href="' + WEB + '" style="color:' + AZUL + ';text-decoration:none">vera-fharma.github.io/Vera</a></div></td></tr></table></td></tr></table>' +
    '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px"><tr><td style="padding:16px 24px;font:12px/1.5 ' + SANS + ';color:#8a94a3;text-align:center">' +
    (soloProponer ? 'Recibes este correo porque propusiste un fármaco a VERA. Tu correo solo se usa para avisarte sobre tu propuesta.<br>'
      : 'Recibes este correo porque solicitaste un informe en VERA. Tu correo solo se usa para enviarte el informe; los documentos y los datos de la solicitud se eliminan tras el envío.<br>') +
    'Este mensaje se envía automáticamente. Si tienes dudas, puedes responder a este correo.</td></tr></table></td></tr></table></body></html>';

  const asunto = 'VERA · Hemos recibido tu ' + (soloProponer ? 'propuesta' : 'solicitud') + ' de ' + farmaco;
  const texto = soloProponer
    ? 'Hemos recibido tu propuesta de ' + farmaco + '. El equipo de VERA la revisará.\n\nVERA · ' + WEB
    : 'Hemos recibido tu solicitud de ' + farmaco + '. Te enviaremos el informe ' + plazo + '.\n\nInforme automático, no revisado por VERA: verificar los datos es responsabilidad tuya.\n\nVERA · ' + WEB;
  return { asunto: asunto, html: html, texto: texto };
}

/** Prueba: envía a la cuenta de VERA un acuse de ejemplo con el diseño nuevo. */
function probarAcuse() {
  const m = plantillaAcuse('Nerandomilast', 'fibrosis pulmonar idiopática', '25/10/2026, 18:00', 'en la próxima hora aproximadamente', false);
  GmailApp.sendEmail(Session.getActiveUser().getEmail(), '[Prueba] ' + m.asunto, m.texto, { htmlBody: m.html, name: 'VERA' });
}
