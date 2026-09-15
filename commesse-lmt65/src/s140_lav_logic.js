
// ======================================================================================
// S140 (alzante scorrevole L&S / scorrevole in linea R) — lavorazioni macchina
// Fonte: manuale lavorazioni e assemblaggio AluK S140 v3A (sez. 9 "Lavorazioni", pag. 9.01-9.49).
// STATO: TUTTO DA TARARE. A differenza di C75S/C82S-CS (calibrate su job di produzione reali)
// per S140 non esiste ancora nessun job di produzione: la serie non è mai stata fabbricata.
// Le quote X lungo la barra (passi, distanze dagli estremi) e i diametri/dimensioni asola sono
// quelli letti sul manuale; la quota Y (posizione della lavorazione nella sezione del profilo),
// la faccia macchina e i codici utensile sono STIME (Y = valore ricorrente nel disegno o centro
// sezione da DATI.profili_ana, faccia F1 per convenzione mai validata, utensili segnaposto) —
// vanno verificate/corrette dal pannello "Tarature lavorazioni" alla prima produzione reale.
//
// Coperto da questo modulo:
//  - Fissaggio telaio a muro (9.01): Ø5, 200 mm dagli estremi, passo <=800 mm, su ogni traverso/
//    montante dei telai U10020/U10400/U10060/U10061/U10402/U10403/U10000/U10401.
//  - Squadretta telaio (9.02): 2x Ø8 per angolo (49.8 e 99.6 mm dal filo di squadro) sui tagli a
//    45° di U10020/U10060/U10061/U10000 (i profili soglia ribassata si assemblano diversamente,
//    vedi sospeso sotto).
//  - Squadretta anta (9.41, sez. superiore): Ø5 a 7.7 mm dal filo di squadro sui tagli a 45° di
//    ogni pezzo U10140 (traverso/montante anta, di ogni tipologia).
//  - Drenaggio soglia (9.04/9.06/9.08/9.10/9.12/9.14): asola 5x30 (fresa 909333), passo ~400 mm
//    su zona esposta, bordo dagli estremi per profilo, sui pezzi soglia (il traverso telaio
//    inferiore quando la soglia è standard, il pezzo dedicato U10400/U10402/U10403/U10401
//    quando la soglia è ribassata).
//  - Ventilazione/drenaggio anta apribile (9.48): asola 5x15 su ogni traverso anta (non centrale)
//    delle tipologie scorrevoli (forma "S:...").
//
// NON coperto (mancano quote a disegno, vedi CLAUDE.md/dossier per il dettaglio pagina per pagina):
//  - Montaggio montante centrale OX/OXO (9.24-9.28, 9.34-9.36): la foratura è definita dalla dima
//    fisica T10082 (nessuna quota mm a disegno).
//  - Foratura montante <-> soglia ribassata (9.03): assemblaggio specifico soglia ribassata.
//  - Ferramenta maniglia/meccanismo alzante e serratura scorrevole (9.42, 9.45): le quote ci sono,
//    ma manca la taratura dell'altezza maniglia (AM) per S140 (nessun equivalente Maico calibrato).
//  - Paracolpo + colonnina K1459 (9.49): K1459 non è un pezzo tagliato da nessuna delle 36
//    tipologie del programma (nessun profilo corrispondente in DATI.profili_ana).
//  - Tutta la sez. 10 "Assemblaggio" (viti, sigillante, spugne): sono istruzioni di montaggio a
//    banco, non lavorazioni macchina — non generano MACHINING nel job.
// ======================================================================================
function s140Lav(w, descr, x, y, z, f, v1, v2, ut){
  return {x:Math.round(x*10)/10, w, v1:String(v1), v2:v2==null?'':String(v2), v3:'2',
          y:Math.round(y*1000)/1000, z, f:String(f), ut:String(ut), descr:descr+' [DA TARARE]'};
}
function s140Foro(descr, x, y, d, f, z, ut){ return s140Lav('#0', descr, x, y, z, f, d/2, '', ut); }
function s140Asola(descr, xc, y, larg, lung, f, z, ut){ return s140Lav('#1', descr, xc, y, z, f, larg, lung, ut); }
// posizioni lungo la barra: bordo dagli estremi + intermedie equidistanti, passo massimo <passo>
function s140PosPerimetrali(L, bordo, passo){
  const span = L - 2*bordo;
  if(span<=0) return [Math.round(L/2*10)/10];
  const n = Math.max(1, Math.ceil(span/passo)), p = span/n;
  return Array.from({length:n+1}, (_,i)=>Math.round((bordo+i*p)*10)/10);
}
// drenaggio soglia (9.04/06/08/10/12/14): bordo/passo lungo la barra, larg/lung asola, y/z nella sezione, utensile
const S140_DREN = {
  U10020: {bordo:160, passo:400, larg:5, lung:30, y:15, z:-6.5, ut:'909333'},
  U10060: {bordo:160, passo:400, larg:5, lung:30, y:15, z:-6.5, ut:'909333'},
  U10061: {bordo:160, passo:400, larg:5, lung:30, y:15, z:-6.5, ut:'909333'},
  U10000: {bordo:160, passo:400, larg:5, lung:30, y:15, z:-6.6, ut:'909333'},
  U10400: {bordo:100, passo:400, larg:5, lung:30, y:8,  z:-2.5, ut:'909333'},
  U10402: {bordo:100, passo:400, larg:5, lung:30, y:8,  z:-2.5, ut:'909333'},
  U10403: {bordo:100, passo:400, larg:5, lung:30, y:8,  z:-2.5, ut:'909333'},
  U10401: {bordo:100, passo:400, larg:5, lung:30, y:8,  z:-2.8, ut:'909333'},
};
const S140_TELAIO_SQUADRETTA = ['U10020','U10060','U10061','U10000'];
function lavS140(t, r, p, k, mm, conDren, conForo8, accessori){
  const out=[]; const art = p.art, d = (p.desc||'').toLowerCase(), F1 = '1';
  const w = (DATI.profili_ana[art]||{}).w || 100;                     // profondità sezione (per stimare la quota Y al centro)
  const angoli = String(p.ang||'').split('-'); const a45 = angoli[0]==='45', b45 = angoli[1]==='45';
  const isTelaio = !!S140_DREN[art] && !/soglia/i.test(d);            // telaio "principale" (non il pezzo dedicato soglia ribassata)
  const isSogliaRibassata = /soglia/i.test(d);
  const isSogliaStandard = !!S140_DREN[art] && !isSogliaRibassata && /traverso telaio/.test(d) && k===0;
  const isAntaS140 = art==='U10140';
  const isTraversoAnta = isAntaS140 && /traverso anta/.test(d) && !/centrale/.test(d);

  // ---------- 1) FISSAGGIO TELAIO A MURO (9.01): Ø5, 200 mm dagli estremi, passo <=800 mm ----------
  if(conDren && !!S140_DREN[art]){
    s140PosPerimetrali(mm, 200, 800).forEach(x=>
      out.push(s140Foro('Fissaggio telaio Ø5 (9.01)', x, 31.3, 5, F1, -10, 'S5')));
  }
  // ---------- 2) SQUADRETTA TELAIO (9.02): 2x Ø8 per angolo, sui tagli a 45° ----------
  if(conForo8 && S140_TELAIO_SQUADRETTA.includes(art)){
    const y = Math.round(w/2*10)/10;
    if(a45){
      out.push(s140Foro('Squadretta telaio Ø8 (9.02)', 49.8, y, 8, F1, -15, 'S8'));
      out.push(s140Foro('Squadretta telaio Ø8 (9.02)', 99.6, y, 8, F1, -15, 'S8'));
    }
    if(b45){
      out.push(s140Foro('Squadretta telaio Ø8 (9.02)', Math.round((mm-49.8)*10)/10, y, 8, F1, -15, 'S8'));
      out.push(s140Foro('Squadretta telaio Ø8 (9.02)', Math.round((mm-99.6)*10)/10, y, 8, F1, -15, 'S8'));
    }
  }
  // ---------- 3) DRENAGGIO SOGLIA (9.04-9.14): asola 5x30 ----------
  if(conDren && (isSogliaRibassata || isSogliaStandard) && S140_DREN[art]){
    const dd = S140_DREN[art];
    s140PosPerimetrali(mm, dd.bordo, dd.passo).forEach(x=>
      out.push(s140Asola(`Drenaggio soglia ${art} 5×30 (9.0x)`, x, dd.y, dd.larg, dd.lung, F1, dd.z, dd.ut)));
  }
  // ---------- 4) SQUADRETTA ANTA (9.41): Ø5 a 7.7 mm dal filo di squadro, sui tagli a 45° ----------
  if(conForo8 && isAntaS140){
    const y = Math.round(w/2*10)/10;
    if(a45) out.push(s140Foro('Squadretta anta Ø5 (9.41)', 7.7, y, 5, F1, -10, 'S5'));
    if(b45) out.push(s140Foro('Squadretta anta Ø5 (9.41)', Math.round((mm-7.7)*10)/10, y, 5, F1, -10, 'S5'));
  }
  // ---------- 5) VENTILAZIONE/DRENAGGIO ANTA APRIBILE (9.48): asola 5x15 ----------
  if(conForo8 && isTraversoAnta && t.forma && String(t.forma).startsWith('S:')){
    const y = Math.round(w/2*10)/10, x = k===0 ? 100 : Math.round((mm-100)*10)/10;
    out.push(s140Asola('Ventilazione anta 5×15 (9.48)', x, y, 5, 15, F1, -3, 'F515'));
  }
  return out;
}
