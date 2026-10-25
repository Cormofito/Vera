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
  let farmaco = '', quiere = '';
  r.getItemResponses().forEach(ir => {
    const t = ir.getItem().getTitle().toLowerCase();
    if (t.indexOf('principio activo') >= 0) farmaco = String(ir.getResponse());
    if (t.indexOf('qué quieres hacer') >= 0) quiere = String(ir.getResponse());
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

  const asunto = 'VERA · Hemos recibido tu solicitud' + (farmaco ? ' de ' + farmaco : '');
  const texto = soloProponer
    ? 'Hemos recibido tu propuesta' + (farmaco ? ' de ' + farmaco : '') + '. El equipo de VERA la revisará y, si procede, publicará el informe en la web.'
    : 'Hemos recibido tu solicitud' + (farmaco ? ' de ' + farmaco : '') + '. Recibirás el informe en este correo ' + plazo +
      '. Si hay muchas solicitudes, puede tardar algo más.\n\nRecuerda: el informe se genera automáticamente y no está revisado por VERA; verificar los datos es responsabilidad tuya.';
  const html = '<div style="font-family:Calibri,Arial,sans-serif;font-size:14px;color:#1b2430;max-width:620px">' +
    '<p style="font-size:22px;font-weight:bold;color:#1f4e79;margin:0 0 4px">VERA</p>' +
    '<p style="color:#5b6675;margin:0 0 18px">Valoración de la Evidencia y Relevancia Asistencial</p>' +
    texto.split('\n\n').map(p => '<p>' + p + '</p>').join('') +
    '<p style="color:#5b6675;font-size:12px;margin-top:24px">VERA · <a href="https://vera-fharma.github.io/Vera/">vera-fharma.github.io/Vera</a></p></div>';
  GmailApp.sendEmail(correo, asunto, texto, { htmlBody: html, name: 'VERA' });
}
