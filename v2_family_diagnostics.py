"""
v2 family layer, Part 1: diagnose entity fragmentation (read-only; report only).

Reads entity_notes_v2.json, paper_to_entity_map_v2.csv, papers_master_with_matching_text_v2.csv
and entity_dedup_candidates_v2.csv. Writes family_diagnostics_v2.md and prints the same text.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'family_diagnostics_v2.md'
MISSING_RE = re.compile(r'(?i)^\s*(not reported|n/?a\b.*|unknown|none|)\s*$')
CUSTOM = 'custom simulated data'
LIB_PREFIX = ['tai', 'bayg', 'bays', 'bal', 'nug', 'chr', 'esc', 'had', 'kra', 'lipa', 'rou', 'scr', 'sko', 'ste',
              'tho', 'wil', 'bur', 'els', 'att', 'berlin', 'burma', 'ch', 'eil', 'fri', 'gr', 'kroa', 'krob', 'kroc',
              'krod', 'kroe', 'lin', 'pr', 'rat', 'st', 'ulysses', 'pcb', 'rd', 'ts', 'tsp', 'gil', 'a', 'd', 'u']
LIB_RE = re.compile(r'^(?:' + '|'.join(sorted(LIB_PREFIX, key=len, reverse=True)) + r')\d+\b', re.I)
PARAM_RE = re.compile(r'\(\s*[A-Za-z][\w]*\s*=')
TAIL_DIGIT_RE = re.compile(r'\d\s*\)?\s*$')
INSTANCE_RE = re.compile(r'(?i)\binstances?\b')


def main():
    notes = json.loads((ROOT / 'entity_notes_v2.json').read_text(encoding='utf-8'))
    N = pd.DataFrame(notes)
    m = pd.read_csv(ROOT / 'paper_to_entity_map_v2.csv', dtype=str, keep_default_na=False)
    d = pd.read_csv(ROOT / 'papers_master_with_matching_text_v2.csv', dtype=str, keep_default_na=False)
    assert len(m) == len(d) == 11342 and N['n_records'].sum() == len(d)
    out = []
    say = out.append

    say('# v2 entity fragmentation diagnostics\n')
    say(f'{len(N)} entities, {len(d)} records. n_papers = distinct paper_key (paper_index.csv, after the approved merges).\n')

    # a. buckets
    say('## a. Entities by n_papers\n')
    bins = [(1, 1, '1'), (2, 2, '2'), (3, 5, '3-5'), (6, 10, '6-10'), (11, 10**9, '11+')]
    say('| n_papers | entities | share of entities | records | share of records |')
    say('|---|---|---|---|---|')
    for lo, hi, lab in bins:
        s = N[(N['n_papers'] >= lo) & (N['n_papers'] <= hi)]
        say(f'| {lab} | {len(s)} | {len(s) / len(N):.1%} | {s["n_records"].sum()} | {s["n_records"].sum() / len(d):.1%} |')
    multi = N[N['n_papers'] >= 2]
    say(f'\nRecords in entities with >= 2 papers: {multi["n_records"].sum()} ({multi["n_records"].sum() / len(d):.1%}).\n')

    # b. 40 random single-paper entities
    say('## b. 40 random single-paper entities (seed 0)\n')
    say('| entity | canonical_name | Category | venue | aliases (up to 3) |')
    say('|---|---|---|---|---|')
    for _, r in N[N['n_papers'] == 1].sample(40, random_state=0).iterrows():
        venue = ', '.join(v for v, c in r['venues'].items() if c)
        say(f'| {r.entity_id} | {r.canonical_name} | {r.category} | {venue} | {"; ".join(r.aliases[:3])} |')
    say('')

    # c. instance / variant look
    say('## c. Entities that look like instances or variants\n')
    nm = N['canonical_name']
    crit = {
        'name ends in digits': nm.map(lambda s: bool(TAIL_DIGIT_RE.search(s))),
        'contains "instance"': nm.map(lambda s: bool(INSTANCE_RE.search(s))),
        'parameters in parentheses, e.g. (m=3)': nm.map(lambda s: bool(PARAM_RE.search(s))),
        'starts with a library prefix + number (tai12, bayg29, bal8, ...)': nm.map(lambda s: bool(LIB_RE.match(s.strip()))),
    }
    say('| criterion | Applied | Pure Math | total |')
    say('|---|---|---|---|')
    anyc = pd.Series(False, index=N.index)
    for k, v in crit.items():
        anyc |= v
        say(f'| {k} | {int((v & (N.category == "Applied")).sum())} | {int((v & (N.category == "Pure Math")).sum())} | {int(v.sum())} |')
    say(f'| **any of the above** | {int((anyc & (N.category == "Applied")).sum())} | '
        f'{int((anyc & (N.category == "Pure Math")).sum())} | {int(anyc.sum())} ({anyc.mean():.1%}) |')
    say(f'\nOf the single-paper entities, {int((anyc & (N.n_papers == 1)).sum())} of {int((N.n_papers == 1).sum())} '
        f'match at least one criterion. Library-prefix list used: {", ".join(LIB_PREFIX)}.\n')

    # d. dataset provenance
    say('## d. Dataset_Name / Source_Platform per entity\n')
    say('Entity-level: "present" if any member row has a real value; else "Custom Simulated Data" if any row says so; '
        'else "not reported" (Not Reported or N/A-style).\n')
    rows = d.assign(entity_id=m['entity_id'].values)
    cat = dict(zip(N['entity_id'], N['category']))

    def classify(vals):
        vals = [v.strip() for v in vals]
        if any(v and not MISSING_RE.match(v) and v.lower() != CUSTOM for v in vals):
            return 'present'
        if any(v.lower() == CUSTOM for v in vals):
            return 'Custom Simulated Data'
        return 'not reported'
    for col in ['Dataset_Name', 'Source_Platform']:
        cls = rows.groupby('entity_id')[col].agg(classify)
        t = pd.crosstab(cls.index.map(cat), cls.values)
        say(f'**{col}**\n')
        say('| Category | ' + ' | '.join(t.columns) + ' |')
        say('|---|' + '---|' * len(t.columns))
        for c, r in t.iterrows():
            say(f'| {c} | ' + ' | '.join(str(int(x)) for x in r) + ' |')
        say('')

    # e. audit candidates
    say('## e. Audit candidates (entity_dedup_candidates_v2.csv)\n')
    a = pd.read_csv(ROOT / 'entity_dedup_candidates_v2.csv')
    rem = a[~(a['is_likely_numbered_variant'] | a['is_likely_named_instance_variant'])]
    true = rem[rem['name_word_overlap'] >= 0.6].copy()
    npap = dict(zip(N['entity_id'], N['n_papers']))
    true['papers_a'] = true['entity_id_a'].map(npap)
    true['papers_b'] = true['entity_id_b'].map(npap)
    true['combined_papers'] = true['papers_a'] + true['papers_b']
    deg = defaultdict(set)
    for _, r in true.iterrows():
        deg[r.entity_id_a].add(r.entity_id_b)
        deg[r.entity_id_b].add(r.entity_id_a)
    true['isolated'] = true.apply(lambda r: len(deg[r.entity_id_a]) == 1 and len(deg[r.entity_id_b]) == 1, axis=1)
    say(f'{len(a)} same-Category pairs with cosine >= 0.95; {len(true)} near-synonym candidates (not numbered/'
        f'named-instance variants, name word overlap >= 0.6), {int(true["isolated"].sum())} isolated 1:1 pairs. '
        f'Paper counts below are paper_key counts.\n')

    def table(frame):
        say('| similarity | Category | entity A | papers | entity B | papers | overlap |')
        say('|---|---|---|---|---|---|---|')
        for _, r in frame.iterrows():
            say(f'| {r.similarity:.3f} | {r.category} | {r.entity_id_a} {r.name_a} | {r.papers_a} | '
                f'{r.entity_id_b} {r.name_b} | {r.papers_b} | {r.name_word_overlap:.2f} |')
        say('')
    say(f'Combined paper counts across all {len(true)} candidates: '
        f'{true["combined_papers"].value_counts().sort_index().to_dict()}; distinct entities involved: '
        f'{len(set(true.entity_id_a) | set(true.entity_id_b))}.'
        + (' Every candidate pairs two single-paper entities, so the "40 largest" below are ties, ordered by '
           'similarity.' if true['combined_papers'].nunique() == 1 else '') + '\n')
    say('**40 largest by combined paper count**\n')
    table(true.sort_values(['combined_papers', 'similarity'], ascending=False).head(40))
    say('**The isolated 1:1 pairs**\n')
    table(true[true['isolated']].sort_values('similarity', ascending=False))

    text = '\n'.join(out) + '\n'
    OUT.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    sys.exit(main())
