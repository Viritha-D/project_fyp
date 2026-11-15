"""
recommend_v23: the product system v2.3 = blend 0.5. This is a thin wrapper around the frozen v2.1/v2.2 code.

By the pre-registered decision rule of the final test (PREREGISTRATION_final_amendment1.md; outcome in RESULTS.md,
"Independent test"), blend λ = 0.5 replaces the stacked ranker as the product system. Nothing in the frozen code
changes; this file only fixes λ = 0.5:

- recommend_v23(query, k): recommend_v21.recommend_v21(query, k, lam=0.5). This is the single-query path used by the
  CLI and the demo app.
- rank_batch_v23(queries): the batched path used for the final test (score_final.py): recommend_v21.rank_batch, the
  full v2 shortlist roll-up from hybrid.Index.from_config().rank_full, and v22/blend.py at λ = 0.5, padded with
  hygiene popularity.

Same config (retrieval_v2/config.json) and model files. Hashes: retrieval_v2/evaluation/FROZEN_HASHES_v23.txt.
The confidence tier is still the stacked model's top-1 probability (frozen cut-offs). It was calibrated for the stacked
ranker and is not validated for v2.3.

Usage: python retrieval_v2/recommend_v23.py "<query>" [--k 5]
"""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / 'evaluation'), str(HERE / 'v22')]
import blend as v22blend  # noqa: E402
import hybrid  # noqa: E402
import recommend_v21 as r21  # noqa: E402

LAMBDA = 0.5
_S = {}


def recommend_v23(query, k=5, slate=False):
    return r21.recommend_v21(query, k=k, slate=slate, lam=LAMBDA)


def rank_batch_v23(queries):
    """Blend 0.5 family rankings for many queries, exactly as scored in the final test."""
    rb = r21.rank_batch(queries)
    st = r21._load()
    if 'idx' not in _S:
        _S['idx'] = hybrid.Index.from_config()
    import numpy as np
    full = _S['idx'].rank_full(list(queries), np.stack([x['qvec'] for x in rb]))
    return [v22blend.blend([f['family_id'] for f in fr['families']], list(x['cands']), LAMBDA, st['pop'])
            for x, fr in zip(rb, full)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--k', type=int, default=5)
    a = ap.parse_args()
    sys.argv = [sys.argv[0], a.query, '--k', str(a.k), '--lambda', str(LAMBDA)]
    r21.main()


if __name__ == '__main__':
    sys.exit(main())
