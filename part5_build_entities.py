"""
Part 5 - Build structured problem-entity records from the Part 4 clusters.

Inputs:
    paper_to_entity_map_final.csv   - paper_id -> entity_id (+ entity_type, parent_benchmark_id)
    papers_master_with_embeddings_ref.csv - full per-row metadata + matching_text
    paper_embeddings.npy            - row-aligned to the master CSV (from Part 3)

For each entity_id:
    - medoid = the member row whose embedding has the highest average cosine
      similarity to all other members' embeddings (most "central" row).
      Its matching_text becomes the entity's base_description.
    - aliases = every distinct Benchmark_Name / Paper_Title string seen among members.
    - n_supporting_papers = distinct SOURCE papers (paper_id with the trailing
      _Ext_NN stripped), since one source paper can contribute many rows
      (one per algorithm x benchmark-instance combination).
    - description_confidence = derived from n_supporting_papers:
          >=5 papers -> "high", 2-4 -> "medium", 1 -> "low"
      (a simple, explicit tiering -- tune thresholds later if needed).
    - characterization_conflicts = for Modality / Separability / Target_Landscape /
      Dimensionality, the distinct values seen among members (excluding the
      "Not Reported" sentinel). Non-empty only when members disagree -- these
      are flagged, not resolved.
    - variant_family_id = a candidate grouping of entities that are probably
      parameter variants of the same base problem (e.g. "RFID ... (C_30)" vs
      "(C_50)"): entities are grouped by (Category, digit-stripped canonical
      name). Scoped to entities with no parent_benchmark_id and
      entity_type != 'suite', since suite/single_function children already
      have that relationship captured via parent_benchmark_id -- this avoids
      re-flagging e.g. every CEC2017 F<n> as a "variant family" on top of the
      suite hierarchy that already links them. This is a heuristic candidate
      list for manual review, not an authoritative merge (per Part 5 spec).

Output:
    problem_entities.json   - one record per entity
    entity_embeddings.npy   - row-aligned to problem_entities.json order,
                              re-embedded from each entity's base_description
                              using the same model as Part 3.
"""

import json
import re
from collections import defaultdict

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ENTITY_MAP_CSV = 'paper_to_entity_map_final.csv'
MASTER_CSV = 'papers_master_with_embeddings_ref.csv'
EMB_FILE = 'paper_embeddings.npy'
MODEL_NAME = 'all-mpnet-base-v2'

OUTPUT_JSON = 'problem_entities.json'
OUTPUT_EMB = 'entity_embeddings.npy'

CHAR_FIELDS = ['Modality', 'Separability', 'Target_Landscape', 'Dimensionality']
NOT_REPORTED = 'Not Reported'


def paper_prefix(paper_id):
    return re.sub(r'_Ext_\d+$', '', paper_id)


def confidence_from_count(n_papers):
    if n_papers >= 5:
        return 'high'
    if n_papers >= 2:
        return 'medium'
    return 'low'


def digit_stripped_key(name):
    s = re.sub(r'\d+', '#', str(name))
    s = re.sub(r'[^a-z#]', '', s.lower())
    return s


def main():
    emap = pd.read_csv(ENTITY_MAP_CSV)
    master = pd.read_csv(MASTER_CSV)
    emb = np.load(EMB_FILE)
    assert len(master) == emb.shape[0], 'master rows and embeddings must be row-aligned'

    df = emap.merge(
        master[['paper_id', 'matching_text'] + CHAR_FIELDS],
        on='paper_id', how='left', validate='one_to_one',
    )
    assert df['matching_text'].isna().sum() == 0, 'missing matching_text after merge'

    # paper_id -> row index into `emb`, for medoid similarity lookups
    row_index = {pid: i for i, pid in enumerate(master['paper_id'])}

    entities = []
    for entity_id, grp in df.groupby('entity_id', sort=True):
        idxs = grp['paper_id'].map(row_index).to_numpy()
        vecs = emb[idxs]  # already L2-normalized (Part 3)

        if len(grp) == 1:
            medoid_pos = 0
        else:
            sims = vecs @ vecs.T
            np.fill_diagonal(sims, 0.0)
            medoid_pos = int(np.argmax(sims.sum(axis=1)))
        medoid_row = grp.iloc[medoid_pos]

        source_papers = sorted(set(grp['paper_id'].map(paper_prefix)))
        aliases_benchmark = sorted(set(grp['Benchmark_Name'].dropna().astype(str)))
        aliases_title = sorted(set(grp['Paper_Title'].dropna().astype(str)))

        conflicts = {}
        for field in CHAR_FIELDS:
            vals = set(v for v in grp[field].dropna().astype(str) if v != NOT_REPORTED)
            if len(vals) > 1:
                conflicts[field] = sorted(vals)

        parent_ids = grp['parent_benchmark_id'].dropna().unique()
        entity_type = grp['entity_type'].iloc[0]

        entities.append({
            'entity_id': entity_id,
            'entity_type': entity_type,
            'parent_benchmark_id': (parent_ids[0] if len(parent_ids) else None),
            'category': grp['Category'].iloc[0],
            'canonical_name': medoid_row['Benchmark_Name'],
            'base_description': medoid_row['matching_text'],
            'medoid_paper_id': medoid_row['paper_id'],
            'n_member_rows': int(len(grp)),
            'n_supporting_papers': len(source_papers),
            'description_confidence': confidence_from_count(len(source_papers)),
            'source_paper_ids': source_papers,
            'member_paper_ids': sorted(grp['paper_id'].tolist()),
            'aliases': {
                'benchmark_names': aliases_benchmark,
                'paper_titles': aliases_title,
            },
            'characterization_conflicts': conflicts,
            'variant_family_id': None,   # filled in below
        })

    # ---- Candidate variant-family detection ----
    # Scope: only entities not already tied into a suite hierarchy via
    # parent_benchmark_id, to avoid redundant flags on top of that relationship.
    family_groups = defaultdict(list)
    for e in entities:
        if e['parent_benchmark_id'] is None and e['entity_type'] != 'suite':
            key = (e['category'], digit_stripped_key(e['canonical_name']))
            family_groups[key].append(e['entity_id'])

    family_counter = 0
    eid_to_family = {}
    for key, eids in family_groups.items():
        if len(eids) > 1:
            family_counter += 1
            fam_id = f'VF{family_counter:04d}'
            for eid in eids:
                eid_to_family[eid] = fam_id
    for e in entities:
        e['variant_family_id'] = eid_to_family.get(e['entity_id'])

    # ---- Re-embed each entity's base_description ----
    print(f'Loading model: {MODEL_NAME}')
    model = SentenceTransformer(MODEL_NAME)
    descriptions = [e['base_description'] for e in entities]
    print(f'Embedding {len(descriptions)} entity descriptions...')
    entity_emb = model.encode(
        descriptions, batch_size=64, show_progress_bar=True, normalize_embeddings=True,
    )

    np.save(OUTPUT_EMB, entity_emb)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)

    print()
    print(f'Wrote {len(entities)} entity records to {OUTPUT_JSON}')
    print(f'Wrote embeddings {entity_emb.shape} to {OUTPUT_EMB}')

    # ---- Sanity summary ----
    total_rows_covered = sum(e['n_member_rows'] for e in entities)
    print()
    print(f'Total member rows across all entities: {total_rows_covered} (master has {len(master)})')
    print(f'Entities with empty base_description: {sum(1 for e in entities if not e["base_description"].strip())}')
    print(f'Confidence distribution: {pd.Series([e["description_confidence"] for e in entities]).value_counts().to_dict()}')
    print(f'Entities with characterization_conflicts: {sum(1 for e in entities if e["characterization_conflicts"])}')
    print(f'Entities assigned a variant_family_id: {sum(1 for e in entities if e["variant_family_id"])}')

    print()
    print('--- Example record ---')
    print(json.dumps(entities[0], indent=2, ensure_ascii=False)[:1500])


if __name__ == '__main__':
    main()
