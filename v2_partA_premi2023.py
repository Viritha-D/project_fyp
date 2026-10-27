"""
v2 Part A - PReMI 2023 paper-identity review (read-only on the master).

Writes premi2023_review.csv:
  scope=flagged_file  one row per (flagged Source_File, title): titles, rows, Paper_ID root and
                      Ext range, authors, 2 sample Problem_Context values, the file's
                      classification and the proposed action.
  scope=cross_file_title_pair  title pairs in PReMI 2023 where one title extends the other
                      (added subtitle / suffix), possibly the same paper under two files.
Classifications:
  multi-paper, contiguous      different titles with different authors, each in its own
                               contiguous Paper_ID/Ext block -> keep one paper_key per title
  same paper, title variants   titles differ only by case/punctuation/whitespace or an added
                               subtitle, with the same authors and Problem_Context -> merge
  unclear                      anything else -> no change proposed
Nothing is merged; my_decision is left empty for the reviewer.
"""

import re
import sys
from itertools import combinations
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / 'papers_master_v2.csv'
INDEX = ROOT / 'paper_index.csv'
OUT = ROOT / 'premi2023_review.csv'
ARTICLES = {'a', 'an', 'the'}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def norm_ctx(s):
    return ''.join(w for w in re.findall(r'[a-z0-9]+', str(s).lower()) if w not in ARTICLES)


def variant(t1, t2):
    """True when one normalised title equals or extends the other (added subtitle / suffix)."""
    a, b = norm(t1), norm(t2)
    return a == b or a.startswith(b) or b.startswith(a)


def main():
    d = pd.read_csv(MASTER, dtype=str, keep_default_na=False)
    d['_pos'] = range(len(d))
    d['_root'] = d['Paper_ID'].str.replace(r'_Ext_\d+$', '', regex=True)
    d['_ext'] = d['Paper_ID'].str.extract(r'_Ext_(\d+)$')[0].astype(int)
    p = d[(d['Conference'] == 'PReMI') & (d['Year'] == '2023')]
    titled = p[p['Paper_Title'] != 'Not Reported']

    idx = pd.read_csv(INDEX, dtype=str, keep_default_na=False)
    fl = idx[(idx['Conference'] == 'PReMI') & (idx['Year'] == '2023')
             & idx['flags'].str.contains('source_file_has_multiple_titles')]
    files = sorted({f for s in fl['Source_Files'] for f in s.split(';')})

    rows = []
    file_class = {}
    for f in files:
        g = titled[titled['Source_File'] == f]
        per = []
        for t, h in g.groupby('Paper_Title', sort=False):
            per.append(dict(title=t, rows=len(h), roots=';'.join(dict.fromkeys(h['_root'])),
                            ext=f'{h["_ext"].min():02d}-{h["_ext"].max():02d}', pos=(h['_pos'].min(), h['_pos'].max()),
                            n_pos=len(h), authors=h['Authors'].iloc[0], n_auth=h['Authors'].nunique(),
                            ctx=list(dict.fromkeys(h['Problem_Context']))[:2]))
        all_variants = all(variant(a['title'], b['title']) and norm(a['authors']) == norm(b['authors'])
                           and {norm_ctx(c) for c in a['ctx']} == {norm_ctx(c) for c in b['ctx']}
                           for a, b in combinations(per, 2))
        contiguous = all(x['pos'][1] - x['pos'][0] + 1 == x['n_pos'] for x in per)
        own_block = all(';' not in x['roots'] for x in per) and len({x['roots'] for x in per}) == len(per)
        authors_differ = len({norm(x['authors']) for x in per}) == len(per)
        if all_variants:
            cls, action = 'same paper, title variants', 'merge all titles into one paper_key'
        elif contiguous and own_block and authors_differ:
            cls, action = 'multi-paper, contiguous', 'keep one paper_key per title (no change)'
        else:
            cls, action = 'unclear', 'no change proposed; reviewer to decide'
        file_class[f] = (cls, len(per))
        note = ('' if cls != 'unclear' else
                f'authors differ between titles: {authors_differ}; each title in its own contiguous '
                f'Paper_ID block: {contiguous and own_block}; titles are variants of each other: {all_variants}')
        for x in per:
            rows.append(dict(scope='flagged_file', Source_File=f, titles=x['title'], rows_per_title=x['rows'],
                             paper_id_roots=x['roots'], ext_ranges=x['ext'], authors=x['authors'],
                             sample_problem_context=' | '.join(x['ctx']), classification=cls,
                             proposed_action=action, notes=note, my_decision=''))

    # cross-file pairs: one title extends the other
    T = titled.groupby(['Paper_Title', 'Source_File'], sort=False).agg(
        authors=('Authors', 'first'), ctx=('Problem_Context', lambda s: list(dict.fromkeys(s))),
        rows=('Paper_ID', 'size'), roots=('_root', lambda s: ';'.join(dict.fromkeys(s)))).reset_index()
    merges = 0
    for (_, a), (_, b) in combinations(T.iterrows(), 2):
        if a['Source_File'] == b['Source_File'] or norm(a['Paper_Title']) == norm(b['Paper_Title']):
            continue
        if not variant(a['Paper_Title'], b['Paper_Title']):
            continue
        same_auth = norm(a['authors']) == norm(b['authors'])
        same_ctx = {norm_ctx(c) for c in a['ctx']} == {norm_ctx(c) for c in b['ctx']}
        if same_auth and same_ctx:
            cls = 'same paper, title variants'
            action = f'merge {b["roots"]} into {a["roots"]} (one paper_key)'
            merges += 1
        else:
            cls, action = 'unclear', 'no change proposed; reviewer to decide'
        note = f'same authors: {same_auth}; same Problem_Context (ignoring articles/case): {same_ctx}'
        rows.append(dict(scope='cross_file_title_pair', Source_File=f'{a["Source_File"]} | {b["Source_File"]}',
                         titles=f'{a["Paper_Title"]} || {b["Paper_Title"]}', rows_per_title=f'{a["rows"]} | {b["rows"]}',
                         paper_id_roots=f'{a["roots"]} | {b["roots"]}', ext_ranges='',
                         authors=f'{a["authors"]} | {b["authors"]}',
                         sample_problem_context=f'{" / ".join(a["ctx"][:2])} | {" / ".join(b["ctx"][:2])}',
                         classification=cls, proposed_action=action, notes=note, my_decision=''))

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)

    # ---------------- report ----------------
    print(f'PReMI 2023: {len(p)} rows, {p["Source_File"].nunique()} files, {titled["Paper_Title"].map(norm).nunique()} real titles, '
          f'{len(fl)} flagged papers in {len(files)} files')
    for f, (cls, n) in file_class.items():
        print(f'  {f}: {n} titles -> {cls}')
    print(f'file classification counts: {pd.Series([c for c, _ in file_class.values()]).value_counts().to_dict()}')
    pairs = out[out['scope'] == 'cross_file_title_pair']
    print(f'cross-file title pairs: {len(pairs)} -> {pairs["classification"].value_counts().to_dict()}')
    for _, r in pairs.iterrows():
        print(f'  [{r.classification}] {r.titles[:150]}\n      files {r.Source_File}; authors {r.authors[:90]}; {r.notes}')
    n_before = len(idx)
    print(f'papers now: {n_before}; after the proposed merges: {n_before - merges} ({merges} merge(s) proposed)')
    print(f'wrote {OUT.name} ({len(out)} rows)')


if __name__ == '__main__':
    sys.exit(main())
