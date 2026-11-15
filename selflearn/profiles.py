"""
Benchmark-family feature profiles, built from the repository metadata (read-only).

Each record of papers_master_with_matching_text_v2.csv is turned into a feature profile by the same rule-based
extractor that reads queries, applied to its metadata fields. Two metadata-only rules (never applied to queries):

- category comes from the record's Category field (Pure Math -> pure_math, Applied -> applied);
- a record whose landscape is described (Landscape_Characteristics or Target_Landscape present) but that does not
  mention constraints counts as "unconstrained", and one that shows no multi-objective signal counts as "single".
  A query that does not state a feature leaves it "unknown".

A family profile holds, per feature, the counts of each value over its records with a known value; dimensionality is
the set of integers in the records' Dimensionality fields; landscape is the set of tags seen. Hygiene-excluded
entities (retrieval_v2/v21_model.json) are left out.
"""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .extract import extract_rules
from .schema import UNKNOWN

ROOT = Path(__file__).resolve().parent.parent
MISSING = {'', 'not reported', 'n/a', 'na', 'none', 'unknown', 'n/a (pure math problem)', 'none / pure synthetic', 'nan'}
CATEGORICAL = ('category', 'variable_type', 'objectives', 'separability', 'modality', 'constraints')


def _val(v):
    v = str(v or '').strip()
    return '' if v.lower() in MISSING else v


def record_profile(r):
    text = ' . '.join(_val(r.get(c)) for c in ('Benchmark_Name', 'Problem_Context', 'Landscape_Characteristics',
                                               'Target_Landscape', 'Modality', 'Separability', 'Dimensionality',
                                               'Performance_Metric', 'Evaluation_Dataset'))
    p = extract_rules(text)
    p['category'] = {'Pure Math': 'pure_math', 'Applied': 'applied'}.get(r.get('Category'), UNKNOWN)
    described = bool(_val(r.get('Landscape_Characteristics')) or _val(r.get('Target_Landscape')))
    if described and p['constraints'] == UNKNOWN:
        p['constraints'] = 'unconstrained'
    if described and p['objectives'] == UNKNOWN:
        p['objectives'] = 'single'
    dims = {int(x) for x in re.findall(r'(\d{1,6})', _val(r.get('Dimensionality'))) if 0 < int(x) < 10 ** 6}
    return p, dims


def build_family_profiles(root=ROOT):
    rows = list(csv.DictReader(open(root / 'papers_master_with_matching_text_v2.csv', encoding='utf-8')))
    emap = list(csv.DictReader(open(root / 'paper_to_entity_map_v2.csv', encoding='utf-8')))
    assert [m['paper_id'] for m in emap] == [r['Paper_ID'] for r in rows]
    e2f = {r['entity_id']: r['family_id'] for r in csv.DictReader(open(root / 'entity_to_family_v5.csv', encoding='utf-8'))}
    excluded = set(json.loads((root / 'retrieval_v2/v21_model.json').read_text(encoding='utf-8'))['excluded_entities'])
    fams = {f['family_id']: f for f in json.loads((root / 'families_v5.json').read_text(encoding='utf-8'))}
    prof = defaultdict(lambda: {'counts': {k: Counter() for k in CATEGORICAL}, 'dims': set(), 'landscape': Counter(),
                                'records': [], 'papers': set()})
    for i, (r, m) in enumerate(zip(rows, emap)):
        if m['entity_id'] in excluded:
            continue
        f = e2f[m['entity_id']]
        p, dims = record_profile(r)
        P = prof[f]
        for k in CATEGORICAL:
            if p[k] != UNKNOWN:
                P['counts'][k][p[k]] += 1
        P['dims'] |= dims
        P['landscape'].update(p['landscape'])
        P['records'].append(i)
        P['papers'].add(m['paper_key'])
    out = {}
    for f, P in prof.items():
        out[f] = {'family_id': f, 'family_name': fams[f]['family_name'], 'n_papers': fams[f]['n_papers'],
                  'counts': {k: dict(v) for k, v in P['counts'].items()}, 'dims': sorted(P['dims']),
                  'landscape': sorted(P['landscape']), 'records': P['records'],
                  'suite_memberships': fams[f].get('suite_memberships') or [],
                  'member_entity_ids': [e for e in fams[f]['member_entity_ids'] if e not in excluded]}
    return out


def majority(counts):
    """Most common value (ties broken alphabetically) and its share, or (UNKNOWN, 0.0) when nothing is known."""
    if not counts:
        return UNKNOWN, 0.0
    total = sum(counts.values())
    v = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return v[0], v[1] / total
