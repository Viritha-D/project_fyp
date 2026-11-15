"""
The fallback module: wraps an answer of the frozen v2.3 ranking (recommend_v23 output) without changing it.

answer(query, ranking, qvec) returns one of:
- out of scope (no optimisation vocabulary and no problem feature): message "this does not look like an
  optimisation problem", no shortlist, nothing stored;
- not triggered: the frozen ranking, unchanged, plus the extracted features (for display and correction);
- triggered (low confidence or feature conflict with all top five): the extracted features, a 3-5 item shortlist from
  the feature matcher (best first, labelled "closest available, not a confirmed match"; each item with matched,
  conflicting and unknown features and a source), earlier similar suggestions from the store labelled with their
  status, and the frozen ranking kept for reference. The new suggestion is added to the store as unverified unless the
  store is read-only.

The independent test queries and their gold labels are never read by this module.
"""

import csv
import json
from pathlib import Path

import numpy as np

from .extract import extract, in_scope
from .matcher import Matcher
from .profiles import build_family_profiles
from .store import Store
from .trigger import decide, load_threshold

ROOT = Path(__file__).resolve().parent.parent
OUT_OF_SCOPE = 'this does not look like an optimisation problem'


class Fallback:
    def __init__(self, store=None, threshold=None, load_embeddings=True, root=ROOT):
        self.profiles = build_family_profiles(root)
        self.threshold = load_threshold() if threshold is None else threshold
        self.store = store if store is not None else Store()
        ent_ids = emb = pemb = None
        if load_embeddings:
            ent_ids = (root / 'entity_ids_order_v2.txt').read_text(encoding='utf-8').splitlines()
            emb = np.load(root / 'entity_embeddings_v2.npy')
            pemb = np.load(root / 'paper_embeddings.npy')
        records = list(csv.DictReader(open(root / 'papers_master_with_matching_text_v2.csv', encoding='utf-8')))
        self.matcher = Matcher(self.profiles, ent_ids, emb, pemb, records)

    def answer(self, query, ranking=None, qvec=None, consent=False, write=True, profile=None):
        prof = profile or extract(query)
        if not in_scope(query, prof):
            return {'status': 'out_of_scope', 'message': OUT_OF_SCOPE, 'profile': prof, 'shortlist': [],
                    'ranking': None, 'stored': None}
        dec = decide(ranking, prof, self.profiles, self.threshold)
        if not dec['triggered']:
            return {'status': 'confident', 'profile': prof, 'decision': dec, 'ranking': ranking, 'shortlist': [],
                    'stored': None}
        rejected = self.store.rejected_for(prof)
        shortlist = self.matcher.match(prof, qvec, k=5, exclude=rejected)
        earlier = [c for c in self.store.candidates_for(prof) if c['family_id'] not in rejected]
        stored, why = (None, 'not written')
        if write and shortlist:
            stored, why = self.store.add(prof, shortlist, shortlist[0], query_text=query, consent=consent)
        return {'status': 'fallback', 'profile': prof, 'decision': dec, 'ranking': ranking, 'shortlist': shortlist,
                'earlier_suggestions': earlier, 'stored': stored['id'] if stored else None,
                'store_note': why, 'store_read_only': self.store.read_only}


def describe(result):
    """Plain-text summary for logs and the CLI."""
    return json.dumps({k: v for k, v in result.items() if k != 'ranking'}, indent=1, default=str)
