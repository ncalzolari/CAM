#!/usr/bin/env python3
"""Patch 7g (13/09/2026): nel riquadro "Orientamento in macchina" della libreria si cita la convenzione
DXF di Frame Project Pro / CAMplus (manuale CAMplus 2.0, cap. 15), come regola per decidere la rotazione."""
import pathlib
P = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'app_template.html'
s = P.read_text(encoding='utf-8')
old = "La rotazione cambia solo i disegni (sezioni, schemi pezzo): mostra la barra come sta in macchina."
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "Regola di riferimento (manuale CAMplus cap. 15): i DXF per Frame Project Pro sono orientati con <b>vetro in alto e lato freddo a sinistra</b>; un DXF disegnato al contrario (es. Cortizo: vetro in basso, freddo a destra) va ruotato di 180°. " + old)
P.write_text(s, encoding='utf-8'); print('patch 7g OK')
