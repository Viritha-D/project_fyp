"""
Part 7 (live) - full hybrid retrieval pipeline: embed a real user query, search,
fuse, and re-rank with a cross-encoder. Run this in YOUR OWN environment (not the
sandbox), since it needs to download two models from Hugging Face on first run.

Install first:
    pip install sentence-transformers rank_bm25 numpy pandas

CHANGE LOG (this version):
- Added evidence-weighted fusion. Part 9 evaluation found 5 of 8 'easy' test
  queries incorrectly matched a thin, single-paper entity over a well-evidenced
  canonical one with near-identical text (e.g. 'Sphere function' at 14 papers
  losing to 'Sphere function (fsphere)' at 1 paper, in 8 of 9 wrong results
  overall). Pure text similarity has no way to know one entity is far better
  attested than another. Fusion now blends THREE ranked signals (dense, sparse,
  evidence strength) instead of two -- RRF blends ranks rather than replacing
  signals, so this nudges toward better-evidenced entities without letting
  evidence fully override a genuine semantic mismatch.
"""

import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

with open('problem_entities.json', encoding='utf-8') as f:
    entities = json.load(f)
entity_embeddings = np.load('entity_embeddings.npy')

entity_ids = [e['entity_id'] for e in entities]
descriptions = [e['base_description'] for e in entities]
id_to_idx = {eid: i for i, eid in enumerate(entity_ids)}
ENTITIES = {e['entity_id']: e for e in entities}

# Must be the SAME model used to build entity_embeddings.npy in Part 3
embed_model = SentenceTransformer('all-mpnet-base-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


def tokenize(text):
    return re.findall(r'[a-z0-9]+', text.lower())


tokenized_corpus = [tokenize(d) for d in descriptions]
bm25 = BM25Okapi(tokenized_corpus)


def bm25_search(query_text, top_k=20):
    scores = bm25.get_scores(tokenize(query_text))
    top_idx = np.argsort(-scores)[:top_k]
    return [(entity_ids[i], float(scores[i])) for i in top_idx if scores[i] > 0]


def dense_search(query_text, top_k=20):
    query_vector = embed_model.encode(query_text, normalize_embeddings=True)
    sims = entity_embeddings @ query_vector
    top_idx = np.argsort(-sims)[:top_k]
    return [(entity_ids[i], float(sims[i])) for i in top_idx]


def evidence_ranking(candidate_entity_ids):
    """Ranks candidates by n_supporting_papers (descending) -- the third RRF signal."""
    scored = [(eid, ENTITIES[eid]['n_supporting_papers']) for eid in candidate_entity_ids if eid in ENTITIES]
    return sorted(scored, key=lambda x: -x[1])


def reciprocal_rank_fusion(rankings_list, k=60):
    fused_scores = {}
    for ranking in rankings_list:
        for rank, (entity_id, _) in enumerate(ranking, start=1):
            fused_scores[entity_id] = fused_scores.get(entity_id, 0) + 1 / (k + rank)
    return sorted(fused_scores.items(), key=lambda x: -x[1])


def diagnose_candidate_reach(query_text, expected_entity_id, top_k=20):
    """For a given query, check whether expected_entity_id is present at all in
    the raw dense_search / bm25_search results (before fusion, evidence
    weighting, or cross-encoder re-ranking touch anything). If it isn't in
    either list, no downstream fix (fusion weighting, evidence bonus, margin
    threshold) can ever surface it -- the failure is at the retrieval stage,
    not the ranking/confidence stage."""
    dense_results = dense_search(query_text, top_k=top_k)
    sparse_results = bm25_search(query_text, top_k=top_k)

    dense_hit = next(((rank, score) for rank, (eid, score) in enumerate(dense_results, start=1)
                       if eid == expected_entity_id), None)
    sparse_hit = next(((rank, score) for rank, (eid, score) in enumerate(sparse_results, start=1)
                        if eid == expected_entity_id), None)

    expected_name = ENTITIES.get(expected_entity_id, {}).get('canonical_name', '(unknown entity_id)')

    print(f'\nQuery: "{query_text}"')
    print(f'Expected: {expected_entity_id} ("{expected_name}")')
    if dense_hit:
        print(f'  dense_search:  FOUND at rank {dense_hit[0]}/{top_k}, score={dense_hit[1]:.4f}')
    else:
        print(f'  dense_search:  NOT FOUND in top {top_k}')
    if sparse_hit:
        print(f'  bm25_search:   FOUND at rank {sparse_hit[0]}/{top_k}, score={sparse_hit[1]:.4f}')
    else:
        print(f'  bm25_search:   NOT FOUND in top {top_k}')

    print(f'  dense_search top 5:  ' + ', '.join(
        f'{eid}({ENTITIES[eid]["canonical_name"]})={score:.3f}' for eid, score in dense_results[:5]))
    print(f'  bm25_search top 5:   ' + ', '.join(
        f'{eid}({ENTITIES[eid]["canonical_name"]})={score:.3f}' for eid, score in sparse_results[:5])
        if sparse_results else '  bm25_search top 5:   (no results)')

    return {'dense_hit': dense_hit, 'sparse_hit': sparse_hit}


def map_user_description(query_text, top_k_final=5, shortlist_size=10, margin_threshold=1.0):
    """The end-to-end function: user description -> ranked matched entities.
    1. Dense + sparse search
    2. Reciprocal rank fusion (dense + sparse + evidence strength) -> shortlist
    3. Cross-encoder re-ranks the shortlist for final precision
    4. Below-margin-threshold -> reports 'no confident match' rather than forcing a result

    Confidence is judged by MARGIN (top-1 cross-encoder score minus top-2), not an
    absolute cutoff -- ms-marco-MiniLM-L-6-v2 returns unbounded raw logits, so a
    fixed absolute threshold has no solid footing (matched pairs can score
    negative). margin_threshold=1.0 is a starting default, not yet validated
    against a labeled query set beyond the 20-query Part 9 held-out set.
    """
    dense_results = dense_search(query_text, top_k=20)
    sparse_results = bm25_search(query_text, top_k=20)
    candidate_ids = list({eid for eid, _ in dense_results} | {eid for eid, _ in sparse_results})
    evidence_results = evidence_ranking(candidate_ids)

    fused = reciprocal_rank_fusion([dense_results, sparse_results, evidence_results])[:shortlist_size]

    if not fused:
        return {'mapped': False, 'reason': 'no candidates found', 'results': []}

    pairs = [(query_text, descriptions[id_to_idx[eid]]) for eid, _ in fused]
    ce_scores = cross_encoder.predict(pairs)

    # Apply evidence adjustment HERE, at the stage that actually decides the winner.
    # The earlier fusion-stage evidence signal had zero effect on outcomes (confirmed:
    # identical margins before/after that fix on 3 of 8 failing cases) because
    # well-evidenced entities were already reaching the shortlist -- the cross-encoder
    # re-ranking, which makes the FINAL decision, never saw evidence at all.
    # alpha=0.5 is a starting point, NOT validated -- log(1+n_papers) gives roughly a
    # +1.35 bonus at 14 papers vs +0.35 at 1 paper (net ~1.0 point advantage), enough
    # to flip small-margin misses (e.g. Rosenbrock's 0.021 margin loss) but likely NOT
    # enough for larger-margin misses (e.g. DTLZ1's 2.063 margin loss to a thin entity)
    # without further tuning or investigating whether those are genuine semantic
    # ambiguity rather than a pure evidence-weighting gap.
    EVIDENCE_ALPHA = 0.5
    adjusted_scores = []
    for eid, ce_score in zip([e for e, _ in fused], ce_scores):
        n_papers = ENTITIES[eid]['n_supporting_papers']
        adjusted = float(ce_score) + EVIDENCE_ALPHA * np.log1p(n_papers)
        adjusted_scores.append(adjusted)

    reranked = sorted(zip([eid for eid, _ in fused], adjusted_scores), key=lambda x: -x[1])
    top_score = float(reranked[0][1])

    if len(reranked) < 2:
        is_mapped = False
        margin = None
    else:
        margin = top_score - float(reranked[1][1])
        is_mapped = margin >= margin_threshold

    results = []
    for eid, score in reranked[:top_k_final]:
        entity = ENTITIES[eid]
        results.append({
            'entity_id': eid,
            'canonical_name': entity['canonical_name'],
            'confidence': float(score),
            'n_supporting_papers': entity['n_supporting_papers'],
            'description_confidence': entity['description_confidence'],
        })

    return {'mapped': is_mapped, 'top_confidence': top_score, 'margin': margin, 'results': results}


if __name__ == '__main__':
    test_queries = [
        "I need to optimize battery charge equalization for an electric vehicle pack",
        "minimize a rugged multimodal function with many local minima",
        "simple unimodal sphere-shaped objective function, convex, single global optimum",
    ]
    for q in test_queries:
        result = map_user_description(q)
        margin = result.get('margin')
        print(f'\nQuery: "{q}"')
        print(f'Mapped: {result["mapped"]} (top confidence: {result.get("top_confidence", 0):.3f}, '
              f'margin over #2: {margin:.3f})' if margin is not None else
              f'Mapped: {result["mapped"]} (margin: n/a)')
        for r in result['results']:
            print(f"  -> {r['canonical_name']} (confidence={r['confidence']:.3f}, "
                  f"n_papers={r['n_supporting_papers']}, evidence={r['description_confidence']})")
