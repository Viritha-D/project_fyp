"""
Blind labelling pack for family_review_sample_v3.csv.

labeling/family_review_sample_v3_blind.csv  same 80 pairs, same row order: per entity only the
    name, up to 5 aliases, Category, venues and 2 sample Problem_Context values, plus empty
    'same_family (y/n/unsure)' and 'notes'. No pair type, evidence, family or entity ids.
labeling/family_review_key_v3.csv           pair_id + entity ids + pair_type, evidence, family columns.
labeling/labeling_instructions.md
Usage: python make_labeling_pack_v3.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'labeling'
MISSING = {'', 'Not Reported', 'N/A (Pure Math problem)'}

DEFINITION = ('Label y if a researcher choosing benchmarks would treat the two as members of the same benchmark '
              'series, suite, repository or experimental grid, so recommending one makes the other a plausible '
              'alternative from the same set. Label n if they are different benchmarks that only share a topic or a '
              'word. Two datasets from the same repository are y only if their task type is also similar (both '
              'classification, both feature selection); different task types are n. Use unsure when you cannot tell '
              'from the shown fields. Do not look anything up.')


def main():
    sample = pd.read_csv(ROOT / 'family_review_sample_v3.csv', dtype=str, keep_default_na=False)
    assert len(sample) == 80
    notes = {n['entity_id']: n for n in json.loads((ROOT / 'entity_notes_v2.json').read_text(encoding='utf-8'))}
    m = pd.read_csv(ROOT / 'paper_to_entity_map_v2.csv', dtype=str, keep_default_na=False)
    d = pd.read_csv(ROOT / 'papers_master_with_matching_text_v2.csv', dtype=str, keep_default_na=False)
    rows = d.assign(entity_id=m['entity_id'].values, paper_key=m['paper_key'].values)
    rows = rows[rows['entity_id'].isin(set(sample['entity_id_a']) | set(sample['entity_id_b']))]
    contexts = {e: g[g['Problem_Context'].map(lambda v: v.strip() not in MISSING)].groupby('Problem_Context')['paper_key']
                .nunique().sort_values(ascending=False, kind='stable').index[:2].tolist() for e, g in rows.groupby('entity_id')}

    def side(e, s):
        n = notes[e]
        return {f'name_{s}': n['canonical_name'],
                f'aliases_{s}': ' | '.join(a for a in n['aliases'][:5]),
                f'category_{s}': n['category'],
                f'venues_{s}': '; '.join(f'{v} ({c})' for v, c in n['venues'].items() if c),
                f'sample_problem_contexts_{s}': ' | '.join(contexts.get(e, []))}

    blind, key = [], []
    for i, r in enumerate(sample.itertuples(index=False), 1):
        pid = f'P{i:02d}'
        blind.append({'pair_id': pid, **side(r.entity_id_a, 'a'), **side(r.entity_id_b, 'b'),
                      'same_family (y/n/unsure)': '', 'notes': ''})
        key.append({'pair_id': pid, 'entity_id_a': r.entity_id_a, 'entity_id_b': r.entity_id_b,
                    'pair_type': r.pair_type, 'evidence': r.evidence, 'family_a': r.family_a, 'family_b': r.family_b})
    B, K = pd.DataFrame(blind), pd.DataFrame(key)

    # checks: same pairs and order; nothing that reveals the answer
    assert B['pair_id'].tolist() == K['pair_id'].tolist() and len(B) == 80
    assert (B['name_a'].tolist() == [notes[e]['canonical_name'] for e in sample['entity_id_a']])
    leak = [c for c in B.columns if any(w in c.lower() for w in ('pair_type', 'evidence', 'family_a', 'family_b', 'entity_id'))]
    assert not leak, leak
    text = ' '.join(B.drop(columns=['pair_id']).astype(str).agg(' '.join, axis=1))
    assert not any(t in text for t in ('merged_by_', 'candidate_not_merged', 'negative_control', 'cosine ')), 'answer leak'

    OUT.mkdir(exist_ok=True)
    B.to_csv(OUT / 'family_review_sample_v3_blind.csv', index=False)
    K.to_csv(OUT / 'family_review_key_v3.csv', index=False)
    (OUT / 'labeling_instructions.md').write_text(INSTRUCTIONS.format(definition=DEFINITION), encoding='utf-8')
    print(f'wrote {OUT.name}/: {len(B)} blind pairs, key with {len(K)} rows; blind columns: {B.columns.tolist()}')


INSTRUCTIONS = """# Labelling instructions: same benchmark family?

You will label 80 pairs of benchmark problems in `family_review_sample_v3_blind.csv`.
Work alone and do not discuss pairs with anyone until you are done.

## What you see

Each row is one pair, **a** and **b**. For each side:

- `name_*`: the benchmark name used in the papers
- `aliases_*`: up to 5 other names papers used for the same benchmark (separated by `|`)
- `category_*`: Pure Math (synthetic / mathematical benchmark) or Applied (real-world problem)
- `venues_*`: conferences where it appears, with the number of papers
- `sample_problem_contexts_*`: up to 2 task descriptions taken from the papers (separated by `|`)

Rows are in random order. Nothing in the file tells you how the pair was chosen.

## The question

{definition}

## How to fill it in

- Write exactly one of `y`, `n` or `unsure` in `same_family (y/n/unsure)` for every row.
- Use `notes` for a short reason when the call was hard, or when you chose `unsure`.
- Judge only from the fields shown. Do not search online, open papers or ask anyone.
- Do not change any other column, and do not sort, add or delete rows.
- When finished, save the file as CSV (UTF-8) under the same name and return it.

## Examples of the distinction (not taken from the file)

- DTLZ1 and DTLZ3: **y** (same suite).
- Two UCI classification datasets: **y**; a UCI classification dataset and a UCI regression
  dataset: **n** (same repository, different task type).
- "Vehicle routing with drones" and "Vehicle routing with time windows" from unrelated papers:
  usually **n** unless the fields show they come from one benchmark set or grid.
"""


if __name__ == '__main__':
    sys.exit(main())
