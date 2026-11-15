"""
Apply the enriched entity descriptions:
- Load problem_entities_enriched.json, drop E00599 ("Evolutionary Algorithm",
  removed earlier as a near-empty extraction artifact -- confirmed the enriched
  file still had it, since it was built before that removal).
- Verify entity_id order now matches the current problem_entities.json / row
  order of entity_embeddings.npy exactly (both are entity_id-sorted with the
  same set after dropping E00599) -- confirmed before running this script.
- Re-embed ONLY the entities flagged description_needs_reembedding: true,
  using the same model as Part 3/5 (all-mpnet-base-v2). Every other row in
  entity_embeddings.npy is left untouched (copied over by position).
- Strip description_needs_reembedding from all entities and save.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

ENRICHED_PATH = r'C:/Users/daggu/Downloads/problem_entities_enriched.json'
CURRENT_ENTITIES_PATH = 'problem_entities.json'
EMB_PATH = 'entity_embeddings.npy'
MODEL_NAME = 'all-mpnet-base-v2'

with open(ENRICHED_PATH, encoding='utf-8') as f:
    enriched = json.load(f)
enriched = [e for e in enriched if e['entity_id'] != 'E00599']

with open(CURRENT_ENTITIES_PATH, encoding='utf-8') as f:
    current = json.load(f)
current_ids = [e['entity_id'] for e in current]
enriched_ids = [e['entity_id'] for e in enriched]

assert enriched_ids == current_ids, 'entity order mismatch -- cannot safely reuse embeddings by position'

old_emb = np.load(EMB_PATH)
assert old_emb.shape[0] == len(current)

new_emb = old_emb.copy()

to_reembed = [(i, e) for i, e in enumerate(enriched) if e.get('description_needs_reembedding')]
print(f'Entities flagged for re-embedding: {len(to_reembed)} / {len(enriched)}')

model = SentenceTransformer(MODEL_NAME)
texts = [e['base_description'] for _, e in to_reembed]
print(f'Embedding {len(texts)} updated descriptions...')
fresh_vecs = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)

for (idx, _), vec in zip(to_reembed, fresh_vecs):
    new_emb[idx] = vec

for e in enriched:
    e.pop('description_needs_reembedding', None)

np.save(EMB_PATH, new_emb)
with open(CURRENT_ENTITIES_PATH, 'w', encoding='utf-8') as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)

print()
print(f'Saved {len(enriched)} entities to {CURRENT_ENTITIES_PATH}')
print(f'Saved embeddings {new_emb.shape} to {EMB_PATH}')
print(f'description_needs_reembedding remaining anywhere: '
      f'{sum(1 for e in enriched if "description_needs_reembedding" in e)}')

# sanity: untouched rows should be byte-identical to before
untouched_idx = [i for i in range(len(enriched)) if i not in {idx for idx, _ in to_reembed}]
unchanged_ok = np.allclose(old_emb[untouched_idx], new_emb[untouched_idx])
print(f'Untouched rows still match original embeddings exactly: {unchanged_ok}')
