"""
Resolve the gold family names of a names-only submission to family ids (PREREGISTRATION_final_amendment2.md).

Input: a submission (.xlsx, first sheet, or .csv) with columns query_id, query_text, gold_family_names, notes and
NO id column. Names in gold_family_names are separated by ';'.

Each written name is matched EXACTLY, after casefold and whitespace collapsing, against the family names in
families_v5.json. A name that matches no family, or more than one, makes the whole query invalid; the name and the
candidates are printed. A name that resolves to a hygiene-excluded family (F02124 "Not Reported", F00334 the family
of the extraction_artifact_suspect entity E00657) also makes the query invalid. A query with no names is invalid.
Nothing is guessed. For a name with no match, the closest names are printed as information only. They are never
used.

The submitted file is never modified: it is only read, and its sha256 is checked before and after. The result goes
to a separate CSV, <stem>_resolved.csv next to the input (or --out). That CSV holds the submitted columns unchanged
plus gold_families (resolved ids, ';'), valid and problems.

A submission that contains a gold_families / id column is refused: it is validated by amendment 1 instead.

Usage: python retrieval_v2/evaluation/resolve_gold_names.py <submission.xlsx|csv> [--out FILE.csv]
Exit code: 0 if every query is valid, 1 if any query is invalid, 2 on a refused or unreadable input.
"""

import argparse
import csv
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
COLS = ['query_id', 'query_text', 'gold_family_names', 'notes']
EXCLUDED = {'F02124': 'Not Reported', 'F00334': 'extraction_artifact_suspect (E00657)'}


def key(s):
    return re.sub(r'\s+', ' ', str(s).casefold()).strip()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_rows(p):
    p = Path(p)
    if p.suffix.lower() == '.xlsx':
        import openpyxl
        ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]      # read only; never saved
        rows = [['' if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
    else:
        rows = list(csv.reader(open(p, encoding='utf-8')))
    rows = [r for r in rows if any(c.strip() for c in r)]
    return rows[0], rows[1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('submission')
    ap.add_argument('--out')
    a = ap.parse_args()
    src = Path(a.submission)
    before = sha(src)
    header, body = read_rows(src)
    header = [h.strip() for h in header]
    if any(h.lower() in ('gold_families', 'gold_ids', 'family_id', 'family_ids') for h in header):
        print(f'REFUSED: {src.name} contains an id column ({header}). Validate it by amendment 1 instead.')
        return 2
    if header[:len(COLS)] != COLS:
        print(f'REFUSED: expected columns {COLS}, found {header}')
        return 2
    fams = json.loads((ROOT / 'families_v5.json').read_text(encoding='utf-8'))
    by_key = {}
    for f in fams:
        by_key.setdefault(key(f['family_name']), []).append(f['family_id'])
    name_of = {f['family_id']: f['family_name'] for f in fams}
    all_keys = list(by_key)

    out_rows, n_invalid = [], 0
    for r in body:
        r = (r + [''] * len(header))[:len(header)]
        rec = dict(zip(header, r))
        names = [x.strip() for x in rec['gold_family_names'].split(';') if x.strip()]
        ids, problems = [], []
        if not names:
            problems.append('no gold family names')
        for n in names:
            hits = by_key.get(key(n), [])
            if len(hits) == 1:
                if hits[0] in EXCLUDED:
                    problems.append(f'"{n}" -> {hits[0]} is an excluded family ({EXCLUDED[hits[0]]})')
                ids.append(hits[0])
            elif not hits:
                close = difflib.get_close_matches(key(n), all_keys, n=3, cutoff=0.6)
                info = '; '.join(f'{name_of[i]} ({i})' for k in close for i in by_key[k]) or 'none'
                problems.append(f'"{n}" matches no family (closest, information only, NOT used: {info})')
            else:
                problems.append(f'"{n}" matches {len(hits)} families: ' + '; '.join(f'{i} ({name_of[i]})' for i in hits))
        valid = not problems
        n_invalid += not valid
        out_rows.append(r + [';'.join(ids) if valid else '', valid, ' | '.join(problems)])
        status = 'valid' if valid else 'INVALID'
        print(f'{rec["query_id"]}: {status}' + ('' if valid else ' - ' + ' | '.join(problems)))

    out = Path(a.out) if a.out else src.with_name(f'{src.stem}_resolved.csv')
    assert out.resolve() != src.resolve(), 'refusing to overwrite the submission'
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(header + ['gold_families', 'valid', 'problems'])
        w.writerows(out_rows)
    assert sha(src) == before, 'the submitted file changed while being read'
    print(f'\n{len(body)} queries: {len(body) - n_invalid} valid, {n_invalid} invalid. Submission sha256 {before} '
          f'(unchanged). Resolved ids written to {out}.')
    return 1 if n_invalid else 0


if __name__ == '__main__':
    sys.exit(main())
