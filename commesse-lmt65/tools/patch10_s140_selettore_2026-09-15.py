#!/usr/bin/env python3
"""S140: selettore tipologia riunito per sigla (XX, OX, 3A...) con menu a tendina separati per
montante (standard/slim) e soglia (standard/ribassata), + Lato apribile per i gruppi OX. Il vecchio
select #r-tip piatto resta come "sorgente di verità" nascosta (tutta la logica esistente lo legge/scrive
invariata): i nuovi controlli lo impostano e lo fanno scattare (change) invece di sostituirlo."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def patch(path, subs):
    p = os.path.join(ROOT, path); s = open(p, encoding='utf-8').read()
    for old, new, n in subs:
        c = s.count(old); assert c == n, f'{path}: attese {n} occorrenze, trovate {c}: {old[:70]!r}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)
    print(path, 'ok')

patch('src/app_template.html', [
    ('<div><label>Tipologia</label><select id="r-tip"></select></div>',
     '''<div id="box-tip-flat"><label>Tipologia</label><select id="r-tip"></select></div>
            <div id="box-tip-s140" style="display:none">
              <label>Tipologia (sigla)</label><select id="r-sigla"></select>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.5rem;margin-top:.4rem">
                <div><label>Montante</label><select id="r-montante-s140"><option value="standard">Standard</option><option value="slim">Slim</option></select></div>
                <div><label>Soglia</label><select id="r-soglia-s140"><option value="standard">Standard</option><option value="ribassata">Ribassata</option></select></div>
                <div id="box-lato-s140" style="display:none"><label>Lato apribile</label><select id="r-lato-s140"><option value="esterna">Esterna</option><option value="interna">Interna</option></select></div>
              </div>
            </div>''', 1),
])

patch('src/app_logic.js', [
    ('''function aggiornaTipologie(){
  const s = $('#r-serie').value;
  $('#r-tip').innerHTML = DATI.tipologie.filter(t=>t.serie===s && !t.nascosta)
    .map(t=>`<option value="${t.id}">[${t.cod}] ${t.nome}</option>`).join('');
  mostraAvvisoTip(); aggiornaSelettoriProfili(); aggiornaAnteprima();
}''',
     '''function aggiornaTipologie(){
  const s = $('#r-serie').value;
  $('#r-tip').innerHTML = DATI.tipologie.filter(t=>t.serie===s && !t.nascosta)
    .map(t=>`<option value="${t.id}">[${t.cod}] ${t.nome}</option>`).join('');
  const raggr = s==='S140';   // S140: selettore riunito per sigla + montante/soglia/lato invece dell'elenco piatto
  $('#box-tip-flat').style.display = raggr ? 'none' : '';
  $('#box-tip-s140').style.display = raggr ? '' : 'none';
  if(raggr) aggiornaSiglaS140();
  mostraAvvisoTip(); aggiornaSelettoriProfili(); aggiornaAnteprima();
}
// S140: una tipologia per sigla (id "gruppo", es. XX/OX/3A) copre più varianti montante/soglia/lato
function tipiPerSiglaS140(){
  const viste = new Set(), out = [];
  DATI.tipologie.filter(t=>t.serie==='S140' && !t.nascosta).forEach(t=>{
    if(!viste.has(t.sigla)){ viste.add(t.sigla); out.push(t); }
  });
  return out;
}
function aggiornaSiglaS140(){
  $('#r-sigla').innerHTML = tipiPerSiglaS140().map(t=>`<option value="${t.sigla}">${t.gruppo}</option>`).join('');
  aggiornaVarianteS140();
}
function aggiornaVarianteS140(){
  const sigla = $('#r-sigla').value;
  const conLato = DATI.tipologie.some(t=>t.serie==='S140' && t.sigla===sigla && t.lato);
  $('#box-lato-s140').style.display = conLato ? '' : 'none';
  risolviTipS140();
}
function risolviTipS140(){
  const sigla = $('#r-sigla').value, montante = $('#r-montante-s140').value, soglia = $('#r-soglia-s140').value;
  const conLato = $('#box-lato-s140').style.display!=='none', lato = conLato ? $('#r-lato-s140').value : null;
  const t = DATI.tipologie.find(x=>x.serie==='S140' && x.sigla===sigla && x.montante===montante && x.soglia===soglia && (conLato ? x.lato===lato : !x.lato));
  if(t){ $('#r-tip').value = t.id; $('#r-tip').dispatchEvent(new Event('change')); }
}''', 1),
    ('''  $('#r-serie').addEventListener('change', aggiornaTipologie);
  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); if(isPorta($('#r-serie').value) || tipProfili($('#r-serie').value)) aggiornaSelettoriProfili(); else aggiornaSezioni();});''',
     '''  $('#r-serie').addEventListener('change', aggiornaTipologie);
  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); if(isPorta($('#r-serie').value) || tipProfili($('#r-serie').value)) aggiornaSelettoriProfili(); else aggiornaSezioni();});
  $('#r-sigla').addEventListener('change', aggiornaVarianteS140);
  ['#r-montante-s140','#r-soglia-s140','#r-lato-s140'].forEach(id=>$(id).addEventListener('change', risolviTipS140));''', 1),
])
print('patch 10 applicata')
