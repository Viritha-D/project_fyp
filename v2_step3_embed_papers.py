"""
v2 Step 3 - Part 3 (paper embeddings) on papers_master_with_matching_text_v2.csv.

Same model and settings as part3_embed_papers.py: sentence-transformers/all-mpnet-base-v2,
768 dimensions, batch_size 64, normalize_embeddings=True, over matching_text in the exact
row order of the input. Outputs (the old versions are in backup_v2/):
    paper_embeddings.npy                  float32, shape (11342, 768), row i <-> input row i
    paper_ids_order.txt                   Paper_ID of row i on line i
    papers_master_with_embeddings_ref.csv the input + matching_text_hash (sha256), the
                                          row-aligned reference read by part4a/5/6
    embedding_metadata.json               same keys as part3 plus the input file, the model
                                          revision and the Paper_ID order file
Usage: python v2_step3_embed_papers.py   (needs sentence-transformers and network access
to huggingface.co on the first run)
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / 'papers_master_with_matching_text_v2.csv'
MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
EXPECTED = (11342, 768)

OUTPUT_EMBEDDINGS = ROOT / 'paper_embeddings.npy'
OUTPUT_IDS = ROOT / 'paper_ids_order.txt'
OUTPUT_METADATA = ROOT / 'embedding_metadata.json'
OUTPUT_CSV_WITH_HASH = ROOT / 'papers_master_with_embeddings_ref.csv'


def main():
    df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
    assert len(df) == EXPECTED[0], len(df)
    assert (df['matching_text'].str.strip() != '').all(), 'empty matching_text -- fix Part 2 output first'
    assert df['Paper_ID'].is_unique
    texts = df['matching_text'].tolist()
    paper_ids = df['Paper_ID'].tolist()

    print(f'Loading model: {MODEL_NAME}')
    model = SentenceTransformer(MODEL_NAME)
    print(f'Embedding {len(texts)} rows...')
    emb = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True,
                       convert_to_numpy=True).astype(np.float32)

    # ---------------- assertions ----------------
    assert emb.shape == EXPECTED, emb.shape
    assert not np.isnan(emb).any(), 'NaN in embeddings'
    norms = np.linalg.norm(emb, axis=1)
    assert np.all(np.abs(norms - 1) < 1e-3), f'norms out of range: {norms.min()}..{norms.max()}'
    print(f'[3] PASSED: shape {emb.shape}, no NaN, norms {norms.min():.6f}..{norms.max():.6f} (within 1e-3 of 1)')

    np.save(OUTPUT_EMBEDDINGS, emb)
    OUTPUT_IDS.write_text('\n'.join(paper_ids) + '\n', encoding='utf-8')

    df['matching_text_hash'] = df['matching_text'].map(lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest())
    df.to_csv(OUTPUT_CSV_WITH_HASH, index=False, lineterminator='\n')

    revision = getattr(getattr(model, 'model_card_data', None), 'base_model_revision', None)
    metadata = {
        'model_name': MODEL_NAME,
        'model_revision': revision,
        'embedding_dim': int(emb.shape[1]),
        'n_papers_embedded': int(emb.shape[0]),
        'normalized': True,
        'batch_size': 64,
        'source_csv': INPUT_CSV.name,
        'generated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'paper_id_order_file': OUTPUT_CSV_WITH_HASH.name,
        'paper_ids_file': OUTPUT_IDS.name,
    }
    OUTPUT_METADATA.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')

    # ---------------- read-back checks ----------------
    back = np.load(OUTPUT_EMBEDDINGS)
    assert back.shape == EXPECTED and np.array_equal(back, emb)
    ids = OUTPUT_IDS.read_text(encoding='utf-8').splitlines()
    assert ids == paper_ids, 'paper_ids_order.txt does not match the input order'
    ref = pd.read_csv(OUTPUT_CSV_WITH_HASH, dtype=str, keep_default_na=False)
    assert ref['Paper_ID'].tolist() == paper_ids and len(ref.columns) == len(df.columns)
    print(f'saved {OUTPUT_EMBEDDINGS.name} ({OUTPUT_EMBEDDINGS.stat().st_size:,} bytes), {OUTPUT_IDS.name}, '
          f'{OUTPUT_CSV_WITH_HASH.name}, {OUTPUT_METADATA.name}; read-back checks passed')

    # nearest-neighbour spot check (as in part3), on 3 fixed rows
    print('\n--- nearest neighbours for 3 rows ---')
    for i in (0, len(df) // 2, len(df) - 1):
        sims = emb @ emb[i]
        top = [j for j in np.argsort(-sims)[:4] if j != i][:3]
        print(f'\n{paper_ids[i]}: "{texts[i][:80]}"')
        for j in top:
            print(f'  -> {paper_ids[j]} (sim={sims[j]:.3f}): "{texts[j][:80]}"')


if __name__ == '__main__':
    sys.exit(main())
