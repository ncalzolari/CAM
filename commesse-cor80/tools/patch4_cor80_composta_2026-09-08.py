# Patch 4 (08/09/2026): costruttore a griglia per la serie COR80 — generalizzazioni dell'editor matrice. Assert sulle occorrenze.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'src', 'app_logic.js')
js = open(JS, encoding='utf-8').read()
def rep(old, new, n=1):
    global js
    c = js.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:70]!r}'
    js = js.replace(old, new)

# 1. composta = ogni tipologia con forma M (non solo gli id C75S/C82S)
rep("function isComposta(){ return $('#r-tip').value==='C75S_COMPOSTA' || $('#r-tip').value==='C82S_COMPOSTA'; }",
    "function isComposta(){ const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value); return !!(t && t.forma==='M'); }\n"
    "function compostaSenzaPF(){ const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value); return !!(t && t.composta_cor80); }   // COR80: niente celle portafinestra")
rep("  if(t.id==='C75S_COMPOSTA' || t.id==='C82S_COMPOSTA'){\n    if(t.serie==='C82S-CS'){",
    "  if(t.forma==='M'){\n    if(t.serie==='C82S-CS'){")
# 2. celle: niente PF dove la serie non le prevede
rep("      if(isPF(v) && r!==matC.rows-1) v='F';    // portefinestre solo nella riga inferiore",
    "      if(isPF(v) && (r!==matC.rows-1 || compostaSenzaPF())) v='F';    // portefinestre solo nella riga inferiore (mai in COR80)")
rep("  const lista = (r===matC.rows-1) ? CICLO_PF : CICLO;",
    "  const lista = (r===matC.rows-1 && !compostaSenzaPF()) ? CICLO_PF : CICLO;")
# 3. sezioni dei profili T
rep("  const c82 = ($('#r-serie').value||'').startsWith('C82');\n  box.innerHTML = c82",
    "  const tC = DATI.tipologie.find(x=>x.id===$('#r-tip').value);\n"
    "  if(tC && tC.composta_cor80){ box.innerHTML = miniSezione(tC.composta_cor80.trav,'montanti e traversi T') + miniSezione(tC.composta_cor80.comp,'complemento telaio (celle apribili)'); return; }\n"
    "  const c82 = ($('#r-serie').value||'').startsWith('C82');\n  box.innerHTML = c82")
open(JS, 'w', encoding='utf-8').write(js); print('patch 4 applicata')
