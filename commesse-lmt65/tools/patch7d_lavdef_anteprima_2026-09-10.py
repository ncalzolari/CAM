#!/usr/bin/env python3
"""Patch 7d (10/09/2026): anteprima grafica nella libreria operativa.
Ogni riga di "Definizioni delle lavorazioni" mostra la sezione DXF del profilo con la faccia evidenziata e
l'utensile alla quota Y (stesso disegno dello schema pezzo, sezioneFacciaSvg). Selettore del profilo di
anteprima per le righe di serie (default: telaio per fissaggi/scontri/drenaggi telaio, anta per cerniere/
martellina/drenaggi anta), profilo fisso per le eccezioni. Aggiornamento immediato al cambio di Y/faccia/v1/v2."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[1]
def patch(path, subs):
    s = path.read_text(encoding='utf-8')
    for old, new in subs:
        assert s.count(old) == 1, (path.name, old[:70], s.count(old))
        s = s.replace(old, new)
    path.write_text(s, encoding='utf-8')

patch(R/'src'/'app_logic.js', [
    # dimensione parametrica dello schema di sezione
    ("function sezioneFacciaSvg(f, col, lav, maxY, prof){\n  const S=104, mg=10, a=S-2*mg;",
     "function sezioneFacciaSvg(f, col, lav, maxY, prof, S){\n  S = S||104; const mg=10, a=S-2*mg;"),
    # anteprima: profilo scelto + svg
    ("function disegnaLavDef(){",
     """// anteprima grafica di una definizione: sezione del profilo, faccia e utensile alla quota Y (Z e X non rappresentati)
const LAV_PREV = (function(){ try{ return JSON.parse(localStorage.getItem('lav_prev')||'{}'); }catch(e){ return {}; } })();
function profiloAnteprima(serie, k, prof){
  const key = serie+'|'+k;
  if(prof!==undefined){ LAV_PREV[key] = prof; try{ localStorage.setItem('lav_prev', JSON.stringify(LAV_PREV)); }catch(e){} }
  if(LAV_PREV[key]) return LAV_PREV[key];
  const lista = profiliSerie(serie).filter(p=>!/^N458|^FV|^K/.test(p)), dx = DATI.dxf_sez||{};
  const nome = p=>((DATI.profili_ana||{})[p]||{}).nome||'';
  const vista = !!((DATI.serie_info||{})[serie]||{}).in_vista;
  const pri = /^(cern|mart|dren_anta)/.test(k) ? (vista ? [/^anta in vista/i, /^anta/i, /anta/i] : [/^anta/i, /anta/i]) : [/^telaio/i, /^stipite/i, /telaio/i];
  for(const re of pri){ const p = lista.find(p=>dx[p] && re.test(nome(p))); if(p) return p; }
  return lista.find(p=>dx[p]) || lista[0] || '';
}
function svgAnteprimaLav(serie, k, art, prof){
  const d = lavDef(k, serie, art); const ff = facciaFisica(prof, d.f);
  const FCOL = {'1':'#1B2328','2':'#5C6B76','3':'#0F6B3C','4':'#8A5A00'};
  const geo = d.v2 ? `${d.v1}×${d.v2}` : `Ø${Math.round(20*parseFloat(d.v1))/10}`;
  return sezioneFacciaSvg(ff, FCOL[ff]||'#BE1622', [{y:d.y, v1:d.v1, v2:d.v2}], Math.abs(d.y)||40, prof, 150) +
    `<div class="nota-piccola" style="text-align:center">${geo} · F${d.f}${ff!==d.f?` (fisica F${ff})`:''} · Y ${d.y} · Z ${d.z}${(DATI.dxf_sez||{})[prof]?'':' · sezione DXF assente'}</div>`;
}
function aggiornaAnteprimeLav(serie){
  document.querySelectorAll('#tab-lavdef .lav-prev').forEach(el=>{
    const k = el.dataset.k, art = el.dataset.art||null; const prof = art || profiloAnteprima(serie, k);
    el.querySelector('.lav-prev-svg').innerHTML = svgAnteprimaLav(serie, k, art, prof); });
}
function disegnaLavDef(){"""),
    # cella anteprima nelle righe di serie e di eccezione
    ("  let h = '';\n  chiavi.forEach(k=>{\n    const d = S[k];\n    h += `<tr><td><b>${NOMI_LAV[k]||k}</b><br><span class=\"nota-piccola\">${k}</span></td>${campi.map(c=>`<td>${cella(k,null,c,d[c],false)}</td>`).join('')}",
     """  const prev = (k, art)=>{ const prof = art || profiloAnteprima(serie, k);
    return `<td class="lav-prev" data-k="${k}" data-art="${art||''}"><div class="lav-prev-svg">${svgAnteprimaLav(serie, k, art, prof)}</div>${art?'':`<select data-prev="${k}" title="Profilo su cui vedere la lavorazione" style="font-size:.72rem;padding:.15rem .3rem;width:9.4rem">${prof_dx.map(p=>`<option ${p===prof?'selected':''}>${p}</option>`).join('')}</select>`}</td>`; };
  const prof_dx = prof.filter(p=>!/^N458|^FV|^K/.test(p));
  let h = '';
  chiavi.forEach(k=>{
    const d = S[k];
    h += `<tr><td><b>${NOMI_LAV[k]||k}</b><br><span class="nota-piccola">${k}</span></td>${prev(k,null)}${campi.map(c=>`<td>${cella(k,null,c,d[c],false)}</td>`).join('')}"""),
    ("${prof.includes(art)?'':`<option selected>${art}</option>`}</select></td>\n        ${campi.map(c=>`<td>${cella(k,art,c,o[c],true)}</td>`).join('')}",
     "${prof.includes(art)?'':`<option selected>${art}</option>`}</select></td>${prev(k,art)}\n        ${campi.map(c=>`<td>${cella(k,art,c,o[c],true)}</td>`).join('')}"),
    ("<tr><td colspan=\"10\" class=\"nota-piccola\">Nessuna definizione per questa serie", "<tr><td colspan=\"11\" class=\"nota-piccola\">Nessuna definizione per questa serie"),
    # aggiornamento anteprime al cambio dei campi e del profilo di anteprima
    ("    else { LAV_DEF[serie][k][c] = num(c) ? (parseFloat(v.replace(',','.'))||0) : v; }\n    salvaLavDef();\n  }));",
     "    else { LAV_DEF[serie][k][c] = num(c) ? (parseFloat(v.replace(',','.'))||0) : v; }\n    salvaLavDef(); aggiornaAnteprimeLav(serie);\n  }));\n"
     "  tb.querySelectorAll('[data-prev]').forEach(s=>s.addEventListener('change', ()=>{ profiloAnteprima(serie, s.dataset.prev, s.value); aggiornaAnteprimeLav(serie); }));"),
])
patch(R/'src'/'app_template.html', [
    ('<table id="tab-lavdef" style="min-width:1180px">', '<table id="tab-lavdef" style="min-width:1380px">'),
    ('<thead><tr><th>Lavorazione</th><th>Descrizione nel job</th>', '<thead><tr><th>Lavorazione</th><th>Sezione · faccia · Y</th><th>Descrizione nel job</th>'),
    ('  #tab-lavdef button{white-space:nowrap}', '  #tab-lavdef button{white-space:nowrap}\n  #tab-lavdef td.lav-prev{text-align:center; padding:.2rem .3rem}'),
    ("Y, Z in mm; faccia; utensile). \"+ profilo\"", "Y, Z in mm; faccia; utensile). La colonna \"Sezione\" mostra la sezione del profilo scelto con la faccia evidenziata (barra colorata, zero sullo spigolo camera) e l'utensile alla quota Y; per le eccezioni il profilo è quello della riga. \"+ profilo\""),
])
print('patch 7d OK')
