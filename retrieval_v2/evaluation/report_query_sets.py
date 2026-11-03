"""
Build report_query_sets.md from the scored query sets (no model is run here).

Primary set: queries_v2 (results_queries_v2.csv, report_queries_v2.md). Secondary sets ai_queries_v1 and
queries_reworded_v1 are included if their results files exist, otherwise listed as not run.
Error analysis (primary only), as pre-registered in PREREGISTRATION_queries.md.

Usage: python retrieval_v2/evaluation/report_query_sets.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PRIMARY = 'queries_v2'
SECONDARY = ['ai_queries_v1', 'queries_reworded_v1']


def body(stem):
    t = (HERE / f'report_{stem}.md').read_text(encoding='utf-8').splitlines()
    return '\n'.join(l.replace('## ', '### ', 1) if l.startswith('## ') else l for l in t[1:])


def main():
    fams = {f['family_id']: f['family_name'] for f in json.loads((ROOT / 'families_v5.json').read_text(encoding='utf-8'))}
    name = lambda ids: '; '.join(fams.get(f, f) for f in ids.split(';') if f)
    Q = pd.read_csv(HERE / f'{PRIMARY}.csv', dtype=str, keep_default_na=False)
    R = pd.read_csv(HERE / f'results_{PRIMARY}.csv', keep_default_na=False)
    S = R[R.system == 'stacked'].copy()
    M = S[S['hit@5'] == 0].merge(Q[['query_id', 'query_text']], on='query_id').sort_values('query_id')
    M['cause'] = M['gold_in_candidates'].map(lambda v: '(b) gold among candidates, ranked below 5' if str(v) == 'True'
                                              else '(a) no gold family among the candidates')
    M['c_all'] = M['gold_all_lt2_papers'].astype(str) == 'True'
    M['c_any'] = M['gold_any_lt2_papers'].astype(str) == 'True'
    prov = (HERE / 'PROVENANCE.md').read_text(encoding='utf-8').strip()
    L = ['# Written query sets: scoring report', '',
         'Models frozen at tag `retrieval-v2.1-frozen` (c0f8802). Pre-registration: `PREREGISTRATION_queries.md` '
         '(aed8464, committed before scoring). The query file was committed before any scoring (c0f8802; marker 2bf6321).', '',
         '## Provenance (from `PROVENANCE.md`, unedited)', '', '> ' + prov.replace('\n', '\n> '), '',
         'Blank in the statement: "System outputs seen before the file was final." has no answer (left blank, as given). '
         'The "Tools used" entry reads "IEEE(reference." as given.', '',
         '## Gold validation', '',
         '126 gold ids in 55 queries; every id exists in families_v5, none is a hygiene-excluded family '
         '(F02124 "Not Reported", F00334 "Evolutionary Algorithm"), every `gold_family_names` entry equals the family '
         'name: **0 mismatches**; no query without valid gold.', '',
         f'## Primary set: `{PRIMARY}.csv`', '', body(PRIMARY), '']
    for s in SECONDARY:
        if (HERE / f'report_{s}.md').exists():
            L += [f'## Secondary set: `{s}.csv`', '', body(s), '']
        else:
            L += [f'## Secondary set: `{s}.csv`', '', f'**Not run**: `{s}.csv` is not in the repository, on any branch, '
                  'or among the uploaded files. It will be scored with the same frozen script when supplied.', '']
    L += ['## Error analysis (primary set, stacked ranker, no gold family in the top 5)', '',
          f'Misses: {len(M)} of {len(S)} queries.', '',
          '| cause | queries | of which (c): every gold family has < 2 papers |', '|---|---|---|']
    for c, g in M.groupby('cause'):
        L.append(f'| {c} | {len(g)} | {int(g.c_all.sum())} |')
    L += ['', f'(c) every gold family has fewer than 2 papers in the index: {int(M.c_all.sum())} of {len(M)} misses; '
          f'at least one gold family with fewer than 2 papers: {int(M.c_any.sum())}.', '',
          'Misses by group: ' + ', '.join(f'{g} {n}' for g, n in M.group.value_counts().items()), '',
          '### First 15 misses (query_id order)', '']
    for _, r in M.head(15).iterrows():
        L += [f'- **{r.query_id}** ({r.group}), cause {r.cause[:3]}' + (', (c)' if r.c_all else ''),
              f'  - query: {r.query_text}',
              f'  - gold: {name(r.gold)}',
              f'  - stacked top 5: {name(r.top5)}']
    (HERE / 'report_query_sets.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L[L.index('## Error analysis (primary set, stacked ranker, no gold family in the top 5)'):]))


if __name__ == '__main__':
    main()
