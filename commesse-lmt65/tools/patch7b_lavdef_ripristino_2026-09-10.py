#!/usr/bin/env python3
"""Patch 7b (10/09/2026): il ripristino della libreria operativa deve ripartire dai DATI originali.
salvaLavDef() sovrascriveva DATI.lav_def con l'oggetto modificato, quindi ripristinaLavDef() lo riassorbiva.
Si congela una copia immutabile (LAV_DEF_DATI) alla partenza e costruisciLavDef() legge quella."""
import pathlib
P = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'app_logic.js'
s = P.read_text(encoding='utf-8')
def sost(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:60], s.count(old))
    s = s.replace(old, new)
sost("function costruisciLavDef(){\n  const clone = o=>JSON.parse(JSON.stringify(o)); const out = {};",
     "const LAV_DEF_DATI = JSON.parse(JSON.stringify(DATI.lav_def||{}));   // copia immutabile dei DATI di partenza (dati_*.json + dati_serie.js)\n"
     "function costruisciLavDef(){\n  const clone = o=>JSON.parse(JSON.stringify(o)); const out = {};")
sost("  fondi(out, DATI.lav_def);\n", "  fondi(out, LAV_DEF_DATI);\n")
P.write_text(s, encoding='utf-8'); print('patch 7b OK')
