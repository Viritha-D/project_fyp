"""Retrieval v2.2: weighted reciprocal-rank blend of the full v2 and stacked v2.1 family rankings."""

LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0]
RRF_K = 60


def blend(r_full, r_stacked, lam, pad, n=10, k=RRF_K):
    """score = (1-lam)/(k+rank_full) + lam/(k+rank_stacked); a family missing from a list gets nothing from it.
    Union sorted by score (desc, ties family_id), then padded to n with `pad` (popularity order)."""
    score = {}
    for w, lst in ((1 - lam, r_full), (lam, r_stacked)):
        for r, f in enumerate(lst, start=1):
            score[f] = score.get(f, 0.0) + w / (k + r)
    ranked = [f for f, s in sorted(score.items(), key=lambda x: (-x[1], x[0])) if s > 0]
    seen = set(ranked)
    return (ranked + [f for f in pad if f not in seen])[:max(n, len(ranked))]
