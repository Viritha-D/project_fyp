"""
recommend(query, k=5): benchmark families for a problem description, with notes.

Returns BENCHMARK FAMILIES only (no algorithm / strategy recommendation). Match confidence (cross-encoder
scores and the top-2 family margin) is reported separately from evidence strength (papers, venues).
When the margin gate fails the result is "not mapped" and the query is logged to
retrieval_v2/unmapped_queries_v2.csv.

Usage:  python retrieval_v2/recommend.py "<query>" [--k 5] [--no-log]
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hybrid  # noqa: E402

C = hybrid.CONFIG
_STATE = {}


def _load():
    if not _STATE:
        _STATE['index'] = hybrid.Index.from_config()
        fams = json.loads(hybrid.path(C['families']['families']).read_text(encoding='utf-8'))
        _STATE['families'] = {f['family_id']: f for f in fams}
        notes = json.loads(hybrid.path(C['families']['notes']).read_text(encoding='utf-8'))
        _STATE['fnotes'] = {n['family_id']: n for n in notes}
        enotes = json.loads(hybrid.path(C['entities']['notes']).read_text(encoding='utf-8'))
        _STATE['enotes'] = {n['entity_id']: n for n in enotes}
    return _STATE


def recommend(query, k=5, log_unmapped=True):
    st = _load()
    idx = st['index']
    res = idx.rank_full([query], hybrid.encode_queries([query]))[0]
    out = {'query': query, 'mapped': res['mapped'],
           'match_confidence': {'margin_top2_families': res['margin'],
                                'margin_threshold': C['retrieval']['margin_threshold']},
           'families': []}
    for f in res['families'][:k]:
        fam, note = st['families'][f['family_id']], st['fnotes'][f['family_id']]
        members = f['members'][:C['retrieval']['members_shown']]
        caveats = sorted({c for e, _ in members for c in st['enotes'][e]['evidence_caveats']})
        out['families'].append({
            'family_id': f['family_id'], 'family_name': fam['family_name'], 'family_kind': fam['family_kind'],
            'family_score': round(f['score'], 4),
            'match': {'best_member_cross_encoder': round(f['best_member_score'], 4),
                      'members': [{'entity_id': e, 'name': st['enotes'][e]['canonical_name'], 'score': round(s, 4)}
                                  for e, s in members]},
            'evidence': {'n_papers': fam['n_papers'], 'evidence_bonus': round(f['evidence_bonus'], 4),
                         'venues': {v: c for v, c in fam['venues'].items() if c},
                         'reuse_signals': fam['reuse_signals'], 'member_evidence_caveats': caveats},
            'note_text': note['note_text']})
    if not res['mapped']:
        out['result'] = 'not mapped'
        if log_unmapped:
            _log(query, res)
    return out


def _log(query, res):
    p = hybrid.path(C['unmapped_log'])
    new = not p.exists()
    with open(p, 'a', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['timestamp', 'query', 'margin', 'top_families'])
        top = '; '.join(f"{f['family_id']} ({f['score']:.3f})" for f in res['families'][:3])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec='seconds'), query,
                    '' if res['margin'] is None else round(res['margin'], 4), top])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--k', type=int, default=5)
    ap.add_argument('--no-log', action='store_true')
    a = ap.parse_args()
    r = recommend(a.query, a.k, log_unmapped=not a.no_log)
    m = r['match_confidence']['margin_top2_families']
    print(f'Query: {r["query"]}')
    print(f'Mapped: {r["mapped"]}  (margin between top-2 families: '
          f'{"n/a" if m is None else f"{m:.3f}"}; gate {r["match_confidence"]["margin_threshold"]})')
    if not r['mapped']:
        print('Result: NOT MAPPED (logged to unmapped_queries_v2.csv). Closest families, for reference only:')
    for i, f in enumerate(r['families'], 1):
        ev = f['evidence']
        print(f'\n{i}. {f["family_name"]}  [{f["family_kind"]}]  family score {f["family_score"]:.3f}')
        print('   match:    ' + '; '.join(f'{x["name"]} ({x["score"]:.2f})' for x in f['match']['members']))
        print(f'   evidence: {ev["n_papers"]} papers; venues {ev["venues"]}; signals {ev["reuse_signals"]}'
              + (f'; caveats {ev["member_evidence_caveats"]}' if ev['member_evidence_caveats'] else ''))
        print(f'   note:     {f["note_text"]}')


if __name__ == '__main__':
    sys.exit(main())
