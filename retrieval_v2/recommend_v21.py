"""
recommend_v21(query, k=5): benchmark families for a problem description (retrieval v2.1).

Hygiene index (no "Not Reported" / artifact entities) + paper-kNN voting + stacked logistic ranker
(retrieval_v2/v21_model.json, fitted by evaluation/evaluate_v21.py as pre-registered). There is no
"not mapped" output: every answer carries a confidence tier (low / medium / high) from the ranker's
probability that the top-1 family is right; "low" is shown as LOW EVIDENCE. Benchmarks only, no algorithm
recommendation.

Usage:  python retrieval_v2/recommend_v21.py "<query>" [--k 5] [--slate]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'evaluation'))
import hybrid  # noqa: E402
import v21  # noqa: E402

C = hybrid.CONFIG
_S = {}


def _load():
    if not _S:
        import evaluate as ev
        rows, _, fams = ev.load()
        m = json.loads((Path(__file__).resolve().parent / 'v21_model.json').read_text(encoding='utf-8'))
        exclude = set(m['excluded_entities'])
        _S.update(model=m, fams=fams, kind={f: x['family_kind'] for f, x in fams.items()},
                  clean=v21.clean_index(hybrid.Index.from_config(), rows, exclude),
                  knn=v21.PaperKNN(np.load(hybrid.path('paper_embeddings.npy')), rows, exclude),
                  fnotes={n['family_id']: n for n in json.loads(hybrid.path(C['families']['notes']).read_text(encoding='utf-8'))})
        _S['pop'] = v21.popularity_order(_S['clean'])
    return _S


def rank_batch(queries):
    """Stacked v2.1 ranking for many queries (the same computation recommend_v21 uses for one)."""
    s = _load()
    m = s['model']
    QV = hybrid.encode_queries(queries)
    PS = s['knn'].paper_sims(QV)
    votes = [s['knn'].votes(PS[i], m['K']) for i in range(len(queries))]
    cands_all, _ = v21.candidate_features(s['clean'], queries, QV, votes, s['kind'])
    out = []
    for qv, cands, v in zip(QV, cands_all, votes):
        p = v21.proba_from_export(m['stacker'], [[c[f] for f in v21.FEATURES] for c in cands])
        for c, pi in zip(cands, p):
            c['prob'] = float(pi)
        cands.sort(key=lambda c: (-c['prob'], c['family_id']))
        by = {c['family_id']: c for c in cands}
        order = [c['family_id'] for c in cands] + [f for f in s['pop'] if f not in by]
        top1 = cands[0]['prob'] if cands else 0.0
        out.append({'qvec': qv, 'cands': by, 'order': order, 'votes': v, 'knn_order': v21.ranked_votes(v),
                    'top1_prob': top1, 'tier': v21.tier(top1, m['tier_cuts'])})
    return out


def recommend_v21(query, k=5, slate=False):
    s = _load()
    m = s['model']
    r = rank_batch([query])[0]
    by, order, top1, t = r['cands'], r['order'], r['top1_prob'], r['tier']
    if slate:
        order = v21.two_slate(order, r['knn_order'], s['kind'])
    out = {'query': query, 'confidence': {'top1_probability': round(top1, 4), 'tier': t,
                                          'label': 'LOW EVIDENCE' if t == 'low' else t, 'tier_cuts': m['tier_cuts']},
           'families': []}
    for i, f in enumerate(order[:k]):
        fam, c = s['fams'][f], by.get(f)
        out['families'].append({
            'family_id': f, 'family_name': fam['family_name'], 'family_kind': fam['family_kind'],
            'slot': ('standard choice' if i < 3 else 'specific match') if slate else None,
            'probability': None if c is None else round(c['prob'], 4),
            'match': None if c is None else {'best_member': c['best_member'],
                                             'cross_encoder': round(c['ce_best'], 4), 'knn_vote': round(c['knn_vote'], 4)},
            'evidence': {'n_papers': fam['n_papers'], 'venues': {v: n for v, n in fam['venues'].items() if n},
                         'reuse_signals': fam['reuse_signals']},
            'note_text': s['fnotes'][f]['note_text']})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--k', type=int, default=5)
    ap.add_argument('--slate', action='store_true', help='3 standard choices + 2 specific matches')
    a = ap.parse_args()
    r = recommend_v21(a.query, a.k, a.slate)
    c = r['confidence']
    print(f'Query: {r["query"]}\nConfidence: {c["label"]} (p(top-1 correct) = {c["top1_probability"]:.3f}; '
          f'tiers {c["tier_cuts"][0]:.3f} / {c["tier_cuts"][1]:.3f})')
    for i, f in enumerate(r['families'], 1):
        slot = f' ({f["slot"]})' if f['slot'] else ''
        pr = '-' if f['probability'] is None else f'{f["probability"]:.3f}'
        print(f'\n{i}. {f["family_name"]}  [{f["family_kind"]}]{slot}  p={pr}')
        if f['match']:
            print(f'   match:    {f["match"]["best_member"]} (CE {f["match"]["cross_encoder"]:.2f}, kNN vote {f["match"]["knn_vote"]:.2f})')
        ev = f['evidence']
        print(f'   evidence: {ev["n_papers"]} papers; venues {ev["venues"]}; signals {ev["reuse_signals"]}')
        print(f'   note:     {f["note_text"]}')


if __name__ == '__main__':
    sys.exit(main())
