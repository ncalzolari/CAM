# Versione "web" del programma per la pubblicazione come Artifact claude.ai: dist/Commesse_LMT65.html -> dist/Commesse_LMT65_web.html
# - toglie doctype/html/head/body (li aggiunge il contenitore) e il caricamento di dati_serie.js (non ammesso);
# - i download (job XML, commessa JSON, archivio dati) passano dalla capability `downloads` del visualizzatore:
#   le estensioni .xml/.js non sono ammesse, quindi il file viene salvato come .xml.txt / .js.txt (da rinominare).
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'dist', 'Commesse_LMT65.html'), encoding='utf-8').read()
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:60]!r}'
    return s.replace(old, new)
s = src
for tag in ['<!DOCTYPE html>\n', '<html lang="it">\n', '<head>\n', '<meta charset="utf-8">\n', '<meta name="viewport" content="width=device-width, initial-scale=1">\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n']:
    s = rep(s, tag, '')
s = rep(s, '<title>Commesse serramenti — AluK C75S / C82S-CS → FOM LMT 65</title>', '<title>Commesse LMT65</title>')
s = rep(s, '<script src="dati_serie.js"></script>\n', '')
# download tramite capability
s = rep(s, """function scarica(blob, nome){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = nome; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
}""", """let __dlCap = null, __dlPronto = false;
if(window.claude && typeof claude.use==='function') claude.use('downloads').then(d=>{ __dlCap = d; __dlPronto = true; }).catch(()=>{ __dlPronto = true; });
const __EXT_OK = ['gif','png','jpg','jpeg','webp','mp4','webm','txt','json','md','docx','pptx','epub','csv','ttf','html','svg','pdf','xlsx'];
function scarica(blob, nome){
  // versione web: il visualizzatore non permette i download diretti; si passa dalla capability "downloads" (conferma dell'utente)
  if(!__dlCap){ $('#esito').textContent = __dlPronto ? 'Salvataggio non disponibile in questa vista: usa il programma scaricato (Commesse_LMT65.html).' : 'Un attimo: salvataggio in preparazione, riprova.'; return; }
  const ext = (nome.split('.').pop()||'').toLowerCase();
  const n = __EXT_OK.includes(ext) ? nome : nome + '.txt';
  __dlCap.save({filename: n, data: blob})
    .then(()=>{ $('#esito').textContent = `File ${n} salvato.` + (n!==nome ? ` Rinominalo in "${nome}" prima di usarlo (estensione .${ext} non ammessa dal visualizzatore).` : ''); })
    .catch(e=>{ if(e && e.code==='declined') return; $('#esito').textContent = 'Salvataggio non riuscito: ' + ((e && (e.message||e.code)) || e); });
}""")
s = rep(s, """  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'dati_serie.js'; a.click();
  URL.revokeObjectURL(a.href);""", "  scarica(blob, 'dati_serie.js');", 2)
# nota nell'intestazione
s = rep(s, 'distinte, fabbisogno e file macchina</span>', 'distinte, fabbisogno e file macchina &nbsp;·&nbsp; <b>versione web</b>: i file .xml/.js vengono salvati come .txt, rinominarli</span>')
open(os.path.join(ROOT, 'dist', 'Commesse_LMT65_web.html'), 'w', encoding='utf-8').write(s)
print('web:', len(s), 'bytes ->', 'dist/Commesse_LMT65_web.html')
