"""
Intake and validation of the independent query sets (no retrieval, no ranking, no scoring).

1. CSV copies of queries_t1.xlsx / queries_t2.xlsx: every cell as written (round-trip checked), plus a separate
   column gold_ids_norm with the gold ids upper-cased (split on ';', stripped, joined with ';').
2. Row validation using only families_v5.json, entity_to_family_v5.csv and families_browse.csv:
   (a) every gold id exists (case-insensitive); (b) it is not an excluded family (the families of the hygiene-excluded
   entities E03148 "Not Reported" and E00657 extraction_artifact_suspect, mapped through entity_to_family_v5.csv);
   (c) each written name equals the stored name after normalisation (NFKC, lower case, whitespace collapsed),
   otherwise the difflib similarity is reported; (d) n_papers of each gold family.
3. Descriptives: dense cosine (all-mpnet-base-v2, query text only) against every queries_v2 query and against the
   other new set; identical texts; gold families shared with queries_v2 gold; gold families with < 2 papers;
   words per query.
Nothing is corrected. Writes validation_t.md and validation_t_rows.csv.

Usage: python retrieval_v2/evaluation/intake_validate_t.py
"""

import csv
import difflib
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SETS = [('t1', 'queries_t1.xlsx'), ('t2', 'queries_t2.xlsx')]
EXCLUDED_ENTITIES = {'E03148': 'Not Reported', 'E00657': 'extraction_artifact_suspect'}
COLS = ['query_id', 'query_text', 'gold_families', 'gold_family_names', 'notes']


def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(s)).lower()).strip()


def split_ids(s):
    return [x.strip() for x in str(s).split(';') if x.strip()]


def read_xlsx(p):
    ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]       # read only; the xlsx is never saved
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    rows = [r for r in rows if any(c is not None for c in r)]
    assert [str(c) for c in rows[0]] == COLS, rows[0]
    return [['' if c is None else str(c) for c in r] for r in rows]


def to_csv(name, fname):
    rows = read_xlsx(HERE / fname)
    out = HERE / fname.replace('.xlsx', '.csv')
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(rows[0] + ['gold_ids_norm'])
        for r in rows[1:]:
            w.writerow(r + [';'.join(x.upper() for x in split_ids(r[2]))])
    back = list(csv.reader(open(out, encoding='utf-8')))
    assert [b[:5] for b in back] == rows, 'round-trip mismatch'
    return pd.read_csv(out, dtype=str, keep_default_na=False)


def main():
    fams = {f['family_id']: f for f in json.loads((ROOT / 'families_v5.json').read_text(encoding='utf-8'))}
    e2f = pd.read_csv(ROOT / 'entity_to_family_v5.csv', dtype=str, keep_default_na=False)
    browse = pd.read_csv(HERE / 'families_browse.csv', dtype=str, keep_default_na=False)
    bname = dict(zip(browse.family_id, browse.family_name))
    assert all(bname[f] == fams[f]['family_name'] for f in bname), 'browse file and families_v5 disagree on a name'
    excl = {}
    for e, why in EXCLUDED_ENTITIES.items():
        f = e2f.loc[e2f.entity_id == e, 'family_id'].iloc[0]
        if set(e2f.loc[e2f.family_id == f, 'entity_id']) <= set(EXCLUDED_ENTITIES):
            excl[f] = why
    upper = {f.upper(): f for f in fams}
    by_name = {}
    for f, x in fams.items():
        by_name.setdefault(norm(x['family_name']), []).append(f)
    q2 = pd.read_csv(HERE / 'queries_v2.csv', dtype=str, keep_default_na=False)
    q2_gold = {f for g in q2.gold_families for f in split_ids(g)}

    D, rows = {}, []
    for s, fname in SETS:
        D[s] = to_csv(s, fname)
        for _, r in D[s].iterrows():
            ids, names = split_ids(r.gold_families), [x.strip() for x in r.gold_family_names.split(';')]
            problems, details = [], []
            if len(ids) != len(names):
                problems.append(f'(c) {len(ids)} ids but {len(names)} names')
            for i, raw in enumerate(ids):
                wn = names[i] if i < len(names) else ''
                fid = upper.get(raw.upper())
                d = {'set': s, 'query_id': r.query_id, 'id_as_written': raw, 'name_as_written': wn,
                     'id_norm': raw.upper(), 'exists': fid is not None, 'stored_name': '', 'excluded': '',
                     'name_match': '', 'name_similarity': '', 'n_papers': '',
                     'ids_whose_stored_name_equals_written_name': ';'.join(by_name.get(norm(wn), []))}
                if fid is None:
                    problems.append(f'(a) {raw} does not exist')
                else:
                    st = fams[fid]['family_name']
                    d.update(stored_name=st, n_papers=fams[fid]['n_papers'], excluded=excl.get(fid, ''))
                    if fid in excl:
                        problems.append(f'(b) {raw} is excluded ({excl[fid]})')
                    ok = norm(st) == norm(wn)
                    d.update(name_match=ok, name_similarity=round(difflib.SequenceMatcher(None, norm(st), norm(wn)).ratio(), 3))
                    if not ok:
                        problems.append(f'(c) {raw}: written "{wn}" vs stored "{st}"')
                details.append(d)
            for d in details:
                d['row_valid'] = not problems
                d['row_problems'] = ' | '.join(problems)
            rows.extend(details)
    V = pd.DataFrame(rows)
    V.to_csv(HERE / 'validation_t_rows.csv', index=False)
    rowv = V.groupby(['set', 'query_id'], sort=False).agg(valid=('row_valid', 'first'), problems=('row_problems', 'first')).reset_index()

    # ---- descriptives
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    enc = lambda t: model.encode(list(t), normalize_embeddings=True, show_progress_bar=False)
    E = {s: enc(D[s].query_text) for s in D}
    E2 = enc(q2.query_text)

    L = ['# Validation of independent query sets t1, t2 (no scoring)', '',
         'Produced by `intake_validate_t.py`. Sources for gold checks: families_v5.json, entity_to_family_v5.csv, '
         'families_browse.csv (browse names equal families_v5 names for all families: checked). Excluded families: '
         + ', '.join(f'{f} ({fams[f]["family_name"]}; {w})' for f, w in excl.items()) + '. Nothing was corrected.', '',
         '## Per-set validation', '',
         '| set | rows | valid | invalid | invalid share | (a) id missing | (b) excluded | (c) name mismatch / count | '
         'distinct gold families (valid ids) | of which in queries_v2 gold | of which < 2 papers | words per query mean / median / min / max |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for s in D:
        rv = rowv[rowv.set == s]
        v = V[V.set == s]
        has = lambda tag: rv.problems.str.contains(re.escape(tag)).sum()
        gf = {upper[i] for i in v.id_norm if i in upper}
        w = D[s].query_text.str.split().str.len()
        L.append(f'| {s} | {len(rv)} | {int(rv.valid.sum())} | {int((~rv.valid).sum())} | {(~rv.valid).mean():.0%} | '
                 f'{has("(a)")} | {has("(b)")} | {has("(c)")} | {len(gf)} | {len(gf & q2_gold)} | '
                 f'{sum(fams[f]["n_papers"] < 2 for f in gf)} | {w.mean():.1f} / {w.median():.0f} / {w.min()} / {w.max()} |')
    w2 = q2.query_text.str.split().str.len()
    L += ['', f'Reference, queries_v2: words per query {w2.mean():.1f} / {w2.median():.0f} / {w2.min()} / {w2.max()}.', '',
          '## Invalid rows (every failing id; correct nothing)', '']
    for s in D:
        bad = rowv[(rowv.set == s) & (~rowv.valid)]
        L += [f'### {s}: {len(bad)} invalid of {len(rowv[rowv.set == s])}', '',
              '| query | id as written | name as written | stored name for that id | similarity | n_papers | ids whose stored name equals the written name (information only) |',
              '|---|---|---|---|---|---|---|']
        for _, b in bad.iterrows():
            for _, d in V[(V.set == s) & (V.query_id == b.query_id)].iterrows():
                if d.exists and d.name_match is True and not d.excluded:
                    continue
                L.append(f'| {s}:{d.query_id} | {d.id_as_written} | {d.name_as_written} | {d.stored_name or "(id does not exist)"} | '
                         f'{d.name_similarity} | {d.n_papers} | {d.ids_whose_stored_name_equals_written_name or "-"} |')
            if '(c)' in b.problems and 'ids but' in b.problems:
                L.append(f'| {s}:{b.query_id} | (row) | {b.problems} | | | | |')
        L.append('')
    L += ['## Query similarity (dense cosine, all-mpnet-base-v2, query text only)', '']
    pairs = []
    for s in D:
        other = [o for o in D if o != s]
        for i, qid in enumerate(D[s].query_id):
            c2 = E2 @ E[s][i]
            j = int(np.argmax(c2))
            pairs.append((s, qid, 'queries_v2', q2.query_id[j], float(c2[j]), D[s].query_text[i], q2.query_text[j]))
            for o in other:
                co = E[o] @ E[s][i]
                k = int(np.argmax(co))
                pairs.append((s, qid, o, D[o].query_id[k], float(co[k]), D[s].query_text[i], D[o].query_text[k]))
    P = pd.DataFrame(pairs, columns=['set', 'query_id', 'against', 'match_id', 'cosine', 'text', 'match_text'])
    ident = [(a, b) for s in D for o in D for a, ta in zip(D[s].query_id, D[s].query_text) for b, tb in zip(D[o].query_id, D[o].query_text)
             if (s, a) < (o, b) and norm(ta) == norm(tb)] + \
            [(s, a, b) for s in D for a, ta in zip(q2.query_id, q2.query_text) for b, tb in zip(D[s].query_id, D[s].query_text) if norm(ta) == norm(tb)]
    L += [f'Identical texts (normalised) within or across t1, t2, queries_v2: {len(ident)}' + (f' {ident}' if ident else '') + '.', '',
          '| set | against | queries with best cosine > 0.8 | >= 0.95 | max cosine |', '|---|---|---|---|---|']
    for (s, a), g in P.groupby(['set', 'against'], sort=False):
        L.append(f'| {s} | {a} | {int((g.cosine > 0.8).sum())} | {int((g.cosine >= 0.95).sum())} | {g.cosine.max():.3f} |')
    L += ['', 'Within-set best cosine (other query of the same set):']
    for s in D:
        C = E[s] @ E[s].T
        np.fill_diagonal(C, -1)
        L.append(f'- {s}: max {C.max():.3f}; pairs > 0.8: {int((np.triu(C, 1) > 0.8).sum())}')
    L += ['', 'Flags (best cosine > 0.8):', '']
    fl = P[P.cosine > 0.8].sort_values('cosine', ascending=False)
    L += [f'- {r.set}:{r.query_id} vs {r.against}:{r.match_id}  cosine {r.cosine:.3f}' for r in fl.itertuples()] or ['- none']
    L += ['', 'The 5 highest best-matches per set and comparison (top match shown):', '']
    for (s, a), g in P.groupby(['set', 'against'], sort=False):
        L.append(f'**{s} vs {a}**')
        L.append('')
        for r in g.sort_values('cosine', ascending=False).head(5).itertuples():
            L.append(f'- {r.set}:{r.query_id} ↔ {r.against}:{r.match_id}, cosine {r.cosine:.3f}: "{r.text[:110]}" ↔ "{r.match_text[:110]}"')
        L.append('')
    (HERE / 'validation_t.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    P.to_csv(HERE / 'similarity_t.csv', index=False)
    print('\n'.join(L))


if __name__ == '__main__':
    sys.exit(main())
