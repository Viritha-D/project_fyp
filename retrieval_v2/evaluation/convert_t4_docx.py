"""
Convert the submitted query files to xlsx/CSV without changing any cell (PREREGISTRATION_final_amendment3.md, s. 2).

t4: queries_t4_original.docx (one Word table) -> queries_t4.xlsx and queries_t4.csv.
    - Every cell's text is copied verbatim (python-docx cell text; paragraphs inside a cell are joined with '\n').
    - The only change: in gold_family_names, newline-separated names become ';'-separated ('\n' -> ';', nothing
      stripped, nothing else touched).
    - An added column group_norm maps notes: 'Theory' -> 'theory / algorithm analysis', 'applied' -> 'applied /
      real-world', 'unusual / niche' unchanged; any other value is copied unchanged and reported. notes is left as is.
    - Round-trip check: every original cell equals the converted cell, except gold_family_names, where the converted
      text with ';' put back to '\n' equals the original. The xlsx and CSV hold the same cells.
t3: queries_t3.xlsx -> queries_t3.csv, every cell as written (round-trip checked). No column added.

The submitted files are only read; their sha256 is checked before and after.

Usage: python retrieval_v2/evaluation/convert_t4_docx.py
"""

import csv
import hashlib
import sys
from pathlib import Path

import docx
import openpyxl
from openpyxl.styles import Alignment, Font

HERE = Path(__file__).resolve().parent
GROUP_NORM = {'Theory': 'theory / algorithm analysis', 'applied': 'applied / real-world', 'unusual / niche': 'unusual / niche'}
COLS_T4 = ['query_id', 'query_text', 'gold_families', 'gold_family_names', 'notes']
COLS_T3 = ['query_id', 'query_text', 'gold_family_names', 'notes']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_xlsx(path, header, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'queries'
    ws.append(header)
    for r in rows:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True)
    for row in ws.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
    wb.save(path)


def read_xlsx(path):
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    rows = [['' if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
    return [r for r in rows if any(c.strip() for c in r)]


def convert_t4():
    src = HERE / 'queries_t4_original.docx'
    before = sha(src)
    d = docx.Document(src)
    assert len(d.tables) == 1, f'expected one table, found {len(d.tables)}'
    orig = [[c.text for c in r.cells] for r in d.tables[0].rows]
    assert orig[0] == COLS_T4, orig[0]
    gi, ni = COLS_T4.index('gold_family_names'), COLS_T4.index('notes')
    assert all(';' not in r[gi] for r in orig[1:]), 'a gold_family_names cell already contains ";"'
    out, unknown = [], []
    for r in orig[1:]:
        new = list(r)
        new[gi] = r[gi].replace('\n', ';')
        if r[ni] not in GROUP_NORM:
            unknown.append((r[0], r[ni]))
        out.append(new + [GROUP_NORM.get(r[ni], r[ni])])
    header = COLS_T4 + ['group_norm']
    write_xlsx(HERE / 'queries_t4.xlsx', header, out)
    with open(HERE / 'queries_t4.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(out)
    # round-trip check against the docx
    x = read_xlsx(HERE / 'queries_t4.xlsx')
    c = list(csv.reader(open(HERE / 'queries_t4.csv', encoding='utf-8')))
    assert x == c, 'xlsx and CSV differ'
    assert c[0] == header
    changed = 0
    for o, n in zip(orig[1:], c[1:]):
        for j, col in enumerate(COLS_T4):
            if col == 'gold_family_names':
                assert n[j].replace(';', '\n') == o[j], (o[0], col)
                changed += n[j] != o[j]
            else:
                assert n[j] == o[j], (o[0], col, o[j], n[j])
    assert len(c) == len(orig), 'row count differs'
    assert sha(src) == before, 'the docx changed'
    other_nl = sum('\n' in o[j] for o in orig[1:] for j, col in enumerate(COLS_T4) if col != 'gold_family_names')
    print(f't4: {len(orig) - 1} rows x {len(COLS_T4)} original columns copied; round-trip OK (xlsx == CSV; every cell '
          f'equal to the docx except gold_family_names, which differs only by the newline rule in {changed} cells). '
          f'Newlines kept as written in other columns: {other_nl}. notes values without a mapping: {unknown or "none"}. '
          f'docx sha256 {before} (unchanged).')


def convert_t3():
    src = HERE / 'queries_t3.xlsx'
    before = sha(src)
    rows = read_xlsx(src)
    assert rows[0] == COLS_T3, rows[0]
    with open(HERE / 'queries_t3.csv', 'w', newline='', encoding='utf-8') as fh:
        csv.writer(fh).writerows(rows)
    assert list(csv.reader(open(HERE / 'queries_t3.csv', encoding='utf-8'))) == rows, 'round-trip mismatch'
    assert sha(src) == before, 'the xlsx changed'
    print(f't3: {len(rows) - 1} rows x {len(rows[0])} columns copied cell for cell; round-trip OK. '
          f'xlsx sha256 {before} (unchanged).')


if __name__ == '__main__':
    convert_t4()
    convert_t3()
    sys.exit(0)
