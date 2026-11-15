"""
Part 5 - entity records, reconstructed and checked against the old outputs.

build_entities   = part5_build_entities.py, field for field (medoid by embedding centrality,
                   aliases, characterization_conflicts, confidence tiers, variant families)
enrich           = the enrichment applied by part7_apply_enrichment.py (its input,
                   problem_entities_enriched.json, is not in the repo; the rule below
                   reproduces the old problem_entities.json exactly, see --fidelity):
                   if the entity's member rows carry any Landscape_Characteristics tag,
                   base_description = "<canonical_name>. <medoid Target_Landscape>. Landscape:
                   <tags>" (tags = union over members in member order, case-insensitive
                   de-duplication, missing markers skipped); otherwise the medoid's
                   matching_text is kept.
merge_entities   = merge_tsp_duplicates.py (members/sources/aliases/conflicts unioned,
                   counts and confidence recomputed, description and embedding kept)
prefix_canonical = fix_underspecified_entities.py (canonical_name prepended)
"""

import re
from collections import defaultdict

import numpy as np

CHAR_FIELDS = ['Modality', 'Separability', 'Target_Landscape', 'Dimensionality']
NOT_REPORTED = 'Not Reported'
MISSING = {'', 'Not Reported', 'N/A (Pure Math problem)'}


def paper_prefix(paper_id):
    return re.sub(r'_Ext_\d+$', '', paper_id)


def confidence_from_count(n):
    return 'high' if n >= 5 else 'medium' if n >= 2 else 'low'


def digit_stripped_key(name):
    s = re.sub(r'\d+', '#', str(name))
    return re.sub(r'[^a-z#]', '', s.lower())


def build_entities(emap, master, emb, id_col):
    """emap: paper_id, Category, Paper_Title, Benchmark_Name, entity_id, parent_benchmark_id, entity_type.
    master: id_col, matching_text, CHAR_FIELDS (row-aligned with emb)."""
    assert len(master) == emb.shape[0], 'master rows and embeddings must be row-aligned'
    m = master[[id_col, 'matching_text'] + CHAR_FIELDS].rename(columns={id_col: 'paper_id'})
    df = emap.merge(m, on='paper_id', how='left', validate='one_to_one')
    assert df['matching_text'].notna().all()
    row_index = {pid: i for i, pid in enumerate(master[id_col])}

    entities = []
    for entity_id, grp in df.groupby('entity_id', sort=True):
        vecs = emb[grp['paper_id'].map(row_index).to_numpy()]
        if len(grp) == 1:
            medoid_pos = 0
        else:
            sims = vecs @ vecs.T
            np.fill_diagonal(sims, 0.0)
            medoid_pos = int(np.argmax(sims.sum(axis=1)))
        med = grp.iloc[medoid_pos]
        sources = sorted(set(grp['paper_id'].map(paper_prefix)))
        conflicts = {}
        for f in CHAR_FIELDS:
            vals = {v for v in grp[f].astype(str) if v not in ('', NOT_REPORTED)}
            if len(vals) > 1:
                conflicts[f] = sorted(vals)
        parents = [p for p in grp['parent_benchmark_id'].unique() if p]
        entities.append({
            'entity_id': entity_id,
            'entity_type': grp['entity_type'].iloc[0],
            'parent_benchmark_id': parents[0] if parents else None,
            'category': grp['Category'].iloc[0],
            'canonical_name': med['Benchmark_Name'],
            'base_description': med['matching_text'],
            'medoid_paper_id': med['paper_id'],
            'n_member_rows': int(len(grp)),
            'n_supporting_papers': len(sources),
            'description_confidence': confidence_from_count(len(sources)),
            'source_paper_ids': sources,
            'member_paper_ids': sorted(grp['paper_id'].tolist()),
            'aliases': {'benchmark_names': sorted({b for b in grp['Benchmark_Name'] if b}),
                        'paper_titles': sorted({t for t in grp['Paper_Title'] if t})},
            'characterization_conflicts': conflicts,
            'variant_family_id': None,
        })

    groups = defaultdict(list)
    for e in entities:
        if e['parent_benchmark_id'] is None and e['entity_type'] != 'suite':
            groups[(e['category'], digit_stripped_key(e['canonical_name']))].append(e['entity_id'])
    fam, counter = {}, 0
    for eids in groups.values():
        if len(eids) > 1:
            counter += 1
            for x in eids:
                fam[x] = f'VF{counter:04d}'
    for e in entities:
        e['variant_family_id'] = fam.get(e['entity_id'])
    return entities


def landscape_tags(member_ids, master_by_id):
    tags, seen = [], set()
    for p in member_ids:
        for t in str(master_by_id.at[p, 'Landscape_Characteristics']).split(';'):
            t = t.strip()
            if t and t not in MISSING and t.lower() not in seen:
                seen.add(t.lower())
                tags.append(t)
    return tags


def enrich(entities, master_by_id):
    """Medoid description enriched with the union of landscape tags (see module doc)."""
    n = 0
    for e in entities:
        tags = landscape_tags(e['member_paper_ids'], master_by_id)
        if not tags:
            continue
        tl = master_by_id.at[e['medoid_paper_id'], 'Target_Landscape']
        parts = [e['canonical_name']] + ([tl] if tl not in MISSING else [])
        e['base_description'] = '. '.join(parts) + '. Landscape: ' + '; '.join(tags)
        e['landscape_tags'] = tags
        n += 1
    return n


def merge_entities(entities, merges):
    """merges: [(absorbed_id, canonical_id)] -> entities without the absorbed records."""
    by_id = {e['entity_id']: e for e in entities}
    drop = set()
    for a_id, c_id in merges:
        a, c = by_id[a_id], by_id[c_id]
        assert a['category'] == c['category'], 'refusing cross-category merge'
        c['member_paper_ids'] = sorted(set(c['member_paper_ids']) | set(a['member_paper_ids']))
        c['source_paper_ids'] = sorted(set(c['source_paper_ids']) | set(a['source_paper_ids']))
        c['n_member_rows'] = len(c['member_paper_ids'])
        c['n_supporting_papers'] = len(c['source_paper_ids'])
        c['description_confidence'] = confidence_from_count(c['n_supporting_papers'])
        for k in ('benchmark_names', 'paper_titles'):
            c['aliases'][k] = sorted(set(c['aliases'][k]) | set(a['aliases'][k]))
        for f, vals in a.get('characterization_conflicts', {}).items():
            c.setdefault('characterization_conflicts', {})[f] = sorted(set(c['characterization_conflicts'].get(f, [])) | set(vals))
        drop.add(a_id)
    return [e for e in entities if e['entity_id'] not in drop]


def prefix_canonical(entities, ids):
    for e in entities:
        if e['entity_id'] in ids:
            e['base_description'] = f"{e['canonical_name']}. {e['base_description']}"
