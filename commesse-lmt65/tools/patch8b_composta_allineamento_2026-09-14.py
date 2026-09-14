#!/usr/bin/env python3
"""Patch 8b (14/09/2026): allineamento del costruttore alle tipologie singole.
- Marcatura "[DA VERIFICARE composta]" solo per le celle che confinano con almeno un profilo T: una cella delimitata
  da soli stipiti (unità 1x1, telai accoppiati) produce esattamente le lavorazioni della tipologia singola (verificato
  con il confronto headless C75S_FIN_1ANTA 1200x1650 vs costruttore 1x1 ADX).
- Drenaggi secondo lo schema aziendale confermato (sez. 5 del dossier) anche nel costruttore: traverso stipite inferiore
  alle posizioni FX ±2 (lavDrenTelaioFP), traverso anta 2xØ8 a 168 dagli estremi, montanti anta 1xØ8 a 218 (alternato)."""
import pathlib
P = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'app_logic.js'
s = P.read_text(encoding='utf-8')
def sost(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)
# marcatura solo con bordi T
sost("    const nodoSu = yb(rr)+spanH;                                        // asse del traverso sopra la cella (quota dal basso)\n    const metti = (p, lav)=>{ p.arr.push(...lav); };",
     "    const nodoSu = yb(rr)+spanH;                                        // asse del traverso sopra la cella (quota dal basso)\n"
     "    const conT = !(bordi.sx && bordi.dx && bordi.su && bordi.giu);      // cella con almeno un profilo T: lavorazioni da verificare\n"
     "    const metti = (p, lav)=>{ if(conT) lav.forEach(l=>{ if(!/DA VERIFICARE composta/.test(l.descr)) l.descr = (l.descr||'')+' [DA VERIFICARE composta]'; }); p.arr.push(...lav); };")
sost("      LAV_CTX.art = anta; F.ant[id] = {k: manoDx?1:0, lav: lavMartellina(ah, hm)};\n    } else {",
     "      LAV_CTX.art = anta; F.ant[id] = {k: manoDx?1:0, lav: lavMartellina(ah, hm)}; if(conT) F.ant[id].lav.forEach(l=>l.descr += ' [DA VERIFICARE composta]');\n    } else {")
sost("      LAV_CTX.art = anta; F.ant[id] = {k: manoDx?1:0, lav: lavMartellina(ah, hm)};\n    }\n  }\n  const marca = arr=>arr.forEach(l=>{ if(!/DA VERIFICARE composta/.test(l.descr)) l.descr = (l.descr||'')+' [DA VERIFICARE composta]'; });\n  F.tell.forEach(marca); F.telh.forEach(marca); F.trvV.forEach(marca); F.trvO.forEach(rw=>rw.forEach(marca)); Object.values(F.ant).forEach(a=>marca(a.lav));\n  return F;",
     "      LAV_CTX.art = anta; F.ant[id] = {k: manoDx?1:0, lav: lavMartellina(ah, hm)}; if(conT) F.ant[id].lav.forEach(l=>l.descr += ' [DA VERIFICARE composta]');\n    }\n  }\n  return F;")
# drenaggi: traverso stipite inferiore alle posizioni FX ±2 (come le tipologie in vista)
sost("    if(conDren&&k===1){ const pos=posizioniDrenaggio(L);\n      lav.push(...pos.map(x=>lavDrenaggio(t.serie,'telaio',x))); capDrenaggio(t.serie,accessori,pos.length); }",
     "    if(conDren&&k===1){ const dl = lavDrenTelaioFP(L, t.serie);                // schema aziendale: alle posizioni FX ±2\n      lav.push(...dl); capDrenaggio(t.serie,accessori,dl.length); }")
# drenaggi anta: traverso a 168 dagli estremi (solo traverso inferiore), montanti a 218 alternato
sost("        spingi(anta,'Traverso battente sx',`${id}-ANTL`,pzS,'45-45',\n          agg.conAnte? posizioniDrenaggio(pzS).map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);",
     "        spingi(anta,'Traverso battente sx',`${id}-ANTL`,pzS,'45-45',\n          agg.conAnte? [168, Math.round((pzS-168)*10)/10].map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);")
sost("        spingi(anta,'Traverso battente dx',`${id}-ANTL`,pzD,'45-45',\n          agg.conAnte? posizioniDrenaggio(pzD).map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);",
     "        spingi(anta,'Traverso battente dx',`${id}-ANTL`,pzD,'45-45',\n          agg.conAnte? [168, Math.round((pzD-168)*10)/10].map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);")
sost("        for(let k=0;k<3;k++) spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          (agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : [])",
     "        for(let k=0;k<3;k++) spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          (agg.conAnte? [lavDrenaggio(t.serie,'antaMont', k%2===0 ? 218 : Math.round((ah-218)*10)/10)] : [])")
sost("        spingi(anta,'Traverso battente',`${id}-ANTL`,aw,'45-45',\n          agg.conAnte? posizioniDrenaggio(aw).map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);",
     "        spingi(anta,'Traverso battente',`${id}-ANTL`,aw,'45-45',\n          agg.conAnte? [168, Math.round((aw-168)*10)/10].map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);")
sost("        [0,1].forEach(k=>spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          (agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : [])",
     "        [0,1].forEach(k=>spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          (agg.conAnte? [lavDrenaggio(t.serie,'antaMont', k===0 ? 218 : Math.round((ah-218)*10)/10)] : [])")
P.write_text(s, encoding='utf-8'); print('patch 8b OK')
