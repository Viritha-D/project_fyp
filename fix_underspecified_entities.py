"""
Fix the 7 description-underspecified entities found by the dedup audit:
each shares an identical, paper-level base_description with its siblings,
with zero mention of the specific dataset/strategy that actually
distinguishes it (that detail only lived in canonical_name). Fix: prepend
the entity's own canonical_name into its base_description, then re-embed
just these 7 rows -- same pattern as the earlier enrichment pass.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

ENTITIES_PATH = 'problem_entities.json'
EMB_PATH = 'entity_embeddings.npy'
MODEL_NAME = 'all-mpnet-base-v2'

TARGET_IDS = ['E00255', 'E00256', 'E00257', 'E00258', 'E00564', 'E00565', 'E00566']

with open(ENTITIES_PATH, encoding='utf-8') as f:
    entities = json.load(f)
emb = np.load(EMB_PATH)
assert emb.shape[0] == len(entities)

id_to_idx = {e['entity_id']: i for i, e in enumerate(entities)}

model = SentenceTransformer(MODEL_NAME)

for eid in TARGET_IDS:
    idx = id_to_idx[eid]
    e = entities[idx]
    old_desc = e['base_description']
    new_desc = f"{e['canonical_name']}. {old_desc}"
    e['base_description'] = new_desc
    print(f'{eid}: "{old_desc[:60]}..." -> "{new_desc[:70]}..."')

texts = [entities[id_to_idx[eid]]['base_description'] for eid in TARGET_IDS]
fresh_vecs = model.encode(texts, batch_size=8, show_progress_bar=False, normalize_embeddings=True)

for eid, vec in zip(TARGET_IDS, fresh_vecs):
    emb[id_to_idx[eid]] = vec

with open(ENTITIES_PATH, 'w', encoding='utf-8') as f:
    json.dump(entities, f, indent=2, ensure_ascii=False)
np.save(EMB_PATH, emb)

# sanity: the 7 entities should no longer be pairwise-identical in embedding space
sub_emb = emb[[id_to_idx[eid] for eid in TARGET_IDS]]
sims = sub_emb @ sub_emb.T
print()
print('Pairwise similarity among the 7 after enrichment (should no longer be 1.000):')
for i, a in enumerate(TARGET_IDS):
    for j, b in enumerate(TARGET_IDS):
        if j > i and entities[id_to_idx[a]]['category'] == entities[id_to_idx[b]]['category']:
            print(f'  {a} <-> {b}: {sims[i,j]:.4f}')
