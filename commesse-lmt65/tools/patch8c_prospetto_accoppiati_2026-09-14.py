#!/usr/bin/env python3
"""Patch 8c (14/09/2026): prospetto del costruttore con giunti "raddoppio" (telai accoppiati).
Le celle adiacenti a un giunto R vengono arretrate della larghezza dello stipite (come sul perimetro), non del mezzo
montante T; i due stipiti accoppiati sono disegnati separati da una linea di giunzione. Il serramento risulta
graficamente diviso in unità distinte, come nella distinta (-U1/-U2, -O1/-O2)."""
import pathlib
P = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'app_logic.js'
s = P.read_text(encoding='utf-8')
def sost(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)
sost("      const x0=x*s+(c===0?t:m/2), y0=y*s+(r===0?t:m/2);\n      const w=ws[c]*s-(c===0?t:m/2)-(c===ws.length-1?t:m/2);\n      const h=hs[r]*s-(r===0?t:m/2)-(r===hs.length-1?t:m/2);",
     "      const iSx = c===0?t:(giunte[c-1]==='R'?t+1:m/2), iDx = c===ws.length-1?t:(giunte[c]==='R'?t+1:m/2);   // arretramento: stipite (t) o mezzo T (m/2)\n"
     "      const iSu = r===0?t:(giunteO[r-1]==='R'?t+1:m/2), iGiu = r===hs.length-1?t:(giunteO[r]==='R'?t+1:m/2);\n"
     "      const x0=x*s+iSx, y0=y*s+iSu;\n      const w=ws[c]*s-iSx-iDx;\n      const h=hs[r]*s-iSu-iGiu;")
sost("    if(giunte[c]==='R')\n      seg += `<rect x=\"${ax*s-t-1}\" y=\"0\" width=\"${t}\" height=\"${A}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>\n              <rect x=\"${ax*s+1}\" y=\"0\" width=\"${t}\" height=\"${A}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>`;",
     "    if(giunte[c]==='R')\n      seg += `<rect x=\"${ax*s-t-1}\" y=\"0\" width=\"${t}\" height=\"${A}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>\n              <rect x=\"${ax*s+1}\" y=\"0\" width=\"${t}\" height=\"${A}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>\n"
     "              <line x1=\"${ax*s}\" y1=\"0\" x2=\"${ax*s}\" y2=\"${A}\" stroke=\"#1B2328\" stroke-width=\"1.2\" stroke-dasharray=\"3 2\"/>`;")
sost("    if(giunteO[r]==='R')\n      seg += `<rect x=\"0\" y=\"${ay*s-t-1}\" width=\"${W}\" height=\"${t}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>\n              <rect x=\"0\" y=\"${ay*s+1}\" width=\"${W}\" height=\"${t}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>`;",
     "    if(giunteO[r]==='R')\n      seg += `<rect x=\"0\" y=\"${ay*s-t-1}\" width=\"${W}\" height=\"${t}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>\n              <rect x=\"0\" y=\"${ay*s+1}\" width=\"${W}\" height=\"${t}\" fill=\"#C9CFD4\" stroke=\"#1B2328\"/>\n"
     "              <line x1=\"0\" y1=\"${ay*s}\" x2=\"${W}\" y2=\"${ay*s}\" stroke=\"#1B2328\" stroke-width=\"1.2\" stroke-dasharray=\"3 2\"/>`;")
P.write_text(s, encoding='utf-8'); print('patch 8c OK')
