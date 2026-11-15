"""
Merge the 2 confirmed TSP spelling-variant duplicates into their canonical
generic-TSP entity (verified against source text earlier):
  E00822 "Traveling Salesperson Problem" (Pure Math, 1 paper) -> E00435 "Traveling Salesman Problem" (Pure Math, 2 papers)
  E00857 "Traveling Salesperson Problem (FOGA2019)" (Applied, 1 paper) -> E00376 "Traveling Salesman Problem (TSP)" (Applied, 2 papers)

Done as a direct entity-level merge (not by re-running Part 5), since Part 5
rebuilds base_description fresh from the un-enriched source CSV and would
discard the enrichment work already applied to problem_entities.json.

Updates, kept consistent across all three artifacts:
  - problem_entities.json: absorbed entity's members/aliases/papers folded
    into the canonical entity; absorbed entity's own record removed.
  - entity_embeddings.npy: absorbed entity's row removed (canonical entity
    keeps its existing embedding -- descriptions are near-identical text,
    re-embedding would not meaningfully change it).
  - paper_to_entity_map_final.csv: absorbed entity's rows reassigned to the
    canonical entity_id, for traceability.
  - entity_strategy_layer_v2.csv: same reassignment, so Part 8's strategy
    lookup for the canonical entity picks up the absorbed entity's strategy
    rows too.
"""

import json
import numpy as np
import pandas as pd

MERGES = [
    ('E00822', 'E00435'),  # absorbed -> canonical
    ('E00857', 'E00376'),
]

with open('problem_entities.json', encoding='utf-8') as f:
    entities = json.load(f)
by_id = {e['entity_id']: e for e in entities}
id_to_idx = {e['entity_id']: i for i, e in enumerate(entities)}
emb = np.load('entity_embeddings.npy')
assert emb.shape[0] == len(entities)

remove_indices = []
for absorbed_id, canonical_id in MERGES:
    absorbed = by_id[absorbed_id]
    canonical = by_id[canonical_id]
    assert absorbed['category'] == canonical['category'], 'refusing cross-category merge'

    canonical['member_paper_ids'] = sorted(set(canonical['member_paper_ids']) | set(absorbed['member_paper_ids']))
    canonical['source_paper_ids'] = sorted(set(canonical['source_paper_ids']) | set(absorbed['source_paper_ids']))
    canonical['n_member_rows'] = len(canonical['member_paper_ids'])
    canonical['n_supporting_papers'] = len(canonical['source_paper_ids'])
    canonical['description_confidence'] = (
        'high' if canonical['n_supporting_papers'] >= 5
        else 'medium' if canonical['n_supporting_papers'] >= 2
        else 'low'
    )
    canonical['aliases']['benchmark_names'] = sorted(
        set(canonical['aliases']['benchmark_names']) | set(absorbed['aliases']['benchmark_names'])
    )
    canonical['aliases']['paper_titles'] = sorted(
        set(canonical['aliases']['paper_titles']) | set(absorbed['aliases']['paper_titles'])
    )
    for field, vals in absorbed.get('characterization_conflicts', {}).items():
        existing = set(canonical.setdefault('characterization_conflicts', {}).get(field, []))
        canonical['characterization_conflicts'][field] = sorted(existing | set(vals))

    remove_indices.append(id_to_idx[absorbed_id])
    print(f'Merged {absorbed_id} ("{absorbed["canonical_name"]}") into '
          f'{canonical_id} ("{canonical["canonical_name"]}") '
          f'-> now {canonical["n_supporting_papers"]} supporting papers')

new_entities = [e for i, e in enumerate(entities) if i not in set(remove_indices)]
new_emb = np.delete(emb, remove_indices, axis=0)
assert len(new_entities) == new_emb.shape[0]

with open('problem_entities.json', 'w', encoding='utf-8') as f:
    json.dump(new_entities, f, indent=2, ensure_ascii=False)
np.save('entity_embeddings.npy', new_emb)
print(f'\nSaved {len(new_entities)} entities and embeddings {new_emb.shape}')

# ---- Keep the map and strategy layer consistent ----
merge_map = dict(MERGES)

emap = pd.read_csv('paper_to_entity_map_final.csv')
n_affected = emap['entity_id'].isin(merge_map).sum()
emap['entity_id'] = emap['entity_id'].replace(merge_map)
emap.to_csv('paper_to_entity_map_final.csv', index=False)
print(f'paper_to_entity_map_final.csv: reassigned {n_affected} rows')

strat = pd.read_csv('entity_strategy_layer_v2.csv')
n_affected_strat = strat['entity_id'].isin(merge_map).sum()
strat['entity_id'] = strat['entity_id'].replace(merge_map)
strat.to_csv('entity_strategy_layer_v2.csv', index=False)
print(f'entity_strategy_layer_v2.csv: reassigned {n_affected_strat} rows')

# sanity
assert 'E00822' not in [e['entity_id'] for e in new_entities]
assert 'E00857' not in [e['entity_id'] for e in new_entities]
print('\nSanity check: absorbed entity_ids no longer present in problem_entities.json -- OK')
