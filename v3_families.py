"""
Family layer v3 (family_rules_v3.json): one primary family key per entity, no union across rules.

Priority: standard_suite > stem > template > library_cue > single. Suite and stem keys may span
both Categories ("mixed"); template and library-cue keys stay within one Category. Library cues
found on an entity's rows are kept as suite_memberships (attribute only). Entities, ids, notes,
embeddings and paper_index.csv are read, never written. Embedding similarity never merges.

Outputs: families_v3.json, entity_to_family_v3.csv, family_notes_v3.json,
family_candidates_v3.csv, family_review_sample_v3.csv
Usage: python v3_families.py
"""

import json
import random
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

import v2_families as v2   # stem / template tokens / cue helpers; their rule sections are asserted equal below

ROOT = Path(__file__).resolve().parent
R = json.loads((ROOT / 'family_rules_v3.json').read_text(encoding='utf-8'))
for sec in ('spelling_us', 'instance_ids'):
    assert R[sec] == v2.R[sec], f'{sec} differs from the v2 helpers'
assert {k: v for k, v in R['stem'].items() if k != '_description'} == {k: v for k, v in v2.R['stem'].items() if k != '_description'}
assert R['library_cue']['cues'] == v2.R['library_cue']['cues']

SUITES = [(s['key'], s['name'], re.compile(s['regex'], re.I)) for s in R['standard_suites']['suites']]
KIND = R['primary_key']['family_kind']
CROSS = set(R['primary_key']['cross_category'])
TPL = R['template']
MISSING = v2.MISSING
VENUES = v2.VENUES
OUT_FAM, OUT_E2F, OUT_NOTES = ROOT / 'families_v3.json', ROOT / 'entity_to_family_v3.csv', ROOT / 'family_notes_v3.json'
OUT_CAND, OUT_REVIEW = ROOT / 'family_candidates_v3.csv', ROOT / 'family_review_sample_v3.csv'
V2_RANDOM15 = ['F01940', 'F02118', 'F00371', 'F01397', 'F01272', 'F00969', 'F01044', 'F01512', 'F00349', 'F00899',
               'F01261', 'F01727', 'F00822', 'F00326', 'F00166']   # the 15 random v2 families shown in the v2 report


def suite_key(name, stem):
    hits = []
    for order, (key, label, rx) in enumerate(SUITES):
        m = rx.search(name)
        if m:
            if '{year}' in key:
                y = m.group(1)
                y = y if len(y) == 4 else '20' + y
                key, label = key.format(year=y), label.format(year=y)
            hits.append((m.start(), order, key, label))
    if not hits and stem in ('tsplib instance', 'qaplib instance'):
        lib = stem.split()[0]
        return lib, lib.upper()
    if not hits:
        return None
    _, _, key, label = min(hits)
    return key, label


def template_match(a, b):
    """Tokens with digits identical (same sequence); other tokens within max_token_edits."""
    da, db = [t for t in a if re.search(r'\d', t)], [t for t in b if re.search(r'\d', t)]
    if da != db:
        return False
    wa, wb = [t for t in a if not re.search(r'\d', t)], [t for t in b if not re.search(r'\d', t)]
    return a != b and v2.token_edits(wa, wb, TPL['max_token_edits']) <= TPL['max_token_edits']


def template_name(token_lists):
    first = token_lists[0]
    common = set(first).intersection(*map(set, token_lists[1:]))
    out = []
    for t in first:
        if t in common:
            out.append(t)
        elif not out or out[-1] != '{...}':
            out.append('{...}')
    return ' '.join(out)


def cues_with_papers(g):
    found = defaultdict(set)
    for ds, sp, pk in zip(g['Dataset_Name'], g['Source_Platform'], g['paper_key']):
        for v in (ds, sp):
            for cue, rx in v2.CUES:
                m = rx.search(v)
                if m:
                    if '{year}' in cue:
                        y = m.group(1)
                        cue = cue.format(year=y if len(y) == 4 else '20' + y)
                    found[cue].add(pk)
    return sorted(((c, len(p)) for c, p in found.items()), key=lambda x: (-x[1], x[0]))


def main():
    notes = json.loads((ROOT / 'entity_notes_v2.json').read_text(encoding='utf-8'))
    emb = np.load(ROOT / 'entity_embeddings_v2.npy')
    order = (ROOT / 'entity_ids_order_v2.txt').read_text(encoding='utf-8').splitlines()
    m = pd.read_csv(ROOT / 'paper_to_entity_map_v2.csv', dtype=str, keep_default_na=False)
    d = pd.read_csv(ROOT / 'papers_master_with_matching_text_v2.csv', dtype=str, keep_default_na=False)
    idx = pd.read_csv(ROOT / 'paper_index.csv', dtype=str, keep_default_na=False)
    v2fam = pd.read_csv(ROOT / 'entity_to_family_v2.csv', dtype=str, keep_default_na=False)
    assert order == [n['entity_id'] for n in notes] and emb.shape[0] == len(order)
    N = pd.DataFrame(notes).set_index('entity_id')
    rows = d.assign(entity_id=m['entity_id'].values, paper_key=m['paper_key'].values)
    by_e = {e: g for e, g in rows.groupby('entity_id')}

    E = pd.DataFrame({'entity_id': order, 'name': [N.at[e, 'canonical_name'] for e in order],
                      'category': [N.at[e, 'category'] for e in order],
                      'n_papers': [int(N.at[e, 'n_papers']) for e in order],
                      'n_records': [int(N.at[e, 'n_records']) for e in order]})
    E['stem'] = E['name'].map(v2.stem)
    E['ttok'] = E['name'].map(v2.template_tokens)
    E['cue'] = [v2.cue_of(list(by_e[e]['Dataset_Name']) + list(by_e[e]['Source_Platform'])) for e in order]
    E['suite_memberships'] = [cues_with_papers(by_e[e]) for e in order]

    key = {}       # entity -> (kind, family key, display name)
    # pass 1: standard suite (always, even alone)
    for r in E.itertuples():
        s = suite_key(r.name, r.stem)
        if s:
            key[r.entity_id] = ('standard_suite', f'suite:{s[0]}', s[1])
    # pass 2: stem shared by >= 2 remaining entities (any Category)
    rem = E[~E['entity_id'].isin(key) & (E['stem'] != '')]
    for st, g in rem.groupby('stem'):
        if len(g) >= 2:
            for e in g['entity_id']:
                key[e] = ('stem', f'stem:{st}', st)
    # pass 3: template components among remaining entities, within Category
    rem = E[~E['entity_id'].isin(key)]
    for cat, g in rem.groupby('category'):
        cand = [(r.entity_id, r.ttok, set(r.ttok)) for r in g.itertuples() if len(r.ttok) >= TPL['min_tokens']]
        uf = v2.UF([c[0] for c in cand])
        cap = TPL['max_token_edits']
        for (a, ta, sa), (b, tb, sb) in combinations(cand, 2):
            if abs(len(ta) - len(tb)) > cap or len(sa & sb) < max(len(ta), len(tb)) - cap:
                continue
            if template_match(ta, tb):
                uf.union(a, b)
        comps = defaultdict(list)
        for c in cand:
            comps[uf.find(c[0])].append(c[0])
        tok = dict(zip(E['entity_id'], E['ttok']))
        for root, ids in comps.items():
            if len(ids) >= 2:
                nm = template_name([tok[e] for e in sorted(ids)])
                for e in ids:
                    key[e] = ('template', f'template:{cat}:{root}', nm)
    # pass 4: library cue shared by >= 2 remaining entities, within Category
    rem = E[~E['entity_id'].isin(key) & (E['cue'] != '')]
    for (cat, cue), g in rem.groupby(['category', 'cue']):
        if len(g) >= 2:
            for e in g['entity_id']:
                key[e] = ('library_cue', f'cue:{cat}:{cue}', cue)
    # rest: single
    for e in order:
        key.setdefault(e, ('single', f'single:{e}', None))
    E['key_type'] = E['entity_id'].map(lambda e: key[e][0])
    E['family_key'] = E['entity_id'].map(lambda e: key[e][1])

    # ---------------- families ----------------
    groups = defaultdict(list)
    for e in order:
        groups[key[e][1]].append(e)
    fam_order = sorted(groups.items(), key=lambda kv: min(kv[1]))
    fid = {}
    for i, (_, ids) in enumerate(fam_order, 1):
        for e in ids:
            fid[e] = f'F{i:05d}'
    E['family_id'] = E['entity_id'].map(fid)
    rows['family_id'] = rows['entity_id'].map(fid)
    flags = dict(zip(idx['paper_key'], idx['flags']))
    std_hit = {e: key[e][0] == 'standard_suite' for e in order}
    real = lambda s: [v for v in s if v.strip() and v.strip() not in MISSING]

    families, fnotes = [], []
    for fkey, ids in fam_order:
        kind_key = key[ids[0]][0]
        f = fid[ids[0]]
        g = rows[rows['family_id'] == f]
        mem = E[E['entity_id'].isin(ids)].sort_values(['n_papers', 'n_records', 'entity_id'], ascending=[False, False, True])
        if kind_key == 'single':
            name = mem.iloc[0]['name']
        elif kind_key == 'library_cue':
            task = g.groupby('Problem_Context')['paper_key'].nunique().sort_values(ascending=False, kind='stable')
            name = f"{key[ids[0]][2]} datasets ({task.index[0]})"
        elif kind_key == 'stem':
            name = key[ids[0]][2]
        else:
            name = key[ids[0]][2]
        cats = Counter(mem['category'])
        cat_counts = {c: {'entities': int(n), 'records': int(g[g['Category'] == c].shape[0])} for c, n in sorted(cats.items())}
        n_pap = int(g['paper_key'].nunique())
        venues = {v: int((g.drop_duplicates('paper_key')['Conference'] == v).sum()) for v in VENUES}
        memberships = cues_with_papers(g)
        ds = [v.strip() for v in g['Dataset_Name']]
        has_real_ds = any(v and not v2.MISSING_RE.match(v) and v.lower() != v2.CUSTOM for v in ds)
        signals = []
        if memberships:
            signals.append('library_cue')
        if n_pap >= 2:
            signals.append('n_papers>=2')
        if sum(1 for c in venues.values() if c) >= 2:
            signals.append('multiple_venues')
        if any(std_hit[e] for e in ids):
            signals.append('standard_suite_name')
        if not has_real_ds and any(v.lower() == v2.CUSTOM for v in ds):
            signals.append('custom_data_only')
        if n_pap == 1:
            signals.append('single_paper')
        fam = {'family_id': f, 'family_name': name, 'family_kind': KIND[kind_key], 'family_key': fkey,
               'category': next(iter(cats)) if len(cats) == 1 else 'mixed', 'category_counts': cat_counts,
               'member_entity_ids': mem['entity_id'].tolist(), 'n_members': len(ids), 'n_papers': n_pap,
               'n_records': int(len(g)), 'venues': venues,
               'suite_memberships': [{'cue': c, 'n_papers': n} for c, n in memberships], 'reuse_signals': signals}
        families.append(fam)

        yrs = g[(g['Conference'] != 'PReMI') & ~g['paper_key'].map(lambda k: 'year_unverified' in flags[k])]['Year']
        yrs = sorted(int(y) for y in yrs if y.isdigit())
        tags = Counter(t.strip() for v in g['Landscape_Characteristics'] for t in v.split(';') if t.strip() and t.strip() not in MISSING)
        algs = g[g['Algorithm_Name'].map(lambda v: v not in MISSING)].groupby('Algorithm_Name')['paper_key'].nunique()
        alias_papers = g.groupby('Benchmark_Name')['paper_key'].nunique().sort_values(ascending=False, kind='stable')
        n = {'family_id': f, 'family_name': name, 'family_kind': fam['family_kind'], 'category': fam['category'],
             'category_counts': cat_counts, 'aliases': alias_papers.index[:8].tolist(), 'n_papers': n_pap,
             'n_records': int(len(g)), 'venues': venues, 'year_range': [yrs[0], yrs[-1]] if yrs else None,
             'typical_dimensions': v2.top(Counter(real(g['Dimensionality'])), 3),
             'landscape': {'Modality': v2.top(Counter(real(g['Modality'])), 3),
                           'Separability': v2.top(Counter(real(g['Separability'])), 3),
                           'Landscape_Characteristics': v2.top(tags, 5)},
             'metrics': v2.top(Counter(real(g['Performance_Metric'])), 3),
             'commonly_compared_algorithms': [{'value': a, 'n_papers': int(c)} for a, c in
                                              algs.sort_values(ascending=False, kind='stable').head(5).items()],
             'industries': v2.top(Counter(real(g['Industry'])), 3) if (g['Category'] == 'Applied').any() else []}
        cav = []
        if (g['Conference'] == 'PPSN').any():
            cav.append('ppsn_partial')
        if g['paper_key'].map(lambda k: 'year_unverified' in flags[k]).any():
            cav.append('premi_year_unverified')
        if n_pap == 1:
            cav.append('single_paper')
        if sum(not real(g[c]) for c in ('Dimensionality', 'Modality', 'Separability', 'Landscape_Characteristics')) >= 3:
            cav.append('sparse_metadata')
        n['evidence_caveats'] = cav
        n['suite_memberships'] = fam['suite_memberships']
        n['members'] = [{'entity_id': r.entity_id, 'name': r.name, 'n_papers': int(r.n_papers)} for r in mem.head(10).itertuples()]
        n['reuse_signals'] = signals
        text, k = v2.family_note_text({**n, 'category': n['category'] if n['category'] != 'mixed' else
                                       'mixed: ' + ', '.join(f"{c} {v['entities']}" for c, v in cat_counts.items())}, len(ids))
        if memberships and k < 4:
            text += ' Rows cite ' + '; '.join(f'{c} ({p} paper{"s" if p != 1 else ""})' for c, p in memberships[:4]) + '.'
            k += 1
        assert 2 <= k <= 4
        n['note_text'] = text
        fnotes.append(n)

    # ---------------- assertions ----------------
    e2f = E[['entity_id', 'family_id', 'key_type', 'family_key', 'name', 'category', 'n_papers', 'n_records', 'stem', 'cue']].rename(
        columns={'name': 'canonical_name', 'cue': 'library_cue'})
    e2f['suite_memberships'] = E['suite_memberships'].map(lambda s: '; '.join(f'{c} ({p})' for c, p in s))
    assert e2f['entity_id'].is_unique and len(e2f) == len(order) and e2f['family_id'].notna().all(), 'entity not in exactly one family'
    root_to_key = {r: k for k, rs in zip(idx['paper_key'], idx['paper_id_roots']) for r in rs.split(';')}
    pk_idx = d['Paper_ID'].str.replace(r'_Ext_\d+$', '', regex=True).map(root_to_key)
    fam_pk = pd.Series(pk_idx.values).groupby(rows['family_id'].values).nunique()
    assert all(fam_pk[f['family_id']] == f['n_papers'] for f in families), 'family n_papers != paper_index count'
    assert all(f['n_papers'] > 0 for f in families), 'family with 0 papers'
    assert sum(f['n_records'] for f in families) == len(d)
    assert all(len({key[e][1] for e in f['member_entity_ids']}) == 1 for f in families), 'family with mixed keys'
    assert all(f['category'] != 'mixed' or f['family_kind'] in ('suite_series', 'stem_group') for f in families), \
        'mixed-Category family from a within-Category rule'
    print(f'assertions passed: {len(order)} entities each in exactly one of {len(families)} families (one key each); '
          f'family n_papers equals the paper_index count of its members\' rows; no family has 0 papers; records sum to {len(d)}; '
          f'mixed-Category families only from suite or stem keys')

    OUT_FAM.write_text(json.dumps(families, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    e2f.to_csv(OUT_E2F, index=False)
    OUT_NOTES.write_text(json.dumps(fnotes, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    # ---------------- embedding candidates (review only) ----------------
    th = R['embedding_candidates']['threshold']
    pos = {e: i for i, e in enumerate(order)}
    cand = []
    for cat, g in E.groupby('category'):
        ids = g['entity_id'].tolist()
        v = emb[[pos[e] for e in ids]]
        sims = v @ v.T
        for i, j in zip(*np.where(np.triu(sims, 1) >= th)):
            a, b = ids[i], ids[j]
            if fid[a] != fid[b]:
                cand.append(dict(similarity=round(float(sims[i, j]), 4), category=cat, entity_id_a=a, name_a=N.at[a, 'canonical_name'],
                                 family_a=fid[a], entity_id_b=b, name_b=N.at[b, 'canonical_name'], family_b=fid[b]))
    C = pd.DataFrame(cand).sort_values('similarity', ascending=False)
    C.to_csv(OUT_CAND, index=False)

    # ---------------- review sample v3 (80 pairs, new seed) ----------------
    rnd = random.Random(3)
    def row(kind, a, b, evidence):
        return {'entity_id_a': a, 'name_a': N.at[a, 'canonical_name'], 'category_a': N.at[a, 'category'],
                'n_papers_a': int(N.at[a, 'n_papers']), 'entity_id_b': b, 'name_b': N.at[b, 'canonical_name'],
                'category_b': N.at[b, 'category'], 'n_papers_b': int(N.at[b, 'n_papers']),
                'same_family (y/n)': '', 'notes': '', 'pair_type': kind, 'evidence': evidence,
                'family_a': fid[a], 'family_b': fid[b]}
    sample = []
    for kt in ('stem', 'template', 'library_cue'):
        fams = [ids for _, ids in fam_order if key[ids[0]][0] == kt and len(ids) >= 2]
        picks = rnd.sample(fams, min(10, len(fams)))
        while len(picks) < 10:
            picks.append(rnd.choice(fams))
        for ids in picks:
            a, b = rnd.sample(ids, 2)
            sample.append(row(f'merged_by_{kt}', a, b, f'{kt}: {key[a][2]}'))
    for _, r in C.sample(min(30, len(C)), random_state=3).iterrows():
        sample.append(row('candidate_not_merged', r.entity_id_a, r.entity_id_b, f'cosine {r.similarity:.3f}'))
    negs = set()
    while len(negs) < 20:
        a, b = rnd.sample(order, 2)
        if fid[a] != fid[b]:
            negs.add(tuple(sorted((a, b))))
    sample += [row('negative_control', a, b, 'random pair, different families') for a, b in sorted(negs)]
    rnd.shuffle(sample)
    pd.DataFrame(sample).to_csv(OUT_REVIEW, index=False)

    report(E, families, fnotes, C, sample, len(d), v2fam, fid)


def report(E, families, fnotes, C, sample, n_records, v2fam, fid):
    F = pd.DataFrame(families)
    print(f'\nfamilies: {len(F)} (v2: 2,136) from {len(E)} entities; by kind: {F.family_kind.value_counts().to_dict()}')
    print(f'entities by key type: {E.key_type.value_counts().to_dict()}')
    print(f'mixed-Category families: {int((F.category == "mixed").sum())}')
    for lo, hi, lab in [(1, 1, '1'), (2, 2, '2'), (3, 5, '3-5'), (6, 10, '6-10'), (11, 10**9, '11+')]:
        s = F[(F.n_papers >= lo) & (F.n_papers <= hi)]
        print(f'  n_papers {lab:5s} {len(s):5d} families, {s.n_records.sum():5d} records ({s.n_records.sum() / n_records:.1%})')
    multi = F[F.n_papers >= 2]
    print(f'share of records in families with >= 2 papers: {multi.n_records.sum() / n_records:.1%} '
          f'({multi.n_records.sum()} of {n_records}; v2 46.0%, entity level 26.3%)')
    combo = F.assign(sig=F.reuse_signals.map(lambda s: ' + '.join(s) if s else '(none)')).groupby('sig').agg(
        families=('family_id', 'size'), records=('n_records', 'sum')).sort_values('records', ascending=False)
    print('reuse_signals combinations (families, records):')
    for sig, r in combo.iterrows():
        print(f'  {r.families:5d} {r.records:5d}  {sig}')
    print(f'embedding candidates across families (review only): {len(C)}; review sample {Counter(s["pair_type"] for s in sample)}')
    print('\n5 largest families (by member entities):')
    for f in F.sort_values(['n_members', 'n_records'], ascending=False).head(5).itertuples():
        print(f'  {f.family_id} {f.family_name[:60]!r} [{f.family_kind}, {f.category}] {f.n_members} entities, '
              f'{f.n_papers} papers, {f.n_records} records')
    keytype = dict(zip(E.entity_id, E.key_type))
    print('\nTOP 25 families by n_papers (members with key type):')
    NN = {n['family_id']: n for n in fnotes}
    for f in F.sort_values(['n_papers', 'n_records'], ascending=False).head(25).itertuples():
        cc = '' if f.category != 'mixed' else ' ' + str({c: v['entities'] for c, v in f.category_counts.items()})
        print(f'  {f.family_id} {f.n_papers:3d}p {f.n_members:3d}e [{f.family_kind}, {f.category}{cc}] {f.family_name[:55]!r}')
        print('      ' + '; '.join(f"{x['name'][:30]} ({x['n_papers']}, {keytype[x['entity_id']]})" for x in NN[f.family_id]['members'][:5]))
    print('\nthe same 15 random v2 families -> v3:')
    for f2 in V2_RANDOM15:
        ents = v2fam[v2fam.family_id == f2]
        for _, r in ents.iterrows():
            f3 = fid[r.entity_id]
            fam = next(x for x in families if x['family_id'] == f3)
            print(f'  v2 {f2} {r.canonical_name[:42]!r} -> v3 {f3} [{fam["family_kind"]}] {fam["family_name"][:45]!r} '
                  f'({fam["n_members"]} entities, {fam["n_papers"]} papers)')


if __name__ == '__main__':
    sys.exit(main())
