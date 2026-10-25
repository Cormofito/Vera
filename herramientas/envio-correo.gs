/**
 * VERA · envío de informes por correo (Google Apps Script, cuenta vera.informes@gmail.com)
 *
 * Recibe por HTTPS (POST, JSON) el informe generado por la tarea diaria y lo envía por Gmail
 * desde la cuenta de VERA, con el PDF y el Word adjuntos.
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
