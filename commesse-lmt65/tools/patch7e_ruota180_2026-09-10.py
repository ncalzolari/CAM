#!/usr/bin/env python3
"""Patch 7e (10/09/2026): orientamento dei profili in macchina, per serie con eccezioni per profilo.
DATI.ruota180[serie] = {'*': bool, '<ART>': bool}: la barra è caricata ruotata di 180° (sull'asse della barra)
rispetto al disegno DXF. Effetto sui DISEGNI (anteprima libreria, schema pezzo, mini-sezioni, schede): sezione
ruotata. Le facce/Y delle lavorazioni non cambiano da sole: il pulsante "scambia le facce delle lavorazioni"
applica F1<->F4, F2<->F3 (Y invariata per le convenzioni di zero: F1 zero a destra, F4 a sinistra, F2 alto, F3 basso)
a tutta la libreria della serie, in un colpo, reversibile. Default: COR80 ruotato (richiesta 10/09/2026)."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[1]
def patch(path, subs):
    s = path.read_text(encoding='utf-8')
    for old, new in subs:
        assert s.count(old) == 1, (path.name, old[:70], s.count(old))
        s = s.replace(old, new)
    path.write_text(s, encoding='utf-8')

patch(R/'src'/'app_logic.js', [
    # stato + helper (prima della libreria operativa, che li usa)
    ("// ---------- libreria operativa: definizioni delle lavorazioni per serie, con eccezioni per profilo ----------",
     """// ---------- orientamento dei profili in macchina: barra ruotata di 180° rispetto al disegno DXF ----------
// DATI.ruota180[serie] = {'*': bool, '<ART>': bool}; copia salvata nel browser (localStorage 'ruota180') con precedenza.
let RUOTA180 = (function(){
  const b = JSON.parse(JSON.stringify(DATI.ruota180||{}));
  try{ const s = localStorage.getItem('ruota180'); if(s){ const l = JSON.parse(s); Object.keys(l).forEach(k=>{ b[k] = Object.assign({}, b[k]||{}, l[k]); }); } }catch(e){}
  return b;
})();
DATI.ruota180 = RUOTA180;
function salvaRuota180(){ DATI.ruota180 = RUOTA180; try{ localStorage.setItem('ruota180', JSON.stringify(RUOTA180)); }catch(e){} }
let PROF_SERIE = null;
function serieDiProfilo(prof){
  if(!PROF_SERIE){ PROF_SERIE = {}; DATI.tipologie.forEach(t=>(t.profili||[]).forEach(p=>{ if(!(p.art in PROF_SERIE)) PROF_SERIE[p.art] = t.serie; }));
    Object.keys(RUOTA180).forEach(s=>Object.keys(RUOTA180[s]).forEach(a=>{ if(a!=='*' && !(a in PROF_SERIE)) PROF_SERIE[a] = s; })); }
  return PROF_SERIE[prof] || null;
}
function ruotato180(prof, serie){
  const R = RUOTA180[serie || serieDiProfilo(prof) || ''] || {};
  return prof in R ? !!R[prof] : !!R['*'];
}
// trasformazione SVG del tracciato DXF nel riquadro (bx,by,bw,bh): normale (y del DXF verso l'alto) o ruotata di 180°
function trasfDxf(dx, bx, by, bw, bh, sc, rot){
  return rot ? `translate(${bx+bw},${by}) scale(${-sc},${sc}) translate(${-dx.x},${-dx.y})`
             : `translate(${bx},${by+bh}) scale(${sc},${-sc}) translate(${-dx.x},${-dx.y})`;
}

// ---------- libreria operativa: definizioni delle lavorazioni per serie, con eccezioni per profilo ----------"""),
    # sezione per faccia: parametro rot
    ("function sezioneFacciaSvg(f, col, lav, maxY, prof, S){\n  S = S||104; const mg=10, a=S-2*mg;",
     "function sezioneFacciaSvg(f, col, lav, maxY, prof, S, rot){\n  S = S||104; const mg=10, a=S-2*mg; if(rot===undefined) rot = ruotato180(prof);"),
    ("    disegno = `<g transform=\"translate(${bx},${by+bhd}) scale(${sc},${-sc}) translate(${-dx.x},${-dx.y})\">\n      <path d=\"${dx.d}\" fill=\"none\" stroke=\"#5C6B76\" stroke-width=\"${(0.9/sc).toFixed(2)}\"/></g>`;\n    const c = dx.cam || {x:dx.x,y:dx.y,w:dx.w,h:dx.h};\n    cam = { L: bx+(c.x-dx.x)*sc, R: bx+(c.x-dx.x+c.w)*sc,\n            T: by+bhd-(c.y-dx.y+c.h)*sc, B: by+bhd-(c.y-dx.y)*sc };",
     "    disegno = `<g transform=\"${trasfDxf(dx, bx, by, bwd, bhd, sc, rot)}\">\n      <path d=\"${dx.d}\" fill=\"none\" stroke=\"#5C6B76\" stroke-width=\"${(0.9/sc).toFixed(2)}\"/></g>`;\n    const c = dx.cam || {x:dx.x,y:dx.y,w:dx.w,h:dx.h};\n    cam = rot ? { L: bx+bwd-(c.x-dx.x+c.w)*sc, R: bx+bwd-(c.x-dx.x)*sc, T: by+(c.y-dx.y)*sc, B: by+(c.y-dx.y+c.h)*sc }\n              : { L: bx+(c.x-dx.x)*sc, R: bx+(c.x-dx.x+c.w)*sc, T: by+bhd-(c.y-dx.y+c.h)*sc, B: by+bhd-(c.y-dx.y)*sc };"),
    ("    <text x=\"${S/2}\" y=\"${S-1}\" font-size=\"8\" fill=\"#5C6B76\" text-anchor=\"middle\">${prof||''} · F${f}</text>",
     "    <text x=\"${S/2}\" y=\"${S-1}\" font-size=\"8\" fill=\"#5C6B76\" text-anchor=\"middle\">${prof||''} · F${f}${rot?' · ruotato 180°':''}</text>"),
    # schema pezzo: orientamento dal profilo/serie del pezzo
    ("        ${sezioneFacciaSvg(f, col, lav, maxY, p.art)}", "        ${sezioneFacciaSvg(f, col, lav, maxY, p.art, undefined, ruotato180(p.art, p.serie))}"),
    # anteprima libreria
    ("  return sezioneFacciaSvg(ff, FCOL[ff]||'#BE1622', [{y:d.y, v1:d.v1, v2:d.v2}], Math.abs(d.y)||40, prof, 150) +",
     "  return sezioneFacciaSvg(ff, FCOL[ff]||'#BE1622', [{y:d.y, v1:d.v1, v2:d.v2}], Math.abs(d.y)||40, prof, 150, ruotato180(prof, serie)) +"),
    # mini-sezione (composta)
    ("      <g transform=\"translate(${bx},${by+bh}) scale(${sc},${-sc}) translate(${-dx.x},${-dx.y})\">\n        <path d=\"${dx.d}\" fill=\"none\" stroke=\"#5C6B76\" stroke-width=\"${(0.9/sc).toFixed(2)}\"/></g>\n    </svg>\n    <div style=\"font-size:.68rem\"><b class=\"num\">${prof}</b> — ${titolo}</div>",
     "      <g transform=\"${trasfDxf(dx, bx, by, bw, bh, sc, ruotato180(prof))}\">\n        <path d=\"${dx.d}\" fill=\"none\" stroke=\"#5C6B76\" stroke-width=\"${(0.9/sc).toFixed(2)}\"/></g>\n    </svg>\n    <div style=\"font-size:.68rem\"><b class=\"num\">${prof}</b> — ${titolo}${ruotato180(prof)?' · ruotato 180°':''}</div>"),
    # scheda sezione
    ("      <path d=\"${dxs.d}\" fill=\"none\" stroke=\"#1B2328\" stroke-width=\"${(0.9/sc).toFixed(2)}\"/></svg>\n      <div class=\"num\" style=\"font-size:.7rem\"><b>${cod}</b> · ${a.w}×${a.h}</div>",
     "      <g transform=\"${ruotato180(cod)?`rotate(180 ${(dxs.w/2).toFixed(1)} ${(dxs.h/2).toFixed(1)})`:''}\"><path d=\"${dxs.d}\" fill=\"none\" stroke=\"#1B2328\" stroke-width=\"${(0.9/sc).toFixed(2)}\"/></g></svg>\n      <div class=\"num\" style=\"font-size:.7rem\"><b>${cod}</b> · ${a.w}×${a.h}${ruotato180(cod)?' · ruotato 180°':''}</div>"),
    # UI nella pagina libreria: stato dei controlli + listener
    ("  const serie = sel.value; const S = LAV_DEF[serie]||{}; const prof = profiliSerie(serie);",
     """  const serie = sel.value; const S = LAV_DEF[serie]||{}; const prof = profiliSerie(serie);
  const R = RUOTA180[serie]||{}; const chk = $('#lib-ruota'), ecc = $('#lib-ruota-ecc');
  if(chk){ chk.checked = !!R['*']; ecc.value = Object.keys(R).filter(k=>k!=='*' && !!R[k]!==!!R['*']).join(', '); }"""),
    ("  tb.querySelectorAll('[data-prev]').forEach(s=>s.addEventListener('change', ()=>{ profiloAnteprima(serie, s.dataset.prev, s.value); aggiornaAnteprimeLav(serie); }));",
     """  tb.querySelectorAll('[data-prev]').forEach(s=>s.addEventListener('change', ()=>{ profiloAnteprima(serie, s.dataset.prev, s.value); aggiornaAnteprimeLav(serie); }));
  if(chk && !chk.dataset.pronto){ chk.dataset.pronto = '1';
    const leggi = ()=>{ const s = $('#lib-serie').value; const base = $('#lib-ruota').checked; const o = {'*': base};
      $('#lib-ruota-ecc').value.split(/[;,\\s]+/).map(x=>x.trim()).filter(Boolean).forEach(a=>{ o[a] = !base; });
      RUOTA180[s] = o; PROF_SERIE = null; salvaRuota180(); aggiornaAnteprimeLav(s); };
    chk.addEventListener('change', leggi); ecc.addEventListener('change', leggi);
    $('#btn-lib-ruota-lav').addEventListener('click', ()=>{ const s = $('#lib-serie').value;
      if(!confirm(`Scambiare le facce di tutte le lavorazioni della serie ${s} (F1↔F4, F2↔F3, Y invariata)? L'operazione è reversibile: ripetendola si torna indietro.`)) return;
      const SW = {'1':'4','4':'1','2':'3','3':'2'}; const D = LAV_DEF[s]||{};
      Object.keys(D).forEach(k=>{ if(k.startsWith('@')) Object.values(D[k]).forEach(o=>{ if(o.f) o.f = SW[String(o.f)]||o.f; }); else if(D[k].f) D[k].f = SW[String(D[k].f)]||D[k].f; });
      salvaLavDef(); disegnaLavDef(); });
  }"""),
])
patch(R/'src'/'app_template.html', [
    ("      <div style=\"overflow-x:auto;margin-bottom:1rem\"><table id=\"tab-lavdef\" style=\"min-width:1380px\">",
     """      <div style="margin:.3rem 0 .6rem; padding:.45rem .6rem; background:#F5F7F9; border:1px solid var(--linea); font-size:.8rem">
        <b>Orientamento in macchina</b> — <label style="display:inline; font-size:inherit; color:inherit"><input type="checkbox" id="lib-ruota" style="width:auto; vertical-align:middle"> profili caricati <b>ruotati di 180°</b> rispetto al disegno DXF (tutta la serie)</label>
        &nbsp; eccezioni (profili con orientamento opposto): <input id="lib-ruota-ecc" placeholder="es. COR-5600, COR-7561" style="width:18rem; display:inline; padding:.2rem .4rem">
        &nbsp; <button class="spoglio" id="btn-lib-ruota-lav" style="font-size:.72rem" title="Applica la rotazione anche alle lavorazioni della serie: F1↔F4, F2↔F3, Y invariata">scambia le facce delle lavorazioni (F1↔F4, F2↔F3)</button>
        <div class="nota-piccola" style="margin-top:.25rem">La rotazione cambia solo i disegni (sezioni, schemi pezzo): mostra la barra come sta in macchina. Le facce e le Y in tabella restano quelle del job; usa il pulsante per scambiarle in blocco, oppure correggile riga per riga guardando la sezione.</div>
      </div>
      <div style="overflow-x:auto;margin-bottom:1rem"><table id="tab-lavdef" style="min-width:1380px">"""),
])
patch(R/'tools'/'build_cor80.py', [
    ("    'drain': drain, 'libreria': libreria, 'lav_def': lav_def,",
     "    'drain': drain, 'libreria': libreria, 'lav_def': lav_def,\n    'ruota180': {SERIE: {'*': True}},   # barre caricate ruotate di 180° rispetto ai DXF Cortizo (richiesta 10/09/2026): agisce sui disegni"),
])
print('patch 7e OK')
