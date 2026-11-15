"""
Choose the low-confidence threshold on the DEVELOPMENT queries only (retrieval_v2/evaluation/queries_v2.csv).
The independent test queries and their gold labels are never read.

Rule (fixed before running): signal p1 = stacked probability of the blend 0.5 rank-1 family (recommend_v23,
single-query path, as used by the app). Candidates = midpoints between consecutive distinct p1 values. Choose the t
that maximises Youden's J = sensitivity + specificity - 1 for predicting a miss (no gold family in the top 5) by
p1 < t; ties go to the smaller t. Writes selflearn/threshold.json and prints how many development queries fall below.

Usage: python -m selflearn.tools.choose_threshold
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'retrieval_v2'), str(ROOT / 'retrieval_v2/evaluation'), str(ROOT / 'retrieval_v2/v22')]

from selflearn.extract import extract  # noqa: E402
from selflearn.matcher import conflicts_with_all  # noqa: E402
from selflearn.profiles import build_family_profiles  # noqa: E402
from selflearn.trigger import THRESHOLD_FILE, confidence  # noqa: E402

DEV = ROOT / 'retrieval_v2/evaluation/queries_v2.csv'


def main():
    import recommend_v23
    Q = list(csv.DictReader(open(DEV, encoding='utf-8')))
    profiles = build_family_profiles()
    rows = []
    for q in Q:
        out = recommend_v23.recommend_v23(q['query_text'], k=5)
        top5 = [f['family_id'] for f in out['families']]
        gold = {g.strip() for g in q['gold_families'].split(';') if g.strip()}
        c = confidence(out)
        rows.append({'query_id': q['query_id'], 'p1': c['p1'], 'margin': c['margin'], 'miss': not (gold & set(top5)),
                     'conflict': conflicts_with_all(extract(q['query_text']), profiles, top5)})
    vals = sorted({r['p1'] for r in rows})
    cands = [(a + b) / 2 for a, b in zip(vals, vals[1:])]
    n_miss, n_hit = sum(r['miss'] for r in rows), sum(not r['miss'] for r in rows)
    best = None
    for t in cands:
        tp = sum(r['miss'] and r['p1'] < t for r in rows)
        tn = sum((not r['miss']) and r['p1'] >= t for r in rows)
        j = tp / n_miss + tn / n_hit - 1
        if best is None or j > best[0] + 1e-12:
            best = (j, t, tp, tn)
    j, t, tp, tn = best
    below = [r for r in rows if r['p1'] < t]
    conflict = [r for r in rows if r['conflict']]
    union = [r for r in rows if r['p1'] < t or r['conflict']]
    data = {'threshold': round(t, 6), 'signal': 'p1 = stacked probability of the blend 0.5 rank-1 family (recommend_v23)',
            'rule': "maximise Youden's J (sensitivity + specificity - 1) for predicting a miss (no gold family in the "
                    'top 5) by p1 < t; candidates are midpoints between consecutive distinct p1 values; ties -> smaller t',
            'chosen_on': 'development queries only: retrieval_v2/evaluation/queries_v2.csv (55 queries; the v2.2 lambda '
                         'was also selected on this set). The independent test queries and gold were not read.',
            'date': str(date.today()), 'youden_j': round(j, 4),
            'dev_counts': {'queries': len(rows), 'misses': n_miss, 'hits': n_hit, 'below_threshold': len(below),
                           'misses_below': tp, 'hits_at_or_above': tn, 'feature_conflict_trigger': len(conflict),
                           'triggered_either': len(union)},
            'feature_conflict_rule': 'fixed a priori: fires when the extracted features conflict with every one of the '
                                     'top five families; no tunable value, so nothing was chosen for it'}
    THRESHOLD_FILE.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(data, indent=1))
    print('\np1 of the development queries (sorted):', [round(v, 4) for v in vals])


if __name__ == '__main__':
    sys.exit(main())
