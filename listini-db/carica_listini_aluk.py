#!/usr/bin/env python3
"""Carica i listini AluK (PDF) nel database listini.sqlite e nei CSV di listini-db/csv/.

Uso:  python3 carica_listini_aluk.py [--profili Listino_profili_260615.pdf] [--accessori Listino_Accessori_AluK_260615.pdf] [--c75s Listino_C75S_C82SCS_260615.pdf]
Serve pymupdf (pip install pymupdf). Rilanciabile: ogni listino (fornitore+tipo+decorrenza) viene sostituito, non duplicato.

Tabelle: listini, accessori, profili_serie, finiture, addebiti, colori, profili_articoli, serie_app, sconti  +  viste v_accessori, v_profili, v_profili_articoli (prezzi netti).
"""
import argparse, csv, json, os, re, sqlite3, sys, datetime
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'listini.sqlite'); CSVDIR = os.path.join(HERE, 'csv')
FORN = 'AluK'
SCONTI = [('AluK', 'profili', 0.38), ('AluK', 'accessori', 0.20)]   # sconti concordati (settembre 2026)
# serie del programma commesse -> serie commerciale del listino profili (articolo di fatturazione = serie + aggregazione colore)
SERIE_APP = [('D67', 'AluK', '312', 'IWG 67ID = PR.ALL.TT D67 (la 311 "67ID" è in esaurimento)'),
             ('D77', 'AluK', '315', 'IWG 77ID = PR.ALL.TT D77 (la 377 "77IW/ID" è in esaurimento)'),
             ('C75S', 'AluK', '333', 'listino C75S/C82S-CS: profili a taglio termico (B23xxx) = 333xx; non isolati (fermavetri N458xx, aggiuntivi) = 108xx; con guarnizione premontata = 182xx — attribuzione per profilo DA CONFERMARE'),
             ('C82S-CS', 'AluK', '333', 'come C75S (stesso listino)'),
             ('COR80', 'Cortizo', None, 'listino Cortizo non caricato')]

num = lambda s: float(s.replace('.', '').replace(',', '.')) if s not in (None, '', '-') else None

def testo(pdf):
    d = pymupdf.open(pdf)
    dec = None
    for p in d:
        m = re.search(r'Decorrenza (\d\d)-(\d\d)-(\d{4})', p.get_text())
        if m: dec = f'{m.group(3)}-{m.group(2)}-{m.group(1)}'; break
    return [[l.strip() for l in p.get_text().split('\n')] for p in d], dec

# ---------------- accessori ----------------
def parse_accessori(pages):
    isCode = lambda s: re.fullmatch(r'[0-9A-Z][0-9A-Z\-]{3,24}', s) and re.search(r'\d', s)   # anche codici numerici (712010) e lunghi (H89306-RAL6005M45P)
    isNum = lambda s: re.fullmatch(r'\d{1,3}(\.\d{3})*,\d+|\d{1,3}(\.\d{3})+|\d+', s)   # anche migliaia senza decimali (2.000)
    rows = []
    for pg, lines in enumerate(pages, 1):
        i = 0
        # codice e descrizione sulla stessa riga (es. 'H89306-RAL6005M45P - CERNIERA DX'): separati prima del parsing
        sp = []
        for j, l in enumerate(lines):
            m = re.match(r'^([0-9A-Z][0-9A-Z\-]{5,24}) (?:- )?(.+)$', l)
            if m and j + 1 < len(lines) and lines[j + 1] in ('PZ', 'CF', 'ML') and isCode(m.group(1)): sp += [m.group(1), m.group(2).strip()]
            else: sp.append(l)
        lines = sp
        while i < len(lines):
            l = lines[i]
            if isCode(l) and i + 3 < len(lines):
                j = i + 1; desc = []
                while j < len(lines) and lines[j] not in ('PZ', 'CF', 'ML') and j < i + 5: desc.append(lines[j]); j += 1
                if j < len(lines) and lines[j] in ('PZ', 'CF', 'ML') and desc:
                    um = lines[j]; k = j + 1; nums = []
                    while k < len(lines) and len(nums) < 4:
                        if isNum(lines[k]): nums.append(lines[k]); k += 1
                        elif lines[k] == '' and len(nums) == 1: nums.append('-'); k += 1   # 'PZ x CF' vuoto (es. V31944L5500)
                        else: break
                    if len(nums) == 4:
                        stato = lines[k] if k < len(lines) and re.match(r'(Attivo|In |Fuori|Sospeso|Non)', lines[k]) else None
                        note = None
                        if stato:
                            k += 1
                            if k < len(lines) and lines[k] and not isCode(lines[k]) and not re.fullmatch(r'\d+(/\d+)?', lines[k]) and not lines[k].startswith('Listino') and not lines[k].startswith('Articolo'):
                                note = lines[k]; k += 1
                        rows.append(dict(codice=l, descrizione=' '.join(desc), um=um, prezzo_listino=num(nums[0]), pz_conf=num(nums[1]),
                                         min_vend=num(nums[2]), prezzo_unitario=num(nums[3]), stato=stato, note=note, pagina=pg))
                        i = k; continue
            i += 1
    return rows

# ---------------- listino C75S / C82S-CS (accessori con imballo + articoli profilo a kg) ----------------
def parse_c75s(pages):
    isCode = lambda s: re.fullmatch(r'[0-9A-Z][0-9A-Z\-]{3,24}', s) and re.search(r'\d', s)
    isNum = lambda s: re.fullmatch(r'\d{1,3}(\.\d{3})*,\d+|\d{1,3}(\.\d{3})+|\d+', s)   # anche migliaia senza decimali (2.000)
    acc, prof = [], []
    for pg, lines in enumerate(pages, 1):
        i = 0
        while i < len(lines):
            l = lines[i]
            if isCode(l) and i + 3 < len(lines):
                j = i + 1; desc = []
                while j < len(lines) and lines[j] not in ('PZ', 'CF', 'ML', 'KG') and j < i + 4: desc.append(lines[j]); j += 1
                if j < len(lines) and lines[j] in ('PZ', 'CF', 'ML', 'KG') and desc:
                    um = lines[j]; k = j + 1; nums = []; nmax = 1 if um == 'KG' else 5   # a kg c'è solo il prezzo: il codice numerico successivo non va letto come numero
                    while k < len(lines) and isNum(lines[k]) and len(nums) < nmax: nums.append(lines[k]); k += 1
                    if um == 'KG' and len(nums) >= 1:
                        prof.append(dict(articolo=l, serie=l[:3], aggregazione=l[3:], descrizione=' '.join(desc), eur_kg=num(nums[0]), pagina=pg)); i = k; continue
                    if um != 'KG' and len(nums) == 5:
                        stato = lines[k] if k < len(lines) and lines[k].startswith('Attivo') else None
                        acc.append(dict(codice=l, descrizione=' '.join(desc), um=um, prezzo_listino=num(nums[0]), pz_conf=num(nums[1]), min_vend=None,
                                        prezzo_unitario=num(nums[4]), stato=stato, note=None, pagina=pg, cf_imballo=num(nums[2]), pz_imballo=num(nums[3])))
                        i = k + (1 if stato else 0); continue
            i += 1
    return acc, prof

# ---------------- profili ----------------
GRUPPI_SERIE = ('Battenti e Porte', 'Scorrevoli', 'Facciate', 'Oscuranti', 'Standard', 'K-VIEW')
SCARTA = ('Serie grezze', 'Serie non isolate', 'Serie Isolate', 'X1A0T', 'Codice', 'Descrizione', 'Note', 'Stato', '€/kg', 'Aggreg.', 'Finiture', 'Con addebiti', 'Senza addebiti', 'Flash d\'Ox.', '[€]')
def parse_profili(pages):
    serie, finiture, addebiti, colori = [], [], [], []
    isPrice = lambda s: re.fullmatch(r'\+? ?\d{1,3},\d\d|-', s)
    # pagine serie (codice a 3 cifre)
    for pg in (2, 3):
        lines = [l for l in pages[pg] if l and l not in SCARTA]
        gruppo = None; i = 0
        while i < len(lines):
            l = lines[i]
            if l in GRUPPI_SERIE: gruppo = l; i += 1; continue
            if re.fullmatch(r'\d{3}', l) and i + 2 < len(lines):
                desc = lines[i + 1]; j = i + 2; note = []; prezzo = None
                while j < len(lines) and not re.fullmatch(r'\d{3}', lines[j]) and lines[j] not in GRUPPI_SERIE:
                    if isPrice(lines[j]) and prezzo is None: prezzo = num(lines[j])
                    else: note.append(lines[j])
                    j += 1
                stato = next((n for n in note if 'Esaurimento' in n), None)
                note = [n for n in note if n != stato]
                if not any(s['codice'] == l for s in serie):
                    serie.append(dict(codice=l, descrizione=desc, gruppo=gruppo, note=' / '.join(note) or None, stato=stato or 'Attivo', eur_kg=prezzo))
                i = j; continue
            i += 1
    # pagine finiture / addebiti (aggregazione a 2 caratteri)
    GR_FIN = ('Verniciati a Cartella', 'Verniciati fuori Cartella', 'Ossidati', 'Note e Maggiorazioni', 'Effetto Legno', 'Bicolore', 'Pretrattamento', 'Addebiti')
    for pg in (4, 5):
        lines = [l for l in pages[pg] if l and l not in SCARTA]
        gruppo = None; i = 0
        while i < len(lines):
            l = lines[i]
            if l in GR_FIN: gruppo = l; i += 1; continue
            if gruppo == 'Addebiti' and re.fullmatch(r'(3\+\+\d\d|\+\+CAMBIOCOL)', l) and i + 2 < len(lines):
                addebiti.append(dict(codice=l, descrizione=lines[i + 1], importo=num(lines[i + 2]))); i += 3; continue
            if gruppo and gruppo != 'Addebiti' and re.fullmatch(r'[0-9A-Z]{2}', l) and i + 1 < len(lines) and not isPrice(lines[i + 1]):
                desc = lines[i + 1]; j = i + 2; note = []; prezzo = None; magg = None
                while j < len(lines) and not re.fullmatch(r'[0-9A-Z]{2}', lines[j]) and lines[j] not in GR_FIN:
                    if isPrice(lines[j]) and prezzo is None and magg is None:
                        if lines[j].startswith('+'): magg = num(lines[j].lstrip('+ '))
                        else: prezzo = num(lines[j])
                    else: note.append(lines[j])
                    j += 1
                finiture.append(dict(aggregazione=l, descrizione=desc, gruppo=gruppo, note=' / '.join(note) or None, eur_kg=prezzo, maggiorazione_eur_kg=magg))
                i = j; continue
            if gruppo == 'Note e Maggiorazioni' or gruppo == 'Pretrattamento':
                # righe descrittive: descrizione, [note], +x,xx
                if not isPrice(l) and i + 1 < len(lines):
                    j = i + 1; note = []; magg = None
                    while j < len(lines) and not isPrice(lines[j]) and lines[j] not in GR_FIN and not re.fullmatch(r'[0-9A-Z]{2}', lines[j]): note.append(lines[j]); j += 1
                    if j < len(lines) and isPrice(lines[j]): magg = num(lines[j].lstrip('+ ')) if lines[j] != '-' else None; j += 1
                    finiture.append(dict(aggregazione=None, descrizione=l, gruppo=gruppo, note=' / '.join(note) or None, eur_kg=None, maggiorazione_eur_kg=magg))
                    i = j; continue
            i += 1
    # pagine colori (codice colore a 6 caratteri)
    sezione = None
    for pg in range(6, len(pages)):
        lines = [l for l in pages[pg] if l]
        i = 0
        while i < len(lines):
            l = lines[i]
            if l.startswith('Elenco colori'): sezione = l; i += 1; continue
            if re.fullmatch(r'\d[0-9A-Z]{5}', l) and i + 2 < len(lines) and re.fullmatch(r'[12]', lines[i + 2]):
                desc, classe = lines[i + 1], lines[i + 2]; sigla = lines[i + 3] if i + 3 < len(lines) else None
                j = i + 4; extra = []
                while j < len(lines) and not (re.fullmatch(r'\d[0-9A-Z]{5}', lines[j]) and j + 2 < len(lines) and re.fullmatch(r'[12]', lines[j + 2])) and not lines[j].startswith('Elenco') and len(extra) < 3 and not lines[j] in ('Codice',):
                    if lines[j] in ('Descrizione', 'Classe', 'Colore', 'documenti', 'monocolore', 'bicolore', 'Passato in cl 2', 'AluK Group SpA'): break
                    extra.append(lines[j]); j += 1
                agg_mono = next((e for e in extra if re.fullmatch(r'[A-Z][A-Z0-9]|\d\d', e) and len(e) == 2 and e != '90'), None)
                agg_bic = next((e for e in extra if e in ('90', '99', '9K', '95')), None)
                altri = [e for e in extra if e not in (agg_mono, agg_bic)]
                colori.append(dict(codice=l, descrizione=desc, classe=int(classe), sigla=sigla, aggregazione=agg_mono, aggregazione_bicolore=agg_bic, codici_collegati=' / '.join(altri) or None, sezione=sezione))
                i = j; continue
            i += 1
    return serie, finiture, addebiti, colori

SCHEMA = """
CREATE TABLE IF NOT EXISTS listini (id INTEGER PRIMARY KEY, fornitore TEXT, tipo TEXT, decorrenza TEXT, file TEXT, caricato_il TEXT, UNIQUE(fornitore, tipo, decorrenza));
CREATE TABLE IF NOT EXISTS accessori (listino_id INTEGER REFERENCES listini(id) ON DELETE CASCADE, codice TEXT, descrizione TEXT, um TEXT, prezzo_listino REAL, pz_conf REAL, min_vend REAL, prezzo_unitario REAL, stato TEXT, note TEXT, pagina INTEGER, cf_imballo REAL, pz_imballo REAL, PRIMARY KEY(listino_id, codice));
CREATE TABLE IF NOT EXISTS profili_articoli (listino_id INTEGER REFERENCES listini(id) ON DELETE CASCADE, articolo TEXT, serie TEXT, aggregazione TEXT, descrizione TEXT, eur_kg REAL, pagina INTEGER, PRIMARY KEY(listino_id, articolo));
CREATE TABLE IF NOT EXISTS profili_serie (listino_id INTEGER REFERENCES listini(id) ON DELETE CASCADE, codice TEXT, descrizione TEXT, gruppo TEXT, note TEXT, stato TEXT, eur_kg REAL, PRIMARY KEY(listino_id, codice));
CREATE TABLE IF NOT EXISTS finiture (listino_id INTEGER REFERENCES listini(id) ON DELETE CASCADE, aggregazione TEXT, descrizione TEXT, gruppo TEXT, note TEXT, eur_kg REAL, maggiorazione_eur_kg REAL);
CREATE TABLE IF NOT EXISTS addebiti (listino_id INTEGER REFERENCES listini(id) ON DELETE CASCADE, codice TEXT, descrizione TEXT, importo REAL);
CREATE TABLE IF NOT EXISTS colori (listino_id INTEGER REFERENCES listini(id) ON DELETE CASCADE, codice TEXT, descrizione TEXT, classe INTEGER, sigla TEXT, aggregazione TEXT, aggregazione_bicolore TEXT, codici_collegati TEXT, sezione TEXT);
CREATE TABLE IF NOT EXISTS sconti (fornitore TEXT, categoria TEXT, sconto REAL, decorrenza TEXT, PRIMARY KEY(fornitore, categoria, decorrenza));
CREATE TABLE IF NOT EXISTS serie_app (serie_app TEXT PRIMARY KEY, fornitore TEXT, serie_listino TEXT, nota TEXT);
CREATE VIEW IF NOT EXISTS v_sconto AS SELECT fornitore, categoria, sconto FROM sconti s WHERE decorrenza = (SELECT MAX(decorrenza) FROM sconti s2 WHERE s2.fornitore=s.fornitore AND s2.categoria=s.categoria);
CREATE VIEW IF NOT EXISTS v_accessori AS
  SELECT l.fornitore, l.tipo AS listino, l.decorrenza, a.codice, a.descrizione, a.um, a.prezzo_listino, a.pz_conf, a.min_vend, a.prezzo_unitario, a.stato, a.note, a.cf_imballo, a.pz_imballo,
         s.sconto, ROUND(a.prezzo_listino*(1-s.sconto), 3) AS prezzo_netto_conf, ROUND(a.prezzo_unitario*(1-s.sconto), 4) AS prezzo_netto_unitario
  FROM accessori a JOIN listini l ON l.id=a.listino_id LEFT JOIN v_sconto s ON s.fornitore=l.fornitore AND s.categoria='accessori'
  WHERE l.decorrenza = (SELECT MAX(decorrenza) FROM listini l2 WHERE l2.fornitore=l.fornitore AND l2.tipo=l.tipo);
CREATE VIEW IF NOT EXISTS v_profili_articoli AS
  SELECT l.fornitore, l.tipo AS listino, l.decorrenza, p.articolo, p.serie, p.aggregazione, p.descrizione, p.eur_kg AS listino_eur_kg, s.sconto, ROUND(p.eur_kg*(1-s.sconto), 4) AS netto_eur_kg
  FROM profili_articoli p JOIN listini l ON l.id=p.listino_id LEFT JOIN v_sconto s ON s.fornitore=l.fornitore AND s.categoria='profili'
  WHERE l.decorrenza = (SELECT MAX(decorrenza) FROM listini l2 WHERE l2.fornitore=l.fornitore AND l2.tipo=l.tipo);
CREATE VIEW IF NOT EXISTS v_profili AS
  SELECT l.fornitore, l.decorrenza, p.codice AS serie, p.descrizione AS serie_descr, p.gruppo, p.stato, p.eur_kg AS grezzo_eur_kg,
         f.aggregazione, f.descrizione AS finitura, f.eur_kg AS finitura_eur_kg,
         ROUND(p.eur_kg + COALESCE(f.eur_kg,0), 2) AS listino_eur_kg, s.sconto,
         ROUND((p.eur_kg + COALESCE(f.eur_kg,0))*(1-s.sconto), 4) AS netto_eur_kg
  FROM profili_serie p JOIN listini l ON l.id=p.listino_id
  LEFT JOIN finiture f ON f.listino_id=p.listino_id AND f.aggregazione IS NOT NULL AND f.eur_kg IS NOT NULL
  LEFT JOIN v_sconto s ON s.fornitore=l.fornitore AND s.categoria='profili'
  WHERE l.decorrenza = (SELECT MAX(decorrenza) FROM listini l2 WHERE l2.fornitore=l.fornitore AND l2.tipo='profili');
"""

def carica(db, fornitore, tipo, decorrenza, file, tabelle):
    cur = db.cursor()
    cur.execute('DELETE FROM listini WHERE fornitore=? AND tipo=? AND decorrenza=?', (fornitore, tipo, decorrenza))
    cur.execute('INSERT INTO listini(fornitore,tipo,decorrenza,file,caricato_il) VALUES(?,?,?,?,?)', (fornitore, tipo, decorrenza, os.path.basename(file), datetime.date.today().isoformat()))
    lid = cur.lastrowid
    for nome, rows in tabelle.items():
        if not rows: continue
        cols = list(rows[0].keys())
        cur.executemany(f'INSERT OR REPLACE INTO {nome}(listino_id,{",".join(cols)}) VALUES(?,{",".join("?"*len(cols))})', [(lid, *[r[c] for c in cols]) for r in rows])
    return lid

def scrivi_csv(nome, rows):
    if not rows: return
    os.makedirs(CSVDIR, exist_ok=True)
    with open(os.path.join(CSVDIR, nome + '.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=';'); w.writeheader(); w.writerows(rows)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--profili', default=os.path.join(HERE, 'Listino_profili_260615.pdf'))
    ap.add_argument('--accessori', default=os.path.join(HERE, 'Listino_Accessori_AluK_260615.pdf'))
    ap.add_argument('--c75s', default=os.path.join(HERE, 'Listino_C75S_C82SCS_260615.pdf'))
    a = ap.parse_args()
    db = sqlite3.connect(DB); db.execute('PRAGMA foreign_keys=ON'); db.executescript(SCHEMA)
    for col in ('cf_imballo', 'pz_imballo'):   # migrazione db creati prima del listino C75S
        try: db.execute(f'ALTER TABLE accessori ADD COLUMN {col} REAL'); db.execute('DROP VIEW IF EXISTS v_accessori'); db.executescript(SCHEMA)
        except sqlite3.OperationalError: pass
    for forn, cat, sc in SCONTI:
        db.execute('INSERT OR REPLACE INTO sconti VALUES(?,?,?,?)', (forn, cat, sc, '2026-09-09'))
    for row in SERIE_APP: db.execute('INSERT OR REPLACE INTO serie_app VALUES(?,?,?,?)', row)
    if os.path.exists(a.accessori):
        pages, dec = testo(a.accessori); rows = parse_accessori(pages)
        carica(db, FORN, 'accessori', dec, a.accessori, {'accessori': rows}); scrivi_csv('accessori', rows)
        print(f'accessori {dec}: {len(rows)} articoli')
    if os.path.exists(a.profili):
        pages, dec = testo(a.profili); serie, fin, add, col = parse_profili(pages)
        carica(db, FORN, 'profili', dec, a.profili, {'profili_serie': serie, 'finiture': fin, 'addebiti': add, 'colori': col})
        scrivi_csv('profili_serie', serie); scrivi_csv('finiture', fin); scrivi_csv('addebiti', add); scrivi_csv('colori', col)
        print(f'profili {dec}: {len(serie)} serie, {len(fin)} finiture/maggiorazioni, {len(add)} addebiti, {len(col)} colori')
    if os.path.exists(a.c75s):
        pages, dec = testo(a.c75s); acc, prof = parse_c75s(pages)
        carica(db, FORN, 'c75s_c82s', dec, a.c75s, {'accessori': acc, 'profili_articoli': prof}); scrivi_csv('accessori_c75s', acc); scrivi_csv('profili_articoli_c75s', prof)
        print(f'C75S/C82S-CS {dec}: {len(acc)} accessori, {len(prof)} articoli profilo a kg')
    db.commit()
    sc = db.execute('SELECT categoria, sconto FROM v_sconto ORDER BY 1').fetchall()
    print('sconti:', sc, '->', DB)
