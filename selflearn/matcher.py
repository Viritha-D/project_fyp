"""
Match an extracted feature profile against benchmark-family profiles (selflearn.profiles).

Per query feature that is known (n_objectives is shown but not compared; objectives covers it):
- family has no information           -> "unknown"   (lowers the score by UNKNOWN_PENALTY)
- equal to the family's majority value -> "matched"   (+1)
- otherwise                            -> "conflicting" (-1)
- certain conflict -> the family is removed: objectives known on both sides, the family unanimous over its records,
  and different from the query (e.g. a single-objective benchmark for a multi-objective problem). Nothing else removes.
Dimensionality: matched if a family dimension lies within [d/2, 2d] ("high": any family dimension >= 100), conflicting
if the family lists dimensions and none does. Landscape tags: matched if the family has the tag, otherwise unknown
(absence is not a conflict).

score = feature_score / n_known_query_features (0 when none known) + cosine, where cosine is the best dense
similarity between the query vector and a member entity (all-mpnet-base-v2 entity embeddings; 0 without a vector).
The weights are fixed a priori; nothing is tuned.
"""

import numpy as np

from .profiles import CATEGORICAL, majority
from .schema import UNKNOWN, known

UNKNOWN_PENALTY = 0.25
BEST_LABEL = 'closest available, not a confirmed match'


def compare(qprof, fprof):
    """Returns (matched, conflicting, unknown, certain_conflict) lists of feature names."""
    matched, conflicting, unknown, certain = [], [], [], False
    for k, qv in known(qprof).items():
        if k == 'n_objectives':
            continue
        if k in CATEGORICAL:
            counts = fprof['counts'].get(k, {})
            fv, share = majority(counts)
            if fv == UNKNOWN:
                unknown.append(k)
            elif qv == fv:
                matched.append(k)
            else:
                conflicting.append(k)
                if k == 'objectives' and share == 1.0:
                    certain = True
        elif k == 'dimensionality':
            dims = fprof.get('dims', [])
            if not dims:
                unknown.append(k)
            elif (qv == 'high' and any(d >= 100 for d in dims)) or \
                    (isinstance(qv, int) and any(qv / 2 <= d <= qv * 2 for d in dims)):
                matched.append(k)
            else:
                conflicting.append(k)
        elif k == 'landscape':
            for tag in qv:
                (matched if tag in fprof.get('landscape', []) else unknown).append(f'landscape:{tag}')
    return matched, conflicting, unknown, certain


def feature_score(qprof, matched, conflicting, unknown):
    n = sum(1 for k in known(qprof) if k != 'n_objectives') + max(0, len(qprof['landscape']) - 1)
    if n == 0:
        return 0.0
    return (len(matched) - len(conflicting) - UNKNOWN_PENALTY * len(unknown)) / n


class Matcher:
    def __init__(self, profiles, entity_ids=None, entity_emb=None, paper_emb=None, records=None):
        self.profiles = profiles
        self.entity_pos = {e: i for i, e in enumerate(entity_ids)} if entity_ids is not None else {}
        self.entity_emb, self.paper_emb, self.records = entity_emb, paper_emb, records

    def cosine(self, f, qvec):
        if qvec is None or self.entity_emb is None:
            return 0.0
        idx = [self.entity_pos[e] for e in self.profiles[f]['member_entity_ids'] if e in self.entity_pos]
        return float((self.entity_emb[idx] @ qvec).max()) if idx else 0.0

    def source(self, f, qvec):
        """The family's closest evidence paper (title, conference, year) by dense cosine, else its first record."""
        recs = self.profiles[f]['records']
        if not recs or self.records is None:
            return None
        i = recs[0]
        if qvec is not None and self.paper_emb is not None:
            i = max(recs, key=lambda j: float(self.paper_emb[j] @ qvec))
        r = self.records[i]
        return {'title': r['Paper_Title'], 'conference': r['Conference'], 'year': r['Year']}

    def match(self, qprof, qvec=None, k=5, exclude=()):
        scored = []
        for f, fp in self.profiles.items():
            if f in exclude:
                continue
            m, c, u, certain = compare(qprof, fp)
            if certain:
                continue
            s = feature_score(qprof, m, c, u) + self.cosine(f, qvec)
            scored.append((s, f, m, c, u))
        scored.sort(key=lambda x: (-x[0], -self.profiles[x[1]]['n_papers'], x[1]))
        out = []
        for rank, (s, f, m, c, u) in enumerate(scored[:k], 1):
            out.append({'family_id': f, 'family_name': self.profiles[f]['family_name'], 'score': round(s, 4),
                        'n_papers': self.profiles[f]['n_papers'], 'matched': m, 'conflicting': c, 'unknown': u,
                        'source': self.source(f, qvec), 'label': BEST_LABEL if rank == 1 else ''})
        return out


def conflicts_with_all(qprof, profiles, family_ids):
    """True when every listed family has at least one conflicting feature with the query (and the query states at
    least one comparable feature)."""
    if not [k for k in known(qprof) if k not in ('n_objectives', 'landscape')]:
        return False
    return all(compare(qprof, profiles[f])[1] or compare(qprof, profiles[f])[3] for f in family_ids if f in profiles) \
        and any(f in profiles for f in family_ids)
