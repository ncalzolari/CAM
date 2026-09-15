# Versione "web" del programma per la pubblicazione come Artifact claude.ai: dist/Commesse_COR80.html -> dist/Commesse_COR80_web.html
# - toglie doctype/html/head/body (li aggiunge il contenitore) e il caricamento di dati_serie.js (non ammesso);
# - i download (job XML, commessa JSON, archivio dati) passano dalla capability `downloads` del visualizzatore:
#   le estensioni .xml/.js non sono ammesse, quindi il file viene impacchettato in uno .zip (dentro il file conserva il nome .xml/.js);
#   se anche lo zip venisse rifiutato, ripiego su .xml.txt / .js.txt (da rinominare).
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'dist', 'Commesse_COR80.html'), encoding='utf-8').read()
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:60]!r}'
    return s.replace(old, new)
s = src
for tag in ['<!DOCTYPE html>\n', '<html lang="it">\n', '<head>\n', '<meta charset="utf-8">\n', '<meta name="viewport" content="width=device-width, initial-scale=1">\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n']:
    s = rep(s, tag, '')
s = rep(s, '<title>Commesse COR80 — Cortizo COR 80 Evolution → FOM LMT 65</title>', '<title>Commesse COR80</title>')
s = rep(s, '<script src="dati_serie.js"></script>\n', '')
# download tramite capability
s = rep(s, """function scarica(blob, nome){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = nome; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
}""", """let __dlCap = null, __dlPronto = false;
if(window.claude && typeof claude.use==='function') claude.use('downloads').then(d=>{ __dlCap = d; __dlPronto = true; }).catch(()=>{ __dlPronto = true; });
const __EXT_OK = ['gif','png','jpg','jpeg','webp','mp4','webm','txt','json','md','docx','pptx','epub','csv','ttf','html','svg','pdf','xlsx','zip'];
// zip "store" (senza compressione) di un singolo file: il visualizzatore non ammette .xml/.js, ma ammette .zip -> il file dentro conserva nome ed estensione
const __CRC = (()=>{ const t=new Uint32Array(256); for(let n=0;n<256;n++){ let c=n; for(let k=0;k<8;k++) c = c&1 ? 0xEDB88320 ^ (c>>>1) : c>>>1; t[n]=c>>>0; } return t; })();
function __crc32(u8){ let c=0xFFFFFFFF; for(let i=0;i<u8.length;i++) c = __CRC[(c ^ u8[i]) & 0xFF] ^ (c>>>8); return (c ^ 0xFFFFFFFF)>>>0; }
function __zipSingolo(nome, u8){
  const enc = new TextEncoder().encode(nome), crc = __crc32(u8), n = u8.length;
  const d = new Date(), dosT = (d.getHours()<<11)|(d.getMinutes()<<5)|(d.getSeconds()>>1), dosD = ((d.getFullYear()-1980)<<9)|((d.getMonth()+1)<<5)|d.getDate();
  const loc = new DataView(new ArrayBuffer(30)), cen = new DataView(new ArrayBuffer(46)), end = new DataView(new ArrayBuffer(22));
  const w = (v,o,x,b)=>{ if(b===2) v.setUint16(o,x,true); else v.setUint32(o,x,true); };
  w(loc,0,0x04034b50); w(loc,4,20,2); w(loc,6,0x0800,2); w(loc,8,0,2); w(loc,10,dosT,2); w(loc,12,dosD,2); w(loc,14,crc); w(loc,18,n); w(loc,22,n); w(loc,26,enc.length,2); w(loc,28,0,2);
  w(cen,0,0x02014b50); w(cen,4,20,2); w(cen,6,20,2); w(cen,8,0x0800,2); w(cen,10,0,2); w(cen,12,dosT,2); w(cen,14,dosD,2); w(cen,16,crc); w(cen,20,n); w(cen,24,n); w(cen,28,enc.length,2); w(cen,30,0,2); w(cen,32,0,2); w(cen,34,0,2); w(cen,36,0,2); w(cen,38,0); w(cen,42,0);
  const offCen = 30 + enc.length + n, lenCen = 46 + enc.length;
  w(end,0,0x06054b50); w(end,4,0,2); w(end,6,0,2); w(end,8,1,2); w(end,10,1,2); w(end,12,lenCen); w(end,16,offCen); w(end,20,0,2);
  return new Blob([loc.buffer, enc, u8, cen.buffer, enc, end.buffer], {type:'application/zip'});
}
function scarica(blob, nome){
  // versione web: il visualizzatore non permette i download diretti; si passa dalla capability "downloads" (conferma dell'utente)
  if(!__dlCap){ $('#esito').textContent = __dlPronto ? 'Salvataggio non disponibile in questa vista: usa il programma scaricato (Commesse_COR80.html).' : 'Un attimo: salvataggio in preparazione, riprova.'; return; }
  const ext = (nome.split('.').pop()||'').toLowerCase();
  const salva = (n, dati, msg) => __dlCap.save({filename: n, data: dati})
    .then(()=>{ $('#esito').textContent = `File ${n} salvato.` + msg; })
    .catch(e=>{ if(e && e.code==='declined') return;
      if(e && (e.code==='rejected_extension' || e.code==='extension_not_enabled') && n!==nome+'.txt')
        return salva(nome+'.txt', blob, ` Rinominalo in "${nome}" prima di usarlo (estensione .${ext} non ammessa dal visualizzatore).`);
      $('#esito').textContent = 'Salvataggio non riuscito: ' + ((e && (e.message||e.code)) || e); });
  if(__EXT_OK.includes(ext)) return salva(nome, blob, '');
  blob.arrayBuffer().then(ab => salva(nome+'.zip', __zipSingolo(nome, new Uint8Array(ab)), ` Estrai lo zip: dentro c'è "${nome}" con l'estensione corretta (il visualizzatore non salva file .${ext}).`));
}""")
s = rep(s, """  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'dati_serie.js'; a.click();
  URL.revokeObjectURL(a.href);""", "  scarica(blob, 'dati_serie.js');", 2)
# nota nell'intestazione
s = rep(s, 'distinte, fabbisogno e file macchina</span>', 'distinte, fabbisogno e file macchina &nbsp;·&nbsp; <b>versione web</b>: i file .xml/.js vengono salvati dentro uno .zip (estrarlo)</span>')
open(os.path.join(ROOT, 'dist', 'Commesse_COR80_web.html'), 'w', encoding='utf-8').write(s)
print('web:', len(s), 'bytes ->', 'dist/Commesse_COR80_web.html')
