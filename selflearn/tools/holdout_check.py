"""
Post-hoc, descriptive hold-out check of the fallback matcher on the DEVELOPMENT queries only (queries_v2).
It states no accuracy for the module. The independent test queries and their gold labels are never read.

For each family that is gold for at least one development query: remove that family from the matcher's in-memory
candidates, run the matcher (as if the fallback had fired; nothing is stored) for the queries that list it as gold,
and record whether the shortlist (5 families) holds
  (g) a family of the same group: one sharing a suite membership with the removed family (families_v5.json), or
  (k) a family sharing the key features: equal majority values on every key feature (category, variable type,
      objectives, constraints) known for the removed family, with at least 2 such features known.

Also writes selflearn/review_pack.csv for human reviewers: per development query, the union of the v2.3 top 5 and the
module shortlist, in a fixed shuffled order, with an empty judgement column and no indication of the source; the key
(which entry came from where) is written to selflearn/review_pack_key.csv for unblinding after review.

Usage: python -m selflearn.tools.holdout_check
"""

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'retrieval_v2'), str(ROOT / 'retrieval_v2/evaluation'), str(ROOT / 'retrieval_v2/v22')]

from selflearn.extract import extract  # noqa: E402
from selflearn.fallback import Fallback  # noqa: E402
from selflearn.profiles import majority  # noqa: E402
from selflearn.schema import KEY_FEATURES  # noqa: E402
from selflearn.store import Store  # noqa: E402

DEV = ROOT / 'retrieval_v2/evaluation/queries_v2.csv'
OUT = ROOT / 'selflearn'


def suite_cues(fp):
    return {d['cue'] if isinstance(d, dict) else str(d) for d in fp['suite_memberships']}


def key_values(fp):
    return {k: majority(fp['counts'].get(k, {}))[0] for k in KEY_FEATURES if majority(fp['counts'].get(k, {}))[0] != 'unknown'}


def main():
    import hybrid
    import recommend_v23
    Q = list(csv.DictReader(open(DEV, encoding='utf-8')))
    fb = Fallback(store=Store(read_only=True))
    P = fb.profiles
    qv = dict(zip([q['query_id'] for q in Q], hybrid.encode_queries([q['query_text'] for q in Q])))
    prof = {q['query_id']: extract(q['query_text']) for q in Q}
    by_family = defaultdict(list)
    for q in Q:
        for g in (x.strip() for x in q['gold_families'].split(';')):
            if g:
                by_family[g].append(q['query_id'])
    rows = []
    for f, qids in sorted(by_family.items()):
        if f not in P:
            continue
        kv = key_values(P[f])
        suites = suite_cues(P[f])
        for qid in qids:
            short = fb.matcher.match(prof[qid], qv[qid], k=5, exclude={f})
            ids = [s['family_id'] for s in short]
            same_group = bool(suites) and any(suites & suite_cues(P[s]) for s in ids)
            same_keys = len(kv) >= 2 and any(all(key_values(P[s]).get(k) == v for k, v in kv.items()) for s in ids)
            rows.append({'removed_family': f, 'family_name': P[f]['family_name'], 'query_id': qid,
                         'removed_family_has_suite': bool(suites), 'key_features_known': len(kv),
                         'same_group': same_group, 'shares_key_features': same_keys,
                         'either': same_group or same_keys, 'shortlist': ';'.join(ids)})
    with open(OUT / 'holdout_check.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    tab = [('removed-family / query pairs', n, ''),
           ('removed family has a suite membership', sum(r['removed_family_has_suite'] for r in rows), ''),
           ('removed family has >= 2 key features known', sum(r['key_features_known'] >= 2 for r in rows), ''),
           ('shortlist holds a same-group family', sum(r['same_group'] for r in rows),
            f"of {sum(r['removed_family_has_suite'] for r in rows)} pairs where a group exists"),
           ('shortlist holds a family sharing the key features', sum(r['shares_key_features'] for r in rows),
            f"of {sum(r['key_features_known'] >= 2 for r in rows)} pairs where >= 2 key features are known"),
           ('either', sum(r['either'] for r in rows), f'of {n}')]
    print('Post-hoc, descriptive, development queries only (queries_v2). No accuracy is claimed for the module.\n')
    print('| measure | count | note |\n|---|---|---|')
    for a, b, c in tab:
        print(f'| {a} | {b} | {c} |')
    print(f'\ndistinct removed families: {len({r["removed_family"] for r in rows})}; development queries involved: '
          f'{len({r["query_id"] for r in rows})}')
    # review pack (blind)
    rng = random.Random(42)
    pack, key = [], []
    for q in Q:
        top5 = [x['family_id'] for x in recommend_v23.recommend_v23(q['query_text'], k=5)['families']]
        mod = [s['family_id'] for s in fb.matcher.match(prof[q['query_id']], qv[q['query_id']], k=5)]
        union = list(dict.fromkeys(top5 + mod))
        rng.shuffle(union)
        for f in union:
            pack.append({'query_id': q['query_id'], 'query_text': q['query_text'], 'family': P[f]['family_name'] if f in P else f,
                         'judgement': ''})
            key.append({'query_id': q['query_id'], 'family_id': f, 'in_v23_top5': f in top5, 'in_module_shortlist': f in mod})
    for path, data in ((OUT / 'review_pack.csv', pack), (OUT / 'review_pack_key.csv', key)):
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    print(f'\nreview_pack.csv: {len(pack)} rows for {len(Q)} development queries (judgement column empty; source hidden). '
          f'Key for unblinding: review_pack_key.csv')


if __name__ == '__main__':
    sys.exit(main())
