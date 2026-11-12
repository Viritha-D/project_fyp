"""
Post-hoc descriptive analysis for the product system v2.3 (blend 0.5). It decides nothing: the final test and its
decisions are fixed in report_final.md. It reads only scored_queries_final.csv, which it never changes.

Blend minus stacked (hit@5, MRR) per set and leaving each set out; blend hit@5 and MRR by group; error causes
(a, b, c) for the blend by set. Paired bootstrap 10,000 resamples, seed 42 (as the final test); group means 1,000.

Usage: python retrieval_v2/evaluation/posthoc_v23.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pandas as pd  # noqa: E402
import score_final as sf  # noqa: E402

R = pd.read_csv(HERE / 'scored_queries_final.csv', keep_default_na=False)
S = R[R.system == 'blend_0.5']
L = ['# Post-hoc descriptive analysis: product system v2.3 (blend 0.5)', '',
     '**Post-hoc. Descriptive only. Decides nothing.** The blend became the product system by the pre-registered decision '
     "rule after the test was seen, so the blend's independent-test numbers are selection numbers now. Source: "
     '`scored_queries_final.csv` (unchanged).', '',
     '## Blend 0.5 minus stacked ranker (paired bootstrap, 10,000 resamples, seed 42)', '',
     '| subset | n | d hit@5 | d MRR |', '|---|---|---|---|']
subsets = [('pooled', list(S.query_id))] + [(f'{s} only', list(S[S.set == s].query_id)) for s in sf.SET_ORDER] + \
          [(f'without {s}', list(S[S.set != s].query_id)) for s in sf.SET_ORDER]
for lab, keys in subsets:
    L.append(f"| {lab} | {len(keys)} | {sf.f3(sf.paired(R, 'blend_0.5', 'stacked', 'hit@5', keys))} | "
             f"{sf.f3(sf.paired(R, 'blend_0.5', 'stacked', 'mrr', keys))} |")
L += ['', '## Blend 0.5 by group (1,000 resamples)', '', '| group | n | hit@5 | MRR |', '|---|---|---|---|']
for g, x in S.groupby('group'):
    L.append(f"| {g} | {len(x)} | {sf.m3(sf.boot_mean(x['hit@5'], sf.B_DESC))} | {sf.m3(sf.boot_mean(x['mrr'], sf.B_DESC))} |")
L += ['', '## Blend 0.5 error causes by set (queries with no gold family in the top 5)', '',
      '| set | n | misses | (a) no gold among candidates | (b) gold among candidates, below rank 5 | (c) every gold family < 2 papers |',
      '|---|---|---|---|---|---|']
for s in sf.SET_ORDER + ['all']:
    x = S if s == 'all' else S[S.set == s]
    m = x[x['hit@5'] == 0]
    L.append(f"| {s} | {len(x)} | {len(m)} | {int((m.miss_cause == 'a').sum())} | {int((m.miss_cause == 'b').sum())} | "
             f"{int((m.gold_all_lt2_papers.astype(str) == 'True').sum())} |")
(HERE / 'report_posthoc_v23.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('\n'.join(L))
