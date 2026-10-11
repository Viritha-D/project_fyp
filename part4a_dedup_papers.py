"""
Part 4a - Deduplicate rows down to one entry per unique paper description.

The master CSV has one row per (paper, algorithm, benchmark-instance) result,
so the same paper appears many times with identical `matching_text` (and thus
identical embeddings). For problem-entity clustering we only want one row per
unique matching_text_hash.

Input:
    papers_master_with_embeddings_ref.csv
    paper_embeddings.npy   (row-aligned to the CSV above)

Output:
    unique_papers.csv          - one row per matching_text_hash, plus a
                                  pipe-separated `member_paper_ids` column
                                  listing every original paper_id that shares
                                  that text
    unique_embeddings.npy      - embeddings row-aligned to unique_papers.csv
"""

import pandas as pd
import numpy as np

REF_CSV = 'papers_master_with_embeddings_ref.csv'
EMB_FILE = 'paper_embeddings.npy'

OUTPUT_CSV = 'unique_papers.csv'
OUTPUT_EMB = 'unique_embeddings.npy'

df = pd.read_csv(REF_CSV)
emb = np.load(EMB_FILE)
assert len(df) == emb.shape[0], "row count mismatch between CSV and embeddings"

# ---- Group by matching_text_hash, keep first row as representative ----
first_idx = df.groupby('matching_text_hash', sort=False).head(1).index
members = df.groupby('matching_text_hash')['paper_id'].apply(lambda s: '|'.join(s)).rename('member_paper_ids')
n_members = df.groupby('matching_text_hash')['paper_id'].size().rename('n_members')

unique_df = df.loc[first_idx].merge(members, on='matching_text_hash').merge(n_members, on='matching_text_hash')
unique_df = unique_df.reset_index(drop=True)
unique_emb = emb[first_idx.to_numpy()]

assert len(unique_df) == unique_emb.shape[0]
assert unique_df['matching_text_hash'].nunique() == len(unique_df)

unique_df.to_csv(OUTPUT_CSV, index=False)
np.save(OUTPUT_EMB, unique_emb)

print(f'Rows in: {len(df)}  ->  unique papers: {len(unique_df)}')
print(f'Saved {OUTPUT_CSV} and {OUTPUT_EMB}')
print()
print('Category breakdown of unique papers:')
print(unique_df['Category'].value_counts())
print()
print('n_members distribution (how many original rows collapse into one unique paper):')
print(unique_df['n_members'].value_counts().sort_index())
