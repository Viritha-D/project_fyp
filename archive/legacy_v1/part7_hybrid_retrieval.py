import json
import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
import re

with open('problem_entities.json', encoding='utf-8') as f:
    entities = json.load(f)
entity_embeddings = np.load('entity_embeddings.npy')

entity_ids = [e['entity_id'] for e in entities]
descriptions = [e['base_description'] for e in entities]
id_to_idx = {eid: i for i, eid in enumerate(entity_ids)}

assert entity_embeddings.shape[0] == len(entities), "Embeddings and entity list must be row-aligned"

# ---- Sparse index: BM25 over entity descriptions ----
def tokenize(text):
    return re.findall(r'[a-z0-9]+', text.lower())

tokenized_corpus = [tokenize(d) for d in descriptions]
bm25 = BM25Okapi(tokenized_corpus)

def bm25_search(query_text, top_k=20):
    scores = bm25.get_scores(tokenize(query_text))
    top_idx = np.argsort(-scores)[:top_k]
    return [(entity_ids[i], float(scores[i])) for i in top_idx if scores[i] > 0]

# ---- Dense index: cosine similarity over entity embeddings ----
# (embeddings are pre-normalized, so dot product == cosine similarity)
def dense_search_by_vector(query_vector, top_k=20):
    sims = entity_embeddings @ query_vector
    top_idx = np.argsort(-sims)[:top_k]
    return [(entity_ids[i], float(sims[i])) for i in top_idx]

def dense_search_by_entity(query_entity_id, top_k=20):
    """For testing the mechanism without a live embedding model: use an existing
    entity's own embedding as a stand-in query. In production, replace this with
    a freshly-embedded user query vector (see part7_embed_query.py)."""
    idx = id_to_idx[query_entity_id]
    return dense_search_by_vector(entity_embeddings[idx], top_k)

# ---- Fusion: Reciprocal Rank Fusion ----
def reciprocal_rank_fusion(rankings_list, k=60):
    """rankings_list: list of [(entity_id, score), ...] lists, already sorted best-first.
    RRF score = sum over rankings of 1 / (k + rank), rank starting at 1."""
    fused_scores = {}
    for ranking in rankings_list:
        for rank, (entity_id, _) in enumerate(ranking, start=1):
            fused_scores[entity_id] = fused_scores.get(entity_id, 0) + 1 / (k + rank)
    return sorted(fused_scores.items(), key=lambda x: -x[1])

def hybrid_search(dense_results, sparse_results, top_k=10):
    fused = reciprocal_rank_fusion([dense_results, sparse_results])
    return fused[:top_k]

# ============================================================
# Validation 1: BM25 sanity check with a real free-text query
# ============================================================
print('=== BM25 sparse search test ===')
test_query = "hybrid differential evolution algorithm for meal delivery scheduling"
results = bm25_search(test_query, top_k=5)
for eid, score in results:
    print(f'  {eid}  score={score:.2f}  "{descriptions[id_to_idx[eid]][:70]}..."')
print()

# ============================================================
# Validation 2: dense retrieval mechanism sanity check
# (using an entity's own embedding as a stand-in for a live query embedding)
# ============================================================
print('=== Dense search mechanism test (using ZDT1 entity as stand-in query) ===')
zdt1_id = [e['entity_id'] for e in entities if e['canonical_name'] == 'ZDT1'][0]
dense_results = dense_search_by_entity(zdt1_id, top_k=5)
for eid, score in dense_results:
    print(f'  {eid}  sim={score:.3f}  "{descriptions[id_to_idx[eid]][:70]}..."')
print()

# ============================================================
# Validation 3: fusion logic sanity check
# ============================================================
print('=== RRF fusion test (combining the two rankings above) ===')
sparse_for_zdt1 = bm25_search("ZDT1 multi-objective test function", top_k=10)
dense_for_zdt1 = dense_search_by_entity(zdt1_id, top_k=10)
fused = hybrid_search(dense_for_zdt1, sparse_for_zdt1, top_k=5)
for eid, score in fused:
    print(f'  {eid}  fused_score={score:.4f}  "{descriptions[id_to_idx[eid]][:70]}..."')
