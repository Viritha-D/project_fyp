"""
Retrieval v2.1 components (see evaluation/PREREGISTRATION.md).

- excluded_entities(): index hygiene list (computed once from the published v2 files).
- clean_index(idx, train_rows, exclude): a hybrid.Index without the excluded entities (BM25 rebuilt, dense
  rows dropped, family n_papers over non-excluded training records).
- PaperKNN: paper-kNN family voting over paper_embeddings.npy rows of training papers.
- candidate_features(): candidate families (shortlist families U top-20 kNN families) with 8 features.
- Stacker: StandardScaler + LogisticRegression over those features.

hybrid.py (Part B) is not modified; it is only imported.
"""

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hybrid  # noqa: E402

C = hybrid.CONFIG
K_GRID = [10, 25, 50, 100]
KNN_CANDIDATES = 20
FEATURES = ['ce_best', 'bm25_best_rel', 'dense_best', 'knn_vote', 'log_n_papers',
            'kind_suite_or_series', 'kind_stem_group', 'kind_template_grid']
SUITE_KINDS = {'suite_series', 'numbered_series'}


# ---------------------------------------------------------------- 1. hygiene
def excluded_entities():
    notes = json.loads(hybrid.path(C['entities']['notes']).read_text(encoding='utf-8'))
    ents = json.loads(hybrid.path(C['entities']['descriptions']).read_text(encoding='utf-8'))
    bad = {n['entity_id'] for n in notes
           if re.sub(r'[^a-z0-9]', '', n['canonical_name'].lower()) in {'notreported', 'na', 'unknown'}}
    bad |= {e['entity_id'] for e in ents if 'extraction_artifact_suspect' in (e.get('flags') or [])}
    return bad


def clean_index(idx, train_rows, exclude):
    keep = [i for i, e in enumerate(idx.entity_ids) if e not in exclude]
    ids = [idx.entity_ids[i] for i in keep]
    tr = train_rows[~train_rows['entity_id'].isin(exclude)]
    fam_papers = tr.groupby('family_id')['paper_key'].nunique().to_dict()
    out = hybrid.Index(ids, [idx.desc[e] for e in ids], idx.emb[keep], idx.fam, fam_papers)
    out.members = {}
    for i, e in enumerate(ids):
        out.members.setdefault(out.fam[e], []).append(i)
    return out


def popularity_order(clean):
    fams = sorted(set(clean.fam[e] for e in clean.entity_ids), key=lambda f: (-clean.fam_papers.get(f, 0), f))
    return fams


# ---------------------------------------------------------------- 2. paper-kNN
class PaperKNN:
    """rows: master rows (with paper_key, family_id, entity_id) in master order, positions = row numbers into
    paper_embeddings.npy. Only the given rows are used (training rows)."""

    def __init__(self, emb_all, rows, exclude):
        pos = np.asarray(rows.index, dtype=int)
        pk = rows['paper_key'].to_numpy()
        codes, uniq = pd.factorize(pk)
        order = np.argsort(codes, kind='stable')
        self.pos, self.codes = pos[order], codes[order]
        self.starts = np.r_[0, np.flatnonzero(np.diff(self.codes)) + 1]
        self.papers = list(uniq)
        self.P = emb_all[self.pos]
        ok = rows[~rows['entity_id'].isin(exclude)]
        fams = ok.groupby('paper_key')['family_id'].apply(lambda s: sorted(set(s))).to_dict()
        self.paper_fams = [fams.get(p, []) for p in self.papers]

    def paper_sims(self, qvecs):
        S = qvecs @ self.P.T                         # queries x rows
        return np.maximum.reduceat(S, self.starts, axis=1)  # queries x papers (papers in self.papers order)

    def votes(self, psims_row, K, exclude_papers=None):
        s = psims_row
        if exclude_papers is not None:
            s = np.where(exclude_papers, -np.inf, s)
        top = np.argsort(-s, kind='stable')[:K]
        v = {}
        for j in top:
            if not np.isfinite(s[j]):
                break
            for f in self.paper_fams[j]:
                v[f] = v.get(f, 0.0) + float(s[j])
        return v


def ranked_votes(v):
    return [f for f, _ in sorted(v.items(), key=lambda x: (-x[1], x[0]))]


def choose_k(knn, train_papers, papers_df, qvec_of, gold_of, seed, n_inner=4):
    """Inner CV over the training papers: mean hit@5 of kNN voting per K; ties -> smaller K."""
    from sklearn.model_selection import StratifiedKFold
    p = papers_df[papers_df['paper_key'].isin(train_papers)].reset_index(drop=True).copy()
    p['stratum'] = p['Category'] + '|' + p['Conference']
    vc = p['stratum'].value_counts()
    p.loc[p['stratum'].map(vc) < n_inner, 'stratum'] = 'rare'
    pidx = {k: i for i, k in enumerate(knn.papers)}
    hits = {K: [] for K in K_GRID}
    for _, test in StratifiedKFold(n_inner, shuffle=True, random_state=seed).split(p, p['stratum']):
        inner_test = p.loc[test, 'paper_key'].tolist()
        mask = np.zeros(len(knn.papers), dtype=bool)
        mask[[pidx[k] for k in inner_test if k in pidx]] = True
        inner_fams = {f for j in np.flatnonzero(~mask) for f in knn.paper_fams[j]}
        qs = [k for k in inner_test if gold_of[k] & inner_fams]
        if not qs:
            continue
        PS = knn.paper_sims(np.stack([qvec_of[k] for k in qs]))
        for qi, k in enumerate(qs):
            gold = gold_of[k] & inner_fams
            for K in K_GRID:
                top5 = ranked_votes(knn.votes(PS[qi], K, mask))[:5]
                hits[K].append(float(any(f in gold for f in top5)))
    means = {K: (float(np.mean(h)) if h else 0.0) for K, h in hits.items()}
    best = max(K_GRID, key=lambda K: (means[K], -K))
    return best, means, len(hits[K_GRID[0]])


# ---------------------------------------------------------------- 3. candidates + features
def kind_onehot(kind):
    return [float(kind in SUITE_KINDS), float(kind == 'stem_group'), float(kind == 'template_grid')]


def candidate_features(clean, queries, qvecs, knn_votes, fam_kind):
    """Per query: list of candidate dicts {family_id, features..., in_shortlist}. Also returns the v2.1 full
    ranking (hygiene index; family score = best CE + evidence bonus) for reference."""
    ce = hybrid.cross_encoder()
    shortlists = [clean.shortlist(q, v) for q, v in zip(queries, qvecs)]
    pairs = [(q, clean.desc[e]) for q, sl in zip(queries, shortlists) for e in sl]
    s1 = ce.predict(pairs, batch_size=64, show_progress_bar=False) if pairs else []
    pos = {e: i for i, e in enumerate(clean.entity_ids)}
    out, extra_pairs, extra_ref, i = [], [], [], 0
    for qi, (q, v, sl) in enumerate(zip(queries, qvecs, shortlists)):
        sc = dict(zip(sl, map(float, s1[i:i + len(sl)])))
        i += len(sl)
        bm = clean.bm25.get_scores(hybrid.tokenize(q))
        bmax = float(bm.max()) if len(bm) else 0.0
        dn = clean.emb @ v
        cands = {}
        for e, s in sc.items():
            f = clean.fam[e]
            if f not in cands or s > cands[f]['ce_best']:
                cands[f] = {'family_id': f, 'best_member': e, 'ce_best': s, 'in_shortlist': True}
        for f in ranked_votes(knn_votes[qi])[:KNN_CANDIDATES]:
            if f in cands or f not in clean.members:
                continue
            j = max(clean.members[f], key=lambda j: (dn[j], -j))
            cands[f] = {'family_id': f, 'best_member': clean.entity_ids[j], 'ce_best': None, 'in_shortlist': False}
            extra_pairs.append((q, clean.desc[clean.entity_ids[j]]))
            extra_ref.append((qi, f))
        for f, c in cands.items():
            j = pos[c['best_member']]
            c['bm25_best_rel'] = float(bm[j]) / bmax if bmax > 0 else 0.0
            c['dense_best'] = float(dn[j])
            c['knn_vote'] = float(knn_votes[qi].get(f, 0.0))
            c['log_n_papers'] = math.log1p(clean.fam_papers.get(f, 0))
            c['kind_suite_or_series'], c['kind_stem_group'], c['kind_template_grid'] = kind_onehot(fam_kind[f])
        out.append(cands)
    if extra_pairs:
        s2 = ce.predict(extra_pairs, batch_size=64, show_progress_bar=False)
        for (qi, f), s in zip(extra_ref, s2):
            out[qi][f]['ce_best'] = float(s)
    full21 = []
    for cands in out:
        sl = [c for c in cands.values() if c['in_shortlist']]
        r = sorted(sl, key=lambda c: (-(c['ce_best'] + C['retrieval']['evidence_weight'] * c['log_n_papers']),
                                      c['family_id']))
        full21.append([c['family_id'] for c in r])
    return [list(c.values()) for c in out], full21


# ---------------------------------------------------------------- 3b. stacker
class Stacker:
    def __init__(self):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        self.model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))

    def fit(self, X, y):
        self.model.fit(np.asarray(X, float), np.asarray(y, int))
        return self

    def proba(self, X):
        return self.model.predict_proba(np.asarray(X, float))[:, 1]

    def export(self):
        sc, lr = self.model.named_steps['standardscaler'], self.model.named_steps['logisticregression']
        return {'features': FEATURES, 'mean': sc.mean_.tolist(), 'scale': sc.scale_.tolist(),
                'coef': lr.coef_[0].tolist(), 'intercept': float(lr.intercept_[0])}


def proba_from_export(m, X):
    z = (np.asarray(X, float) - np.asarray(m['mean'])) / np.asarray(m['scale'])
    return 1 / (1 + np.exp(-(z @ np.asarray(m['coef']) + m['intercept'])))


def tier(p, cuts):
    return 'low' if p < cuts[0] else ('medium' if p < cuts[1] else 'high')


def two_slate(cands_sorted, knn_vote_rank, fam_kind):
    """3 standard choices (highest kNN vote among suite/series families) + 2 specific matches (highest stacked
    excluding those). cands_sorted: stacked order (padded); knn_vote_rank: kNN ranked families."""
    std = [f for f in knn_vote_rank if fam_kind.get(f) in SUITE_KINDS][:3]
    for f in cands_sorted:
        if len(std) >= 3:
            break
        if f not in std:
            std.append(f)
    spec = [f for f in cands_sorted if f not in std][:2]
    return std + spec
