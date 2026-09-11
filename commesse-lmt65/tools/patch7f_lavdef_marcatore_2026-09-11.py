#!/usr/bin/env python3
"""Patch 7f (11/09/2026): tracciabilità delle modifiche di serie nella libreria operativa.
Una lavorazione i cui valori di serie (w, v1, v2, y, z, f, ut) differiscono da quelli di consegna
(dati interni + dati_serie.js, senza la copia del browser) porta " [lib.<serie>]" nella descrizione,
come già " [lib.<articolo>]" per le eccezioni per profilo."""
import pathlib
P = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'app_logic.js'
s = P.read_text(encoding='utf-8')
def sost(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)
sost("function costruisciLavDef(){\n", "function costruisciLavDef(senzaLocale){\n")
sost("  try{ const s = localStorage.getItem('lav_def'); if(s) fondi(out, JSON.parse(s)); }catch(e){}\n  return out;\n}\nlet LAV_DEF = costruisciLavDef();",
     "  if(!senzaLocale){ try{ const s = localStorage.getItem('lav_def'); if(s) fondi(out, JSON.parse(s)); }catch(e){} }\n  return out;\n}\nconst LAV_DEF_ORIG = costruisciLavDef(true);   // valori di consegna, per marcare le modifiche fatte nel programma\nlet LAV_DEF = costruisciLavDef();")
sost("  const d = Object.assign({}, base, ov||{});\n  return {w:d.w||'#0',",
     "  const d = Object.assign({}, base, ov||{});\n  const o = (LAV_DEF_ORIG[serie]||{})[chiave] || (LAV_DEF_ORIG.C75S||{})[chiave] || null;\n  const mod = !!o && ['w','v1','v2','y','z','f','ut'].some(k=>String(base[k]==null?'':base[k])!==String(o[k]==null?'':o[k]));\n  return {w:d.w||'#0',")
sost("descr:(d.descr||chiave) + (ov ? ` [lib.${art}]` : '')};", "descr:(d.descr||chiave) + (ov ? ` [lib.${art}]` : (mod ? ` [lib.${serie}]` : ''))};")
P.write_text(s, encoding='utf-8'); print('patch 7f OK')
