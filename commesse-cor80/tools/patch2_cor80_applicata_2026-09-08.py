# Patch 2 (08/09/2026): serie Cortizo COR 80 Evolution — generalizzazioni in app_logic.js / app_template.html.
# Applicata una volta ai sorgenti (tenuta come documentazione delle modifiche). Ogni sostituzione ha un assert
# sul numero di occorrenze. Comportamento C75S/C82S/D67/D77 invariato (regress.js identico).
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'src', 'app_logic.js'); TPL = os.path.join(ROOT, 'src', 'app_template.html')
js = open(JS, encoding='utf-8').read(); tpl = open(TPL, encoding='utf-8').read()
def rep(old, new, n=1):
    global js
    c = js.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:70]!r}'
    js = js.replace(old, new)

# 1. helper di serie: in vista (FX + ferramenta Maico) e selettori profili per tipologia
rep("function isPorta(serie){ return !!(SERIE_INFO[serie] && SERIE_INFO[serie].porta); }",
    "function isPorta(serie){ return !!(SERIE_INFO[serie] && SERIE_INFO[serie].porta); }\n"
    "function serieInVista(serie){ return serie==='C75S' || !!(SERIE_INFO[serie] && SERIE_INFO[serie].in_vista); }   // FX + ferramenta Maico in vista\n"
    "function tipProfili(serie){ return !!(SERIE_INFO[serie] && SERIE_INFO[serie].tip_profili); }                    // telaio/anta/vetro definiti dalla tipologia (come le porte)")
rep("  const inVista = (serie||'C75S')==='C75S';\n  return { giu: dren, tutti: dren && inVista };",
    "  const inVista = serieInVista(serie||'C75S');\n  return { giu: dren, tutti: dren && inVista };")
rep("          const inVista = t.serie==='C75S';\n          const ferrAR = ['1','2','P1','P2'].includes(t.forma);   // ferramenta A-R solo su battenti\n          const conStulp = r.battuta==='stulp' || /stulp/i.test(t.nome||'');",
    "          const inVista = serieInVista(t.serie);\n          const ferrAR = ['1','2','P1','P2'].includes(t.forma) && t.ferr!==false;   // ferramenta A-R solo su battenti (ferr:false = anta a scomparsa)\n          const conStulp = r.battuta==='stulp' || /stulp/i.test(t.nome||'') || t.stulp===true;")

# 2. tavole di vetrazione: chiave esplicita (tipologia/fermavetro) e prefisso generico tav[A-Z]
rep("function tavolaVetro(codProfilo){\n  for(const k of Object.keys(DATI.vetrazione)) if(/^tavD/.test(k) && DATI.vetrazione[k].profili.includes(codProfilo)) return DATI.vetrazione[k];",
    "function tavolaVetro(codProfilo, key){\n  if(key && DATI.vetrazione[key]) return DATI.vetrazione[key];\n  for(const k of Object.keys(DATI.vetrazione)) if(/^tav[A-Z]/.test(k) && DATI.vetrazione[k].profili.includes(codProfilo)) return DATI.vetrazione[k];")
rep("function risolviVetro(mm, codProfilo){\n  const tav = tavolaVetro(codProfilo);",
    "function risolviVetro(mm, codProfilo, key){\n  const tav = tavolaVetro(codProfilo, key);")

# 3. altezza maniglia: formula anta della tipologia (COR80: H-54, H-73.6, H1-32.6)
rep("  const H = parseFloat($('#r-h').value)||1400; const hAnta = H-43;",
    "  const H = parseFloat($('#r-h').value)||1400, L = parseFloat($('#r-l').value)||1200;\n  const hAnta = (tP && tP.anta_h) ? (valuta(tP.anta_h, L, H, {h2: parseFloat($('#r-h2').value)||0}) || H-43) : H-43;")

# 4. selettori profili per tipologia (come porte) + etichetta variante telaio + vetro di default della serie
rep("  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); if(isPorta($('#r-serie').value)) aggiornaSelettoriProfili(); else aggiornaSezioni();});",
    "  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); if(isPorta($('#r-serie').value) || tipProfili($('#r-serie').value)) aggiornaSelettoriProfili(); else aggiornaSezioni();});")
rep("  const s = $('#r-serie').value, v = DATI.varianti[s];\n  if(isPorta(s)){",
    "  const s = $('#r-serie').value, v = DATI.varianti[s];\n  if(isPorta(s) || tipProfili(s)){")
rep("(ala? `<option value=\"ala\">${ala} — con ala 32 mm</option>` : '');",
    "(ala? `<option value=\"ala\">${ala} — ${vp.nome_ala||'con ala 32 mm'}</option>` : '');")
rep("    const tav = tavolaVetro(t.anta_rif||'');\n    const spess = Object.keys(tav.righe).sort((a,b)=>a-b);\n    const def = spess.includes('30')? '30' : spess.includes('46')? '46' : spess[0];",
    "    const tav = tavolaVetro(t.anta_rif||'', t.vetro_tav);\n    const spess = Object.keys(tav.righe).sort((a,b)=>a-b);\n    const vd = (SERIE_INFO[s]||{}).vetro_default;\n    const def = vd ? (spess.includes(vd) ? vd : spess.reduce((a,b)=>Math.abs(b-vd)<Math.abs(a-vd)?b:a)) : spess.includes('30')? '30' : spess.includes('46')? '46' : spess[0];")

# 5. aggiornaSezioni: H2 anche per finestre con fisso inferiore; pannello sezioni/vetro per serie a tipologia
rep("  const apribile = t && ['1','P1','1F','2','P2'].includes(t.forma);\n  $('#box-blocal').style.display = (t && !porta && ['1','1F','2','P1','P2','M'].includes(t.forma)) ? 'block' : 'none';",
    "  const tipP = t && tipProfili(t.serie);\n  const apribile = t && ['1','P1','1F','2','P2'].includes(t.forma) && t.ferr!==false;\n  $('#box-blocal').style.display = (t && !porta && !tipP && ['1','1F','2','P1','P2','M'].includes(t.forma)) ? 'block' : 'none';")
rep("  if(bt && porta) bt.style.display = 'none';\n  const bh2 = $('#box-h2'); if(bh2) bh2.style.display = (porta && t.sopraluce) ? 'block' : 'none';",
    "  if(bt && (porta || tipP)) bt.style.display = 'none';\n  const bh2 = $('#box-h2'); if(bh2) bh2.style.display = (t && t.sopraluce) ? 'block' : 'none';")
rep("  if(porta){\n    const vp = DATI.varianti_porte[t.serie], telP = t.telaio_rif || vp.telaio_int;",
    "  if(porta || tipP){\n    const vp = DATI.varianti_porte[t.serie], telP = t.telaio_rif || vp.telaio_int;")
rep("    const mmP = $('#r-vetro').value, rP = risolviVetro(mmP, t.anta_rif);\n    $('#info-vetro').innerHTML = `<div style=\"font-size:.72rem;line-height:1.5\"><b>Vetro ${mmP} mm</b> (tav. 7.0${t.serie==='D67'?'4':'5'})<br>",
    "    const mmP = $('#r-vetro').value, rP = risolviVetro(mmP, t.anta_rif, t.vetro_tav);\n    $('#info-vetro').innerHTML = `<div style=\"font-size:.72rem;line-height:1.5\"><b>Vetro ${mmP} mm</b> (${porta ? 'tav. 7.0'+(t.serie==='D67'?'4':'5') : 'tavola '+(t.vetro_tav||'')})<br>")
rep("      <span style=\"color:var(--acciaio)\">squadrato ${rP&&rP.fv_sq?rP.fv_sq:'—'} · tubolare ${rP&&rP.fv_tub?rP.fv_tub:'—'} · clips ${rP&&rP.fv_clip?rP.fv_clip:'—'}</span></div>`;",
    "      ${porta ? `<span style=\"color:var(--acciaio)\">squadrato ${rP&&rP.fv_sq?rP.fv_sq:'—'} · tubolare ${rP&&rP.fv_tub?rP.fv_tub:'—'} · clips ${rP&&rP.fv_clip?rP.fv_clip:'—'}</span>`\n              : `<span style=\"color:var(--acciaio)\">guarn. esterna ${rP&&rP.ext?rP.ext:'—'} · fermavetro ${rP&&rP.B?rP.B:'—'} mm</span>`}</div>`;")

# 6. leggiRigaCorrente: H2 per ogni tipologia con sopraluce/fisso inferiore
rep("  const h2 = (t.porta && t.sopraluce) ? (parseFloat(String($('#r-h2').value).replace(',','.'))||null) : null;\n  if(t.porta && t.sopraluce && !(h2>50 && h2<H-300)){\n    if(!quiet) $('#esito').textContent = 'Porta con sopraluce: inserisci H2 (altezza sopraluce, mm) tra 50 e H-300.';",
    "  const h2 = t.sopraluce ? (parseFloat(String($('#r-h2').value).replace(',','.'))||null) : null;\n  if(t.sopraluce && !(h2>50 && h2<H-300)){\n    if(!quiet) $('#esito').textContent = (t.porta ? 'Porta con sopraluce: inserisci H2 (altezza sopraluce, mm)' : 'Inserisci H2 (altezza del fisso inferiore, mm)') + ' tra 50 e H-300.';")

# 7. motore di calcolo: fermavetri e guarnizione interna vetro dalla tavola della tipologia
rep("          const codRif = t.porta ? (t.anta_rif||r.anta) : (suFisso ? (r.telaio||'B23008C') : (r.anta||'B23122C'));\n          const ris = risolviVetro(r.vetro, codRif);",
    "          const codRif = t.porta ? (t.anta_rif||r.anta) : (t.anta_rif ? (suFisso && t.telaio_rif ? t.telaio_rif : t.anta_rif) : (suFisso ? (r.telaio||'B23008C') : (r.anta||'B23122C')));\n          const ris = risolviVetro(r.vetro, codRif, suFisso ? p.tav : (p.tav||t.vetro_tav));")
rep("        if(/^809119/.test(g.art) || (t.porta && /^interna vetro/i.test(g.desc))){  // guarnizione interna vetro -> dalla tavola di vetrazione\n          const ris = risolviVetro(r.vetro, t.porta ? (t.anta_rif||r.anta) : (r.anta||'B23122C'));",
    "        if(/^809119/.test(g.art) || (t.porta && /^interna vetro/i.test(g.desc)) || g.gv===true){  // guarnizione interna vetro -> dalla tavola di vetrazione\n          const ris = risolviVetro(r.vetro, (t.porta||t.anta_rif) ? (t.anta_rif||r.anta) : (r.anta||'B23122C'), t.vetro_tav);")

# 8. drenaggi telaio: bordo/passo dal catalogo (COR80: 75 / <=1000) e tipo per tipologia (ala 39 / ala 21)
rep("            const dl = inVista ? lavDrenTelaioFP(mm, t.serie) : posizioniDrenaggio(mm).map(x=>lavDrenaggio(t.serie,'telaio',x));",
    "            const dT = (DRAIN[t.serie]||{})[t.dren_telaio||'telaio'] || {};\n            const dl = dT.bordo ? posizioniDrenaggio(mm, dT.bordo, dT.passo||450).map(x=>lavDrenaggio(t.serie, t.dren_telaio||'telaio', x))\n                     : inVista ? lavDrenTelaioFP(mm, t.serie) : posizioniDrenaggio(mm).map(x=>lavDrenaggio(t.serie,'telaio',x));")

# 9. ferramenta Maico: formule anta della tipologia (default C75S: H-43 / L-43 / L/2-24)
rep("valuta('H-43', r.L, r.H)", "valuta(t.anta_h||'H-43', r.L, r.H, r)", 2)
rep("valuta('L-43', r.L, r.H)", "valuta(t.anta_l||'L-43', r.L, r.H, r)", 2)
rep("valuta('L/2-24', r.L, r.H)", "valuta(t.anta_l2||'L/2-24', r.L, r.H, r)")

# 10. drenaggi/aerazioni anta: posizione e tipo dalla tipologia
rep("            [168, Math.round((mm-168)*10)/10].forEach(x=>lav.push(lavDrenaggio(t.serie,'antaTrav',x)));",
    "            const xd = t.dren_x||168;\n            [xd, Math.round((mm-xd)*10)/10].forEach(x=>lav.push(lavDrenaggio(t.serie, t.dren_anta||'antaTrav', x)));")
rep("            lav.push(lavDrenaggio(t.serie,'antaTrav', xSf));", "            lav.push(lavDrenaggio(t.serie, t.dren_anta||'antaTrav', xSf));")
rep("            lav.push(lavDrenaggio(t.serie,'antaMont', (k%2===0)? 218 : Math.round((mm-218)*10)/10));",
    "            { const xm = t.dren_x||218; lav.push(lavDrenaggio(t.serie,'antaMont', (k%2===0)? xm : Math.round((mm-xm)*10)/10)); }")

# 11. serie senza riscontro di produzione: tutte le lavorazioni marcate [DA TARARE]
rep("          pezzi.push({art, desc:p.desc, mm:Math.round(mm*10)/10, al, ar, unita,",
    "          if(SERIE_INFO[t.serie] && SERIE_INFO[t.serie].da_tarare) lav.forEach(l=>{ if(!/DA TARARE/.test(l.descr)) l.descr += ' [DA TARARE]'; });\n          pezzi.push({art, desc:p.desc, mm:Math.round(mm*10)/10, al, ar, unita,")

# 12. template: etichetta H2
old = "H2 — altezza sopraluce (mm, da filo esterno telaio)"; new = "H2 — altezza sopraluce / fisso inferiore (mm, da filo esterno telaio)"
assert tpl.count(old) == 1; tpl = tpl.replace(old, new)

open(JS, 'w', encoding='utf-8').write(js); open(TPL, 'w', encoding='utf-8').write(tpl)
print('patch 2 applicata')
