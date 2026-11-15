"""
When the fallback fires.

Confidence comes only from values the frozen ranking already returns (recommend_v23 output):
- p1 = the stacked probability ("probability") of the blend's rank-1 family (0.0 if it has none);
- margin = p1 minus the probability of the rank-2 family (recorded, not used by the rule).
Low confidence: p1 < threshold, with the threshold read from selflearn/threshold.json (chosen on the development
queries queries_v2 only; see selflearn/tools/choose_threshold.py).

Feature-conflict trigger (fixed rule, no tunable value): the answer also counts as low confidence when the extracted
features conflict with every one of the top five families (matcher.conflicts_with_all), even in score band 1.

The learned store is never consulted here: no stored record, verified or not, counts as evidence for confidence.
"""

import json
from pathlib import Path

from .matcher import conflicts_with_all

THRESHOLD_FILE = Path(__file__).resolve().parent / 'threshold.json'


def confidence(ranking):
    fams = ranking['families']
    p = [f.get('probability') or 0.0 for f in fams[:2]] + [0.0, 0.0]
    return {'p1': float(p[0]), 'margin': float(p[0] - p[1])}


def load_threshold(path=THRESHOLD_FILE):
    return float(json.loads(Path(path).read_text(encoding='utf-8'))['threshold'])


def decide(ranking, qprof, profiles, threshold):
    """Returns {'triggered', 'low_confidence', 'feature_conflict', 'p1', 'margin', 'threshold'}."""
    c = confidence(ranking)
    low = c['p1'] < threshold
    top5 = [f['family_id'] for f in ranking['families'][:5]]
    conflict = conflicts_with_all(qprof, profiles, top5)
    return {'triggered': low or conflict, 'low_confidence': low, 'feature_conflict': conflict,
            'p1': c['p1'], 'margin': c['margin'], 'threshold': threshold}
