"""
Entity-to-entity dedup audit: finish what Part 4 started one level up.

Part 4 clustered PAPERS into entities. This clusters ENTITIES against each
other (within the same Category, since cross-category matches are guaranteed
non-matches per the original blocking rule) to surface likely duplicate/
near-duplicate entities -- the TSP spelling-variant pattern
(Salesman/Salesperson, Traveling/Travelling) that split retrieval's "vote"
across many entities instead of one.

This does NOT merge anything automatically. High cosine similarity alone
isn't enough to decide -- entities can be legitimately distinct despite
near-identical text (e.g. numbered function families like DTLZ1 vs DTLZ2,
or specific named benchmark instances like "TSP (bays29)"), as the manual
TSP investigation showed. So candidate pairs are flagged with a heuristic
is_likely_numbered_variant marker (names differing only by a digit swap --
DTLZ1 vs DTLZ2 pattern, established as usually legitimate) to help a human
reviewer triage quickly, but every pair still needs a human look at aliases/
Dataset_Name before merging, same discipline as the TSP case.

Output: entity_dedup_candidates.csv, sorted by similarity descending.
"""

import json
import re
import numpy as np
import pandas as pd

ENTITIES_PATH = 'problem_entities.json'
EMB_PATH = 'entity_embeddings.npy'
SIM_THRESHOLD = 0.95  # near-identical text similarity; keeps the review list precise
OUTPUT_CSV = 'entity_dedup_candidates.csv'

with open(ENTITIES_PATH, encoding='utf-8') as f:
    entities = json.load(f)
emb = np.load(EMB_PATH)
assert emb.shape[0] == len(entities)

entity_ids = [e['entity_id'] for e in entities]
by_id = {e['entity_id']: e for e in entities}


def digit_stripped(name):
    s = re.sub(r'\d+', '#', str(name))
    return re.sub(r'[^a-z#]', '', s.lower())


TRAILING_MODIFIER_RE = re.compile(
    r'^(.*?)\s*(?:\bon\b|\bfor\b|-|\()\s*[A-Z0-9][\w .]*\)?$'
)


def strip_trailing_modifier(name):
    """Strip a final ' on X' / ' for X' / ' - X' / ' (X)' clause -- the pattern
    behind the false-positive bug-prediction-per-codebase pairs (same family,
    different specific target/instance, not a duplicate). Falls back to the
    full name if no such clause is found."""
    m = TRAILING_MODIFIER_RE.match(str(name))
    return m.group(1).strip().lower() if m else str(name).strip().lower()


WORD_RE = re.compile(r'[a-z0-9]+')


def name_word_jaccard(a, b):
    """Word-level Jaccard overlap between two names -- high for true synonym
    pairs (Salesman/Salesperson share nearly every word), low when the names
    differ in a substantive noun (different algorithm, different metric)."""
    wa, wb = set(WORD_RE.findall(a.lower())), set(WORD_RE.findall(b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


# parent/child pairs are intentional relationships, not duplicates -- exclude
parent_child_pairs = set()
for e in entities:
    if e['parent_benchmark_id']:
        parent_child_pairs.add(frozenset({e['entity_id'], e['parent_benchmark_id']}))

rows = []
for category in ['Pure Math', 'Applied']:
    idxs = [i for i, e in enumerate(entities) if e['category'] == category]
    sub_emb = emb[idxs]
    sims = sub_emb @ sub_emb.T
    n = len(idxs)
    for a in range(n):
        for b in range(a + 1, n):
            sim = sims[a, b]
            if sim < SIM_THRESHOLD:
                continue
            ea, eb = entities[idxs[a]], entities[idxs[b]]
            if frozenset({ea['entity_id'], eb['entity_id']}) in parent_child_pairs:
                continue
            numbered_variant = digit_stripped(ea['canonical_name']) == digit_stripped(eb['canonical_name']) \
                and ea['canonical_name'] != eb['canonical_name']
            named_instance_variant = (
                strip_trailing_modifier(ea['canonical_name']) == strip_trailing_modifier(eb['canonical_name'])
                and ea['canonical_name'] != eb['canonical_name']
            )
            desc_identical = ea['base_description'] == eb['base_description']
            name_overlap = round(name_word_jaccard(ea['canonical_name'], eb['canonical_name']), 3)
            rows.append({
                'similarity': round(float(sim), 4),
                'category': category,
                'entity_id_a': ea['entity_id'],
                'name_a': ea['canonical_name'],
                'n_papers_a': ea['n_supporting_papers'],
                'entity_id_b': eb['entity_id'],
                'name_b': eb['canonical_name'],
                'n_papers_b': eb['n_supporting_papers'],
                'is_likely_numbered_variant': numbered_variant,
                'is_likely_named_instance_variant': named_instance_variant,
                'base_description_identical': desc_identical,
                'name_word_overlap': name_overlap,
            })

report = pd.DataFrame(rows).sort_values('similarity', ascending=False)
report.to_csv(OUTPUT_CSV, index=False)

flagged_either = report['is_likely_numbered_variant'] | report['is_likely_named_instance_variant']
remaining = report[~flagged_either]

# True merge candidates: names are near-synonyms (high word overlap) -- the
# TSP Salesman/Salesperson pattern.
true_merge_candidates = remaining[remaining['name_word_overlap'] >= 0.6].sort_values(
    ['name_word_overlap', 'similarity'], ascending=False)

# Description-underspecified: identical embedded text but names share few
# words -- a different real entity hiding behind a too-generic description
# (needs enrichment, NOT merging).
needs_enrichment = remaining[
    (remaining['base_description_identical']) & (remaining['name_word_overlap'] < 0.4)
]
needs_enrichment_entities = sorted(set(needs_enrichment['entity_id_a']) | set(needs_enrichment['entity_id_b']))

print(f'Total same-category pairs above similarity {SIM_THRESHOLD}: {len(report)}')
print(f"  flagged as likely legitimate numbered variants (DTLZ1 vs DTLZ2-style): "
      f"{report['is_likely_numbered_variant'].sum()}")
print(f"  flagged as likely legitimate named-instance variants (...on Mylyn vs ...on Eclipse-style): "
      f"{report['is_likely_named_instance_variant'].sum()}")
print(f"  remaining after those two filters: {len(remaining)}")
print(f"    -> true merge candidates (name_word_overlap >= 0.6): {len(true_merge_candidates)}")
print(f"    -> description-underspecified, needs enrichment not merging "
      f"(identical description, name_word_overlap < 0.4): {len(needs_enrichment)} pairs, "
      f"{len(needs_enrichment_entities)} distinct entities")
print()
print(f'Full report saved to {OUTPUT_CSV}')
print()
print('=== TRUE MERGE CANDIDATES (near-synonym names, review before merging) ===')
for _, r in true_merge_candidates.head(30).iterrows():
    print(f"  sim={r['similarity']:.3f}  overlap={r['name_word_overlap']:.2f}  [{r['category']}]  "
          f"{r['entity_id_a']} \"{r['name_a']}\" ({r['n_papers_a']}p)  <->  "
          f"{r['entity_id_b']} \"{r['name_b']}\" ({r['n_papers_b']}p)")
print()
print('=== DESCRIPTION-UNDERSPECIFIED entities (need richer base_description, not merging) ===')
for eid in needs_enrichment_entities[:20]:
    print(f"  {eid}: \"{by_id[eid]['canonical_name']}\"")
if len(needs_enrichment_entities) > 20:
    print(f"  ... and {len(needs_enrichment_entities) - 20} more (see {OUTPUT_CSV})")
