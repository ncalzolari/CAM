#!/usr/bin/env python3
"""Patch 7c (10/09/2026): layout della tabella "Definizioni delle lavorazioni" (selettori W/Faccia tagliati,
descrizione troncata, "+ profilo" a capo)."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[1]
def patch(path, subs):
    s = path.read_text(encoding='utf-8')
    for old, new in subs:
        assert s.count(old) == 1, (path.name, old[:60], s.count(old))
        s = s.replace(old, new)
    path.write_text(encoding='utf-8', data=s)
patch(R/'src'/'app_template.html', [
    ('<table id="tab-lavdef" style="min-width:1000px">', '<table id="tab-lavdef" style="min-width:1180px">'),
    ('  #m-celle select{font-size:.82rem}',
     '  #m-celle select{font-size:.82rem}\n'
     '  #tab-lavdef td{padding:.35rem .3rem; vertical-align:middle; white-space:nowrap}\n'
     '  #tab-lavdef td:first-child{white-space:normal; min-width:11rem}\n'
     '  #tab-lavdef input,#tab-lavdef select{padding:.35rem .4rem; width:auto}\n'
     '  #tab-lavdef select{min-width:5.2rem}\n'
     '  #tab-lavdef button{white-space:nowrap}'),
])
patch(R/'src'/'app_logic.js', [
    ("    const w = campo==='descr' ? '15rem' : '4.6rem';", "    const w = campo==='descr' ? '22rem' : '4.4rem';"),
    ("<option value=\"#0\" ${v==='#0'?'selected':''}>#0 foro</option><option value=\"#1\" ${v==='#1'?'selected':''}>#1 asola</option>",
     "<option value=\"#0\" ${v==='#0'?'selected':''}>#0 foro</option><option value=\"#1\" ${v==='#1'?'selected':''}>#1 asola</option>"),
])
print('patch 7c OK')
