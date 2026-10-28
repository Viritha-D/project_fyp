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
  scope=same_2023_proceedings_paper  two PReMI 2023 paper_keys that match the same
                      proceedings paper (e.g. full title and running head), not already a pair
  scope=other_year_in_2023_proceedings  PReMI papers labelled with another Year whose title
                      and at least one author surname are found in the PReMI 2023 proceedings.
When premi2023_proceedings_check.csv exists (v2_partD_premi2023_proceedings.py), every row
gets a proceedings_evidence column, and a title pair whose two titles both match the same
proceedings paper with a shared author surname is proposed as one paper.
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
CHECK = ROOT / 'premi2023_proceedings_check.csv'
MATCHED = {'exact', 'running_head', 'prefix', 'fuzzy'}
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

    chk = pd.read_csv(CHECK, dtype=str, keep_default_na=False).set_index('paper_key') if CHECK.exists() else None

    def evidence(year, title):
        if chk is None:
            return ''
        key = f'PReMI|{year}|{norm(title)}'
        if key not in chk.index:
            return 'not checked'
        c = chk.loc[key]
        if c['match'] not in MATCHED:
            return 'not in the PReMI 2023 proceedings'
        return (f'{c["match"]} match: "{c["toc_title"]}" (pp. {c["toc_pages"]}; {c["toc_authors"]}); '
                f'shared author surnames: {c["author_overlap"] or "none"}')

    def proceedings_paper(year, title):
        """(toc_title, has shared author) for a matched title, else None."""
        if chk is None:
            return None
        key = f'PReMI|{year}|{norm(title)}'
        if key not in chk.index or chk.loc[key, 'match'] not in MATCHED:
            return None
        return chk.loc[key, 'toc_title'], chk.loc[key, 'author_overlap'] != ''

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
                             proposed_action=action, notes=note,
                             proceedings_evidence=evidence('2023', x['title']), my_decision=''))

    # cross-file pairs: one title extends the other
    T = titled.groupby(['Paper_Title', 'Source_File'], sort=False).agg(
        authors=('Authors', 'first'), ctx=('Problem_Context', lambda s: list(dict.fromkeys(s))),
        rows=('Paper_ID', 'size'), roots=('_root', lambda s: ';'.join(dict.fromkeys(s)))).reset_index()
    merges = 0
    covered = set()   # title pairs already reviewed as cross-file pairs
    for (_, a), (_, b) in combinations(T.iterrows(), 2):
        if a['Source_File'] == b['Source_File'] or norm(a['Paper_Title']) == norm(b['Paper_Title']):
            continue
        if not variant(a['Paper_Title'], b['Paper_Title']):
            continue
        covered.add(frozenset((norm(a['Paper_Title']), norm(b['Paper_Title']))))
        same_auth = norm(a['authors']) == norm(b['authors'])
        same_ctx = {norm_ctx(c) for c in a['ctx']} == {norm_ctx(c) for c in b['ctx']}
        pa, pb = proceedings_paper('2023', a['Paper_Title']), proceedings_paper('2023', b['Paper_Title'])
        same_proc = bool(pa and pb and pa[0] == pb[0] and pa[1] and pb[1])
        if same_auth and same_ctx:
            cls = 'same paper, title variants'
            action = f'merge {b["roots"]} into {a["roots"]} (one paper_key)'
            merges += 1
        elif same_proc:
            cls = 'same paper, title variants'
            action = f'merge {b["roots"]} into {a["roots"]} (one paper_key); both titles are the same proceedings paper'
            merges += 1
        else:
            cls, action = 'unclear', 'no change proposed; reviewer to decide'
        note = (f'same authors: {same_auth}; same Problem_Context (ignoring articles/case): {same_ctx}; '
                f'both titles match the same PReMI 2023 proceedings paper with a shared author: {same_proc}')
        rows.append(dict(scope='cross_file_title_pair', Source_File=f'{a["Source_File"]} | {b["Source_File"]}',
                         titles=f'{a["Paper_Title"]} || {b["Paper_Title"]}', rows_per_title=f'{a["rows"]} | {b["rows"]}',
                         paper_id_roots=f'{a["roots"]} | {b["roots"]}', ext_ranges='',
                         authors=f'{a["authors"]} | {b["authors"]}',
                         sample_problem_context=f'{" / ".join(a["ctx"][:2])} | {" / ".join(b["ctx"][:2])}',
                         classification=cls, proposed_action=action, notes=note,
                         proceedings_evidence=' || '.join(evidence('2023', t) for t in (a['Paper_Title'], b['Paper_Title'])),
                         my_decision=''))

    # two 2023 paper_keys that are the same proceedings paper (e.g. full title + running head)
    if chk is not None:
        c = chk.reset_index()
        c23 = c[(c['Year'] == '2023') & c['match'].isin(MATCHED)]
        for toc_title, grp in c23.groupby('toc_title'):
            if len(grp) < 2:
                continue
            keys = [norm(t) for t in grp['title']]
            if all(frozenset((x, y)) in covered for x, y in combinations(keys, 2)):
                continue
            all_auth = (grp['author_overlap'] != '').all()
            main = grp.sort_values('match', key=lambda m: m != 'exact').iloc[0]
            if all_auth:
                cls = 'same paper, title variants'
                action = f'merge into {main["paper_key"]} (same proceedings paper)'
                merges += len(grp) - 1
            else:
                cls, action = 'unclear', 'no change proposed; reviewer to decide'
            rows.append(dict(scope='same_2023_proceedings_paper', Source_File=' | '.join(grp['Source_Files']),
                             titles=' || '.join(grp['title']), rows_per_title='', paper_id_roots='', ext_ranges='',
                             authors=' | '.join(grp['master_authors']), sample_problem_context='',
                             classification=cls, proposed_action=action,
                             notes=f'match kinds: {", ".join(grp["match"])}; every copy shares an author with the proceedings: {all_auth}',
                             proceedings_evidence=' || '.join(evidence('2023', t) for t in grp['title']), my_decision=''))

    # PReMI papers labelled with another Year that are in the 2023 proceedings
    if chk is not None:
        hits = c[(c['Year'] != '2023') & c['match'].isin(MATCHED) & (c['author_overlap'] != '')]
        c23 = c[(c['Year'] == '2023') & c['match'].isin(MATCHED)]
        for _, h in hits.iterrows():
            twin = c23[c23['toc_title'] == h['toc_title']]
            if len(twin):
                cls = 'same paper, title variants'
                action = (f'merge into {twin.iloc[0]["paper_key"]} (same proceedings paper); '
                          f'Year {h["Year"]} is likely wrong')
                merges += 1
            else:
                cls = 'unclear'
                action = f'no 2023 copy; Year {h["Year"]} looks wrong (paper is in the 2023 proceedings); reviewer to decide'
            rows.append(dict(scope='other_year_in_2023_proceedings', Source_File=h['Source_Files'], titles=h['title'],
                             rows_per_title='', paper_id_roots='', ext_ranges='', authors=h['master_authors'],
                             sample_problem_context='', classification=cls, proposed_action=action,
                             notes=f'labelled PReMI {h["Year"]}' + (f'; 2023 copy: {twin.iloc[0]["title"]} '
                                                                    f'({twin.iloc[0]["Source_Files"]})' if len(twin) else ''),
                             proceedings_evidence=evidence(h['Year'], h['title']), my_decision=''))

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)

    # ---------------- report ----------------
    print(f'PReMI 2023: {len(p)} rows, {p["Source_File"].nunique()} files, {titled["Paper_Title"].map(norm).nunique()} real titles, '
          f'{len(fl)} flagged papers in {len(files)} files')
    for f, (cls, n) in file_class.items():
        print(f'  {f}: {n} titles -> {cls}')
    print(f'file classification counts: {pd.Series([c for c, _ in file_class.values()]).value_counts().to_dict()}')
    if chk is not None:
        fe = out[out['scope'] == 'flagged_file']
        print(f'flagged-file titles found in the PReMI 2023 proceedings: '
              f'{int((~fe["proceedings_evidence"].str.startswith("not")).sum())} of {len(fe)}')
        oy = out[out['scope'] == 'other_year_in_2023_proceedings']
        print(f'other-Year PReMI papers found in the 2023 proceedings: {len(oy)} -> {oy["classification"].value_counts().to_dict()}')
        for _, r in oy.iterrows():
            print(f'  [{r.classification}] {r.titles[:80]} ({r.Source_File}, {r.notes[:110]})')
        sp = out[out['scope'] == 'same_2023_proceedings_paper']
        for _, r in sp.iterrows():
            print(f'  [same 2023 proceedings paper: {r.classification}] {r.titles[:140]} ({r.Source_File})')
    pairs = out[out['scope'] == 'cross_file_title_pair']
    print(f'cross-file title pairs: {len(pairs)} -> {pairs["classification"].value_counts().to_dict()}')
    for _, r in pairs.iterrows():
        print(f'  [{r.classification}] {r.titles[:150]}\n      files {r.Source_File}; authors {r.authors[:90]}; {r.notes}')
    n_before = len(idx)
    print(f'papers now: {n_before}; after the proposed merges: {n_before - merges} ({merges} merge(s) proposed)')
    print(f'wrote {OUT.name} ({len(out)} rows)')


if __name__ == '__main__':
    sys.exit(main())
