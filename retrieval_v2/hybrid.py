"""
Retrieval v2 core: hybrid entity retrieval rolled up to benchmark families.

Same components as Part 7 (part7_hybrid_retrieval.py / part7_live_pipeline_v2.py, which are not
modified or imported because they load the old files at import time): BM25 over the entity
descriptions (same tokenizer), dense search with all-mpnet-base-v2 over L2-normalised entity
embeddings, reciprocal rank fusion (k = 60), cross-encoder re-scoring of the shortlist and a margin
gate. New here: the result unit is the FAMILY. Family score = best member cross-encoder score +
evidence_weight * log1p(family n_papers); the margin gate compares the top-2 families.

No strategy / algorithm-recommendation output is used anywhere.
"""

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((Path(__file__).resolve().parent / 'config.json').read_text(encoding='utf-8'))
_MODELS = {}


def path(rel):
    return ROOT / rel


def tokenize(text):
    return re.findall(r'[a-z0-9]+', str(text).lower())


def embed_model():
    if 'embed' not in _MODELS:
        from sentence_transformers import SentenceTransformer
        _MODELS['embed'] = SentenceTransformer(CONFIG['models']['embed'])
    return _MODELS['embed']


def cross_encoder():
    if 'ce' not in _MODELS:
        from sentence_transformers import CrossEncoder
        _MODELS['ce'] = CrossEncoder(CONFIG['models']['cross_encoder'])
    return _MODELS['ce']


def encode_queries(texts):
    return embed_model().encode(list(texts), batch_size=64, normalize_embeddings=True, show_progress_bar=False,
                                convert_to_numpy=True).astype(np.float32)


def reciprocal_rank_fusion(rankings_list, k=60):
    """Part 7: RRF score = sum over rankings of 1 / (k + rank), rank starting at 1."""
    fused = {}
    for ranking in rankings_list:
        for rank, (eid, _) in enumerate(ranking, start=1):
            fused[eid] = fused.get(eid, 0) + 1 / (k + rank)
    return sorted(fused.items(), key=lambda x: -x[1])


class Index:
    """Entity index + family roll-up. Built from the published v2 files (from_config) or from a hold-out
    build of one evaluation fold (from_holdout)."""

    def __init__(self, entity_ids, descriptions, embeddings, entity_to_family, family_n_papers):
        from rank_bm25 import BM25Okapi
        assert embeddings.shape[0] == len(entity_ids) == len(descriptions)
        self.entity_ids = list(entity_ids)
        self.desc = dict(zip(entity_ids, descriptions))
        self.emb = embeddings
        self.fam = {e: entity_to_family[e] for e in entity_ids}
        self.fam_papers = family_n_papers
        self.bm25 = BM25Okapi([tokenize(d) for d in descriptions])
        self.r = CONFIG['retrieval']

    # ---- the published index ----
    @classmethod
    def from_config(cls):
        ents = json.loads(path(CONFIG['entities']['descriptions']).read_text(encoding='utf-8'))
        order = path(CONFIG['entities']['order']).read_text(encoding='utf-8').splitlines()
        assert order == [e['entity_id'] for e in ents]
        e2f = pd.read_csv(path(CONFIG['families']['entity_to_family']), dtype=str, keep_default_na=False)
        fams = json.loads(path(CONFIG['families']['families']).read_text(encoding='utf-8'))
        return cls(order, [e['base_description'] for e in ents], np.load(path(CONFIG['entities']['embeddings'])),
                   dict(zip(e2f.entity_id, e2f.family_id)), {f['family_id']: f['n_papers'] for f in fams})

    # ---- an evaluation fold ----
    @classmethod
    def from_holdout(cls, build_dir, train_rows):
        """train_rows: master rows of the training papers with entity_id, family_id and paper_key columns."""
        build_dir = Path(build_dir)
        ents = json.loads((build_dir / 'problem_entities_enriched.json').read_text(encoding='utf-8'))
        order = (build_dir / 'entity_ids_order.txt').read_text(encoding='utf-8').splitlines()
        assert order == [e['entity_id'] for e in ents]
        e2f = dict(zip(train_rows['entity_id'], train_rows['family_id']))
        fam_papers = train_rows.groupby('family_id')['paper_key'].nunique().to_dict()
        return cls(order, [e['base_description'] for e in ents], np.load(build_dir / 'entity_embeddings.npy'),
                   e2f, fam_papers)

    # ---- searches ----
    def bm25_search(self, query, top_k):
        scores = self.bm25.get_scores(tokenize(query))
        top = np.argsort(-scores)[:top_k]
        return [(self.entity_ids[i], float(scores[i])) for i in top if scores[i] > 0]

    def dense_search(self, qvec, top_k):
        sims = self.emb @ qvec
        top = np.argsort(-sims)[:top_k]
        return [(self.entity_ids[i], float(sims[i])) for i in top]

    def shortlist(self, query, qvec):
        fused = reciprocal_rank_fusion([self.dense_search(qvec, self.r['dense_top']),
                                        self.bm25_search(query, self.r['bm25_top'])], k=self.r['rrf_k'])
        return [e for e, _ in fused[:self.r['shortlist']]]

    def rollup(self, scored, bonus=True):
        """[(entity, score)] -> families sorted by family score (best member score + optional evidence bonus)."""
        best = {}
        for e, s in scored:
            f = self.fam[e]
            best.setdefault(f, []).append((e, float(s)))
        out = []
        for f, members in best.items():
            members.sort(key=lambda x: -x[1])
            ev = self.r['evidence_weight'] * math.log1p(self.fam_papers.get(f, 0)) if bonus else 0.0
            out.append({'family_id': f, 'score': members[0][1] + ev, 'best_member_score': members[0][1],
                        'evidence_bonus': ev, 'members': members})
        out.sort(key=lambda x: (-x['score'], x['family_id']))
        return out

    def gate(self, families):
        """Margin between the top-2 family scores. A single candidate family has no margin and counts as mapped."""
        if not families:
            return False, None
        if len(families) == 1:
            return True, None
        margin = families[0]['score'] - families[1]['score']
        return margin >= self.r['margin_threshold'], margin

    # ---- the full pipeline, for many queries at once ----
    def rank_full(self, queries, qvecs):
        shortlists = [self.shortlist(q, v) for q, v in zip(queries, qvecs)]
        pairs = [(q, self.desc[e]) for q, sl in zip(queries, shortlists) for e in sl]
        scores = cross_encoder().predict(pairs, batch_size=64, show_progress_bar=False) if pairs else []
        out, i = [], 0
        for sl in shortlists:
            sc = list(zip(sl, scores[i:i + len(sl)]))
            i += len(sl)
            fams = self.rollup(sc, bonus=True)
            mapped, margin = self.gate(fams)
            out.append({'families': fams, 'mapped': mapped, 'margin': margin})
        return out

    # ---- baselines ----
    def rank_bm25_only(self, query, top_k=50):
        return self.rollup(self.bm25_search(query, top_k), bonus=False)

    def rank_dense_only(self, qvec, top_k=50):
        return self.rollup(self.dense_search(qvec, top_k), bonus=False)

    def rank_popularity(self):
        fams = sorted(set(self.fam.values()), key=lambda f: (-self.fam_papers.get(f, 0), f))
        return [{'family_id': f, 'score': float(self.fam_papers.get(f, 0)), 'members': []} for f in fams]
