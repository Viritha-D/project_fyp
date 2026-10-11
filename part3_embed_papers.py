"""
Part 3 - Embed every paper's matching_text into a vector.

Run this in YOUR OWN environment (not this sandbox), since it needs to download
a pretrained model from Hugging Face on first run.

Install first:
    pip install sentence-transformers pandas numpy
"""

import pandas as pd
import numpy as np
import json
import hashlib
from datetime import datetime
from sentence_transformers import SentenceTransformer

INPUT_CSV = 'papers_master_with_matching_text.csv'
MODEL_NAME = 'all-mpnet-base-v2'   # general-purpose, strong baseline (see note below)

OUTPUT_EMBEDDINGS = 'paper_embeddings.npy'
OUTPUT_METADATA = 'embedding_metadata.json'
OUTPUT_CSV_WITH_HASH = 'papers_master_with_embeddings_ref.csv'

# ---- Load data ----
df = pd.read_csv(INPUT_CSV)
assert df['matching_text'].isna().sum() == 0, "Found NaN in matching_text -- fix Part 2 output first"
assert (df['matching_text'].str.strip() == '').sum() == 0, "Found empty matching_text -- fix Part 2 output first"

texts = df['matching_text'].tolist()
paper_ids = df['paper_id'].tolist()

# ---- Load model and embed ----
print(f'Loading model: {MODEL_NAME} (downloads on first run, then cached locally)')
model = SentenceTransformer(MODEL_NAME)

print(f'Embedding {len(texts)} papers...')
embeddings = model.encode(
    texts,
    batch_size=64,
    show_progress_bar=True,
    normalize_embeddings=True,  # pre-normalize so cosine similarity = dot product later
)

# ---- Save embeddings, row-aligned to paper_id order ----
np.save(OUTPUT_EMBEDDINGS, embeddings)

# ---- Save a hash of each paper's matching_text, so future runs only re-embed changed rows ----
df['matching_text_hash'] = df['matching_text'].apply(
    lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()
)
df.to_csv(OUTPUT_CSV_WITH_HASH, index=False)

# ---- Save metadata for traceability ----
metadata = {
    'model_name': MODEL_NAME,
    'embedding_dim': int(embeddings.shape[1]),
    'n_papers_embedded': int(embeddings.shape[0]),
    'normalized': True,
    'generated_at': datetime.utcnow().isoformat() + 'Z',
    'paper_id_order_file': OUTPUT_CSV_WITH_HASH,  # confirms row alignment: embeddings[i] <-> paper_ids[i]
}
with open(OUTPUT_METADATA, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f'\nSaved {embeddings.shape[0]} embeddings of dim {embeddings.shape[1]} to {OUTPUT_EMBEDDINGS}')
print(f'Saved metadata to {OUTPUT_METADATA}')
print(f'Saved hash-tagged reference CSV to {OUTPUT_CSV_WITH_HASH}')

# ---- Sanity check: nearest-neighbor spot check on 3 papers, per Part 3's "done when" criteria ----
print('\n--- Sanity check: nearest neighbors for first 3 papers ---')
sims = embeddings[:3] @ embeddings.T  # cosine sim, since vectors are normalized
for i in range(3):
    top5 = np.argsort(-sims[i])[:5]
    print(f'\nPaper {paper_ids[i]}: "{texts[i][:70]}..."')
    for j in top5:
        if j == i:
            continue
        print(f'  -> {paper_ids[j]} (sim={sims[i][j]:.3f}): "{texts[j][:70]}..."')