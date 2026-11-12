"""
Live mode: calls the product system v2.3 (blend 0.5, retrieval_v2/recommend_v23.py) unchanged and adds data-only
notes. Used by the local app (run_demo.sh) and by tools/build_gallery.py, so the gallery and the live app share one code
path.

The ranking is exactly recommend_v23.recommend_v23(query, k=5) (recommend_v21 with lambda 0.5, single-query path).
Nothing here changes it: notes, evidence papers and members are display-only and computed after the ranking.
"""

import sys
from pathlib import Path

import numpy as np

import core

ROOT = core.ROOT
for p in ('retrieval_v2', 'retrieval_v2/evaluation', 'retrieval_v2/v22'):
    sys.path.insert(0, str(ROOT / p))

_S = {}


def load():
    """Load the frozen recommender (after the hash check) and the note data, once."""
    if not _S:
        actual, expected, ok = core.frozen_hash_status()
        if not ok:
            raise RuntimeError(f'recommend_v23.py sha256 {actual} does not match FROZEN_HASHES_v23.txt ({expected}); '
                               'live mode refuses to run.')
        import hybrid
        import recommend_v21
        import recommend_v23
        recommend_v21._load()
        _S.update(rec=recommend_v23, hybrid=hybrid, hash=actual, notes=core.FamilyNotes(),
                  paper_emb=np.load(ROOT / 'paper_embeddings.npy'))
        _S['guard'] = core.TestQueryGuard(hybrid.encode_queries)
    return _S


def recommend(query):
    """Full result for the UI: the frozen top 5 plus display-only notes. Raises ValueError for blocked inputs."""
    s = load()
    blocked, cos = s['guard'].check(query)
    if blocked:
        raise ValueError('This text matches a held-out test query, so it is not run until the independent test has '
                         'been scored and reported.')
    out = s['rec'].recommend_v23(query, k=5)
    qv = s['hybrid'].encode_queries([query])[0]
    fams = []
    for f in out['families']:
        members_first = [m['entity_id'] for m in (f.get('members') or [])]
        note = s['notes'].build_note(f['family_id'], qv, s['paper_emb'], members_first)
        fams.append({'family_id': f['family_id'], 'family_name': f['family_name'], 'family_kind': f['family_kind'],
                     'ranker_score': f['probability'], 'note': note})
    return {'query': query, 'families': fams, 'tier': out['confidence']['tier'],
            'top1_score': out['confidence']['top1_score'], 'lambda': out['lambda'],
            'applied_share': core.applied_share_of_papers([f['note'] for f in fams]),
            'system_hash': s['hash'], 'timestamp': core.now_iso(), 'mode': 'live'}
