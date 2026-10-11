"""
Narrow the 316 'true merge candidate' pairs (high name-word-overlap) down to
likely genuine synonym duplicates, using degree in the candidate graph as the
discriminator: a real 1:1 synonym pair (like TSP Salesman/Salesperson) is
usually isolated -- each entity matches only its one synonym partner. A
family of genuinely distinct named instances sharing a template (OCTSP
instances, KNN metric variants) shows up as a CLIQUE -- each entity matches
many siblings. Low-degree pairs are the best candidates for a manual review
pass like the one done for TSP.
"""

import pandas as pd
from collections import defaultdict

report = pd.read_csv('entity_dedup_candidates.csv')
flagged = report['is_likely_numbered_variant'] | report['is_likely_named_instance_variant']
remaining = report[~flagged]
true_candidates = remaining[remaining['name_word_overlap'] >= 0.6]

degree = defaultdict(set)
for _, r in true_candidates.iterrows():
    degree[r['entity_id_a']].add(r['entity_id_b'])
    degree[r['entity_id_b']].add(r['entity_id_a'])

rows = []
for _, r in true_candidates.iterrows():
    deg_a = len(degree[r['entity_id_a']])
    deg_b = len(degree[r['entity_id_b']])
    rows.append({**r.to_dict(), 'deg_a': deg_a, 'deg_b': deg_b, 'max_deg': max(deg_a, deg_b)})

scored = pd.DataFrame(rows).sort_values(['max_deg', 'similarity'], ascending=[True, False])

print(f'Total true-merge-candidate pairs: {len(scored)}')
print(f'Isolated 1:1 pairs (deg=1 both sides -- highest-confidence candidates): '
      f'{(scored["max_deg"] == 1).sum()}')
print()
print('=== Isolated pairs (max_deg == 1) ===')
iso = scored[scored['max_deg'] == 1]
for _, r in iso.iterrows():
    print(f"  sim={r['similarity']:.3f}  overlap={r['name_word_overlap']:.2f}  [{r['category']}]  "
          f"{r['entity_id_a']} \"{r['name_a']}\"  <->  {r['entity_id_b']} \"{r['name_b']}\"")

print()
print('=== Low-degree pairs (max_deg in 2-3, still worth a look) ===')
low = scored[(scored['max_deg'] >= 2) & (scored['max_deg'] <= 3)]
for _, r in low.head(20).iterrows():
    print(f"  sim={r['similarity']:.3f}  overlap={r['name_word_overlap']:.2f}  deg={r['max_deg']}  [{r['category']}]  "
          f"{r['entity_id_a']} \"{r['name_a']}\"  <->  {r['entity_id_b']} \"{r['name_b']}\"")
