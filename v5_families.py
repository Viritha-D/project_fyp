"""
Family layer v5 (family_rules_v5.json), correcting v4.

One key per entity: standard_suite > template > stem > single. The stem key is (a) the plain v3
stem (>= 4 letters, no numbers needed) or, for entities (a) does not group, (b) the v4
numbered-series rule with numbers of >= 4 digits ignored. Template edits: 2 for 5-7 tokens, 3
for >= 8, never above 40% of the tokens. Library cues are attribute-only. Entities, ids, notes,
embeddings, paper_index.csv and all v3 / v4 files are read, never written.

Outputs: families_v5.json, entity_to_family_v5.csv, family_notes_v5.json,
labeling/family_review_sample_v5_delta_blind.csv, labeling/family_review_key_v5_delta.csv
Usage: python v5_families.py
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

import v2_families as v2
import v3_families as v3     # suite_key / template_name / cues_with_papers (rule sections asserted equal below)

ROOT = Path(__file__).resolve().parent
R = json.loads((ROOT / 'family_rules_v5.json').read_text(encoding='utf-8'))
assert R['standard_suites'] == v3.R['standard_suites'] and R['stem'] == v3.R['stem']
assert R['instance_ids'] == v3.R['instance_ids'] and R['library_cue']['cues'] == v3.R['library_cue']['cues']
KIND = R['primary_key']['family_kind']
TPL, NS, SK = R['template'], R['numbered_series'], R['stem_key']
GENERIC_Q = set(NS['generic_qualifiers'])
MISSING = v2.MISSING
GRID = re.compile(r'Hyper-parameter Optimization .*Software Bug Prediction', re.I)
OUT_FAM, OUT_E2F, OUT_NOTES = ROOT / 'families_v5.json', ROOT / 'entity_to_family_v5.csv', ROOT / 'family_notes_v5.json'
LAB = ROOT / 'labeling'


def norm_ctx(s):
    return ' '.join(re.findall(r'[a-z0-9]+', str(s).lower()))


def series_parts(name, primary_ctx):
    """(base, qualifier, numbers) for the numbered-series rule."""
    s = v2.us(name)
    paren = ' '.join(re.findall(r'\(([^()]*)\)|\[([^\[\]]*)\]', s) and
                     [a or b for a, b in re.findall(r'\(([^()]*)\)|\[([^\[\]]*)\]', s)])
    outside = v2.unparen(s)
    base = ' '.join(re.findall(r'[a-z]+', outside))
    numbers = tuple(int(x) for x in re.findall(r'\d+', outside))
    q = ' '.join(t for t in re.findall(r'[a-z]+', paren) if len(t) >= NS['qualifier_min_token_letters'])
    if not q:
        q = norm_ctx(primary_ctx)
    if q in GENERIC_Q:
        q = ''
    return base, q, numbers


def template_ok(a, b, ca, cb):
    if not ca or ca != cb:
        return False
    da, db = [t for t in a if re.search(r'\d', t)], [t for t in b if re.search(r'\d', t)]
    if da != db or a == b:
        return False
    wa, wb = [t for t in a if not re.search(r'\d', t)], [t for t in b if not re.search(r'\d', t)]
    cap = max_edits(min(len(a), len(b)))
    return v2.token_edits(wa, wb, cap) <= cap


def max_edits(n):
    """2 edits for names of 5-7 tokens, 3 for >= 8, never more than 40% of the tokens."""
    base = TPL['edits_long'] if n >= TPL['long_from_tokens'] else TPL['edits_short']
    return min(base, int(TPL['max_edit_share'] * n))


def series_numbers(nums):
    return tuple(n for n in nums if len(str(n)) < SK['ignore_digits_from'])


def main():
    notes = json.loads((ROOT / 'entity_notes_v2.json').read_text(encoding='utf-8'))
    order = (ROOT / 'entity_ids_order_v2.txt').read_text(encoding='utf-8').splitlines()
    m = pd.read_csv(ROOT / 'paper_to_entity_map_v2.csv', dtype=str, keep_default_na=False)
    d = pd.read_csv(ROOT / 'papers_master_with_matching_text_v2.csv', dtype=str, keep_default_na=False)
    idx = pd.read_csv(ROOT / 'paper_index.csv', dtype=str, keep_default_na=False)
    v3e = pd.read_csv(ROOT / 'entity_to_family_v3.csv', dtype=str, keep_default_na=False)
    v3f = {f['family_id']: f for f in json.loads((ROOT / 'families_v3.json').read_text(encoding='utf-8'))}
    assert order == [n['entity_id'] for n in notes]
    N = pd.DataFrame(notes).set_index('entity_id')
    rows = d.assign(entity_id=m['entity_id'].values, paper_key=m['paper_key'].values)
    by_e = {e: g for e, g in rows.groupby('entity_id')}

    def primary_ctx(e):
        g = by_e[e][by_e[e]['Problem_Context'].map(lambda v: v.strip() not in MISSING)]
        if g.empty:
            return ''
        return g.groupby('Problem_Context')['paper_key'].nunique().sort_values(ascending=False, kind='stable').index[0]

    E = pd.DataFrame({'entity_id': order, 'name': [N.at[e, 'canonical_name'] for e in order],
                      'category': [N.at[e, 'category'] for e in order],
                      'n_papers': [int(N.at[e, 'n_papers']) for e in order],
                      'n_records': [int(N.at[e, 'n_records']) for e in order]})
    E['ctx'] = E['entity_id'].map(primary_ctx)
    E['ctx_norm'] = E['ctx'].map(norm_ctx)
    E['stem'] = E['name'].map(v2.stem)
    E['ttok'] = E['name'].map(v2.template_tokens)
    E['suite_memberships'] = [v3.cues_with_papers(by_e[e]) for e in order]
    parts = {r.entity_id: series_parts(r.name, r.ctx) for r in E.itertuples()}

    key = {}
    # pass 1: standard suite
    for r in E.itertuples():
        s = v3.suite_key(r.name, r.stem)
        if s:
            key[r.entity_id] = ('standard_suite', f'suite:{s[0]}', s[1])
    # pass 2: template components (same Category, same primary context)
    tok = dict(zip(E['entity_id'], E['ttok']))
    for cat, g in E[~E['entity_id'].isin(key)].groupby('category'):
        cand = [(r.entity_id, r.ttok, set(r.ttok), r.ctx_norm) for r in g.itertuples() if len(r.ttok) >= TPL['min_tokens']]
        uf = v2.UF([c[0] for c in cand])
        cap = TPL['edits_long']                       # widest possible allowance, for the pre-filter only
        for (a, ta, sa, ca), (b, tb, sb, cb) in combinations(cand, 2):
            if ca != cb or abs(len(ta) - len(tb)) > cap or len(sa & sb) < max(len(ta), len(tb)) - cap:
                continue
            if template_ok(ta, tb, ca, cb):
                uf.union(a, b)
        comps = defaultdict(list)
        for c in cand:
            comps[uf.find(c[0])].append(c[0])
        for root, ids in comps.items():
            if len(ids) >= 2:
                nm = v3.template_name([tok[e] for e in sorted(ids)])
                for e in ids:
                    key[e] = ('template', f'template:{cat}:{root}', nm)
    # pass 3: stem key (same Category): (a) plain v3 stem, then (b) numbered series for the rest
    rem = E[~E['entity_id'].isin(key)]
    plain = rem[rem['stem'].map(lambda st: len(st.replace(' ', '')) >= SK['min_plain_letters'])]
    for (cat, st), g in plain.groupby(['category', 'stem']):
        if len(g) >= 2:
            for e in g['entity_id']:
                key[e] = ('stem_plain', f'stem:{cat}:{st}', st)

    def series_groups(ignore_long_ids):
        groups = defaultdict(list)
        for r in E[~E['entity_id'].isin(key)].itertuples():
            base, q, nums = parts[r.entity_id]
            if ignore_long_ids:
                nums = series_numbers(nums)
            if not nums or not base:
                continue
            if len(base.replace(' ', '')) >= NS['min_base_letters']:
                groups[(r.category, base, '')].append((r.entity_id, nums))
            elif q:
                groups[(r.category, base, q)].append((r.entity_id, nums))
        return {k: v for k, v in groups.items()
                if len(v) >= NS['min_series_members'] and len({n for _, n in v}) >= 2}
    with_rule3, without_rule3 = series_groups(True), series_groups(False)
    removed_by_rule3 = {k: [e for e, _ in v] for k, v in without_rule3.items() if k not in with_rule3}
    for (cat, base, q), members in with_rule3.items():
        label = f'{base} ({q}) series' if q else f'{base} series'
        for e, _ in members:
            key[e] = ('stem_series', f'series:{cat}:{base}|{q}', label)
    for e in order:
        key.setdefault(e, ('single', f'single:{e}', None))
    E['key_type'] = E['entity_id'].map(lambda e: 'stem' if key[e][0].startswith('stem_') else key[e][0])
    E['family_key'] = E['entity_id'].map(lambda e: key[e][1])

    # ---------------- families (same record format as v3) ----------------
    fam_groups = defaultdict(list)
    for e in order:
        fam_groups[key[e][1]].append(e)
    fam_order = sorted(fam_groups.items(), key=lambda kv: min(kv[1]))
    fid = {e: f'F{i:05d}' for i, (_, ids) in enumerate(fam_order, 1) for e in ids}
    E['family_id'] = E['entity_id'].map(fid)
    rows['family_id'] = rows['entity_id'].map(fid)
    flags = dict(zip(idx['paper_key'], idx['flags']))
    real = lambda s: [v for v in s if v.strip() and v.strip() not in MISSING]
    families, fnotes = [], []
    for fkey, ids in fam_order:
        kt = key[ids[0]][0]
        f = fid[ids[0]]
        g = rows[rows['family_id'] == f]
        mem = E[E['entity_id'].isin(ids)].sort_values(['n_papers', 'n_records', 'entity_id'], ascending=[False, False, True])
        name = mem.iloc[0]['name'] if kt == 'single' else key[ids[0]][2]
        cats = Counter(mem['category'])
        cat_counts = {c: {'entities': int(n), 'records': int((g['Category'] == c).sum())} for c, n in sorted(cats.items())}
        n_pap = int(g['paper_key'].nunique())
        venues = {v: int((g.drop_duplicates('paper_key')['Conference'] == v).sum()) for v in v2.VENUES}
        memberships = v3.cues_with_papers(g)
        tasks = g[g['Problem_Context'].map(lambda v: v.strip() not in MISSING)].groupby('Problem_Context')['paper_key'] \
            .nunique().sort_values(ascending=False, kind='stable')
        top_tasks = [{'task': t, 'n_papers': int(c)} for t, c in tasks.head(5).items()]
        ds = [v.strip() for v in g['Dataset_Name']]
        has_real_ds = any(v and not v2.MISSING_RE.match(v) and v.lower() != v2.CUSTOM for v in ds)
        signals = [s for s, ok in [('library_cue', bool(memberships)), ('n_papers>=2', n_pap >= 2),
                                   ('multiple_venues', sum(1 for c in venues.values() if c) >= 2),
                                   ('standard_suite_name', kt == 'standard_suite'),
                                   ('custom_data_only', not has_real_ds and any(v.lower() == v2.CUSTOM for v in ds)),
                                   ('single_paper', n_pap == 1)] if ok]
        fam = {'family_id': f, 'family_name': name, 'family_kind': KIND[kt], 'family_key': fkey,
               'category': next(iter(cats)) if len(cats) == 1 else 'mixed', 'category_counts': cat_counts,
               'member_entity_ids': mem['entity_id'].tolist(), 'n_members': len(ids), 'n_papers': n_pap,
               'n_records': int(len(g)), 'venues': venues,
               'suite_memberships': [{'cue': c, 'n_papers': n} for c, n in memberships], 'top_tasks': top_tasks,
               'reuse_signals': signals}
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
        cav = [c for c, ok in [('ppsn_partial', (g['Conference'] == 'PPSN').any()),
                               ('premi_year_unverified', g['paper_key'].map(lambda k: 'year_unverified' in flags[k]).any()),
                               ('single_paper', n_pap == 1),
                               ('sparse_metadata', sum(not real(g[c]) for c in ('Dimensionality', 'Modality', 'Separability',
                                                                                'Landscape_Characteristics')) >= 3)] if ok]
        n.update({'evidence_caveats': cav, 'suite_memberships': fam['suite_memberships'],
                  'members': [{'entity_id': r.entity_id, 'name': r.name, 'n_papers': int(r.n_papers)} for r in mem.head(10).itertuples()],
                  'reuse_signals': signals, 'top_tasks': top_tasks})
        text, k = v2.family_note_text({**n, 'category': n['category'] if n['category'] != 'mixed' else
                                       'mixed: ' + ', '.join(f"{c} {v['entities']}" for c, v in cat_counts.items())}, len(ids))
        if memberships and k < 4:
            text += ' Rows cite ' + '; '.join(f'{c} ({p} paper{"s" if p != 1 else ""})' for c, p in memberships[:4]) + '.'
            k += 1
        assert 2 <= k <= 4
        n['note_text'] = text
        fnotes.append(n)

    # ---------------- assertions ----------------
    e2f = E[['entity_id', 'family_id', 'key_type', 'family_key', 'name', 'category', 'n_papers', 'n_records']].rename(
        columns={'name': 'canonical_name'})
    e2f['primary_problem_context'] = E['ctx']
    e2f['suite_memberships'] = E['suite_memberships'].map(lambda s: '; '.join(f'{c} ({p})' for c, p in s))
    assert e2f['entity_id'].is_unique and len(e2f) == len(order) and e2f['family_id'].notna().all(), 'entity not in exactly one family'
    root_to_key = {r: k for k, rs in zip(idx['paper_key'], idx['paper_id_roots']) for r in rs.split(';')}
    pk_idx = d['Paper_ID'].str.replace(r'_Ext_\d+$', '', regex=True).map(root_to_key)
    fam_pk = pd.Series(pk_idx.values).groupby(rows['family_id'].values).nunique()
    assert all(fam_pk[f['family_id']] == f['n_papers'] for f in families), 'family n_papers != paper_index count'
    assert all(f['n_papers'] > 0 for f in families) and sum(f['n_records'] for f in families) == len(d)
    assert all(len({key[e][1] for e in f['member_entity_ids']}) == 1 for f in families)
    assert all(f['category'] != 'mixed' or f['family_kind'] == 'suite_series' for f in families)  # stem keys are per Category
    print(f'assertions passed: {len(order)} entities each in exactly one of {len(families)} families (one key each); '
          f'family n_papers equals the paper_index count of its members\' rows; no family has 0 papers; records sum to {len(d)}')
    OUT_FAM.write_text(json.dumps(families, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    e2f.to_csv(OUT_E2F, index=False)
    OUT_NOTES.write_text(json.dumps(fnotes, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    labelled = {frozenset(p) for f in ('family_review_key_v3.csv', 'family_review_key_v4.csv')
                for p in pd.read_csv(LAB / f, dtype=str)[['entity_id_a', 'entity_id_b']].values}
    assert len(labelled) == 140, len(labelled)
    v4e = pd.read_csv(ROOT / 'entity_to_family_v4.csv', dtype=str, keep_default_na=False)
    v4f = {f['family_id']: f for f in json.loads((ROOT / 'families_v4.json').read_text(encoding='utf-8'))}
    pack = build_delta_pack(E, key, fid, by_e, N, labelled, dict(zip(v4e.entity_id, v4e.family_id)))
    report(E, families, v3e, v3f, v4e, v4f, fid, key, len(d), pack, removed_by_rule3)


# ---------------------------------------------------------------- delta labelling pack
def build_delta_pack(E, key, fid, by_e, N, labelled, v4fam):
    """Up to 20 pairs merged in v5 but not in v4, not already labelled; one pair per v5 family first."""
    rnd = random.Random(5)
    fams = defaultdict(list)
    for e in E['entity_id']:
        fams[fid[e]].append(e)
    per_family = []
    for f, ids in fams.items():
        pairs = [(a, b) for a, b in combinations(sorted(ids), 2)
                 if v4fam[a] != v4fam[b] and frozenset((a, b)) not in labelled]
        if pairs:
            rnd.shuffle(pairs)
            per_family.append(pairs)
    n_new = sum(len(p) for p in per_family)
    rnd.shuffle(per_family)
    chosen = []
    while len(chosen) < 20 and any(per_family):     # round-robin over families
        for pairs in per_family:
            if pairs and len(chosen) < 20:
                chosen.append(pairs.pop())
    rnd.shuffle(chosen)

    def ctx2(e):
        g = by_e[e][by_e[e]['Problem_Context'].map(lambda v: v.strip() not in MISSING)]
        return g.groupby('Problem_Context')['paper_key'].nunique().sort_values(ascending=False, kind='stable').index[:2].tolist()

    def side(e, s):
        return {f'name_{s}': N.at[e, 'canonical_name'], f'aliases_{s}': ' | '.join(N.at[e, 'aliases'][:5]),
                f'category_{s}': N.at[e, 'category'],
                f'venues_{s}': '; '.join(f'{v} ({c})' for v, c in N.at[e, 'venues'].items() if c),
                f'sample_problem_contexts_{s}': ' | '.join(ctx2(e))}
    blind, keyf = [], []
    for i, (a, b) in enumerate(chosen, 1):
        pid = f'D{i:02d}'
        kt = key[a][0]
        blind.append({'pair_id': pid, **side(a, 'a'), **side(b, 'b'), 'same_family (y/n/unsure)': '', 'notes': ''})
        keyf.append({'pair_id': pid, 'entity_id_a': a, 'entity_id_b': b, 'pair_type': f'new_in_v5_{KIND[kt]}',
                     'evidence': f'{KIND[kt]}: {key[a][2]}', 'family_v5': fid[a], 'family_v4_a': v4fam[a], 'family_v4_b': v4fam[b]})
    B, K = pd.DataFrame(blind), pd.DataFrame(keyf)
    assert not ({frozenset(p) for p in K[['entity_id_a', 'entity_id_b']].values} & labelled)
    assert all(fid[a] == fid[b] and v4fam[a] != v4fam[b] for a, b in K[['entity_id_a', 'entity_id_b']].values)
    text = ' '.join(B.astype(str).agg(' '.join, axis=1))
    assert not any(t in text for t in ('new_in_v5', 'suite:', 'series:', 'template:', 'stem:')), 'answer leak'
    B.to_csv(LAB / 'family_review_sample_v5_delta_blind.csv', index=False)
    K.to_csv(LAB / 'family_review_key_v5_delta.csv', index=False)
    instr = (LAB / 'labeling_instructions.md').read_text(encoding='utf-8').replace(
        'You will label 80 pairs of benchmark problems in `family_review_sample_v3_blind.csv`.',
        f'You will label {len(B)} pairs of benchmark problems in `family_review_sample_v5_delta_blind.csv`.')
    assert f'{len(B)} pairs' in instr
    (LAB / 'labeling_instructions_v5_delta.md').write_text(instr, encoding='utf-8')
    return K, n_new


def report(E, families, v3e, v3f, v4e, v4f, fid, key, n_records, pack, removed_by_rule3):
    F = pd.DataFrame(families)
    print(f'\nfamilies: {len(F)} (v3: 2,027; v4: 2,391); by kind {F.family_kind.value_counts().to_dict()}')
    print(f'entities by key type: {E.key_type.value_counts().to_dict()}; stem rule (a) plain '
          f'{sum(1 for e in E.entity_id if key[e][0] == "stem_plain")}, (b) numbered series '
          f'{sum(1 for e in E.entity_id if key[e][0] == "stem_series")}')
    multi = F[F.n_papers >= 2]
    print(f'share of records in families with >= 2 papers: {multi.n_records.sum() / n_records:.1%} '
          f'({multi.n_records.sum()} of {n_records}; v3 46.7%, v4 37.3%)')
    v5sets = E.groupby('family_id')['entity_id'].apply(frozenset).to_dict()
    for lab, ve in (('v3', v3e), ('v4', v4e)):
        fam = dict(zip(ve.entity_id, ve.family_id))
        sets = ve.groupby('family_id')['entity_id'].apply(frozenset).to_dict()
        ch = sum(1 for e in E.entity_id if sets[fam[e]] != v5sets[fid[e]])
        print(f'entities whose co-members changed vs {lab}: {ch} of {len(E)}')
    print('\nrule 3 (ignore numbers with >= 4 digits) removes these numbered series:')
    name = dict(zip(E.entity_id, E.name))
    if not removed_by_rule3:
        print('  none')
    for (cat, base, q), ids in removed_by_rule3.items():
        now = Counter(key[e][0] for e in ids)
        print(f'  [{cat}] "{base}{" (" + q + ")" if q else ""} series": {len(ids)} entities, e.g. '
              f'{[name[e][:30] for e in ids[:3]]} -> now {dict(now)}')
    print('\n8 largest families:')
    for f in F.sort_values(['n_members', 'n_records'], ascending=False).head(8).itertuples():
        print(f'  {f.family_id} {f.family_name[:60]!r} [{f.family_kind}, {f.category}] {f.n_members} entities, {f.n_papers} papers')
    t = F[F.family_kind == 'template_grid']
    print(f'\ntemplate families: {len(t)} (v4: 40), {int(t.n_members.sum())} entities; 5 largest:')
    for f in t.sort_values(['n_members', 'n_records'], ascending=False).head(5).itertuples():
        print(f'  {f.family_id} {f.family_name[:70]!r} [{f.category}] {f.n_members} entities, {f.n_papers} papers')
    gone = '{...} problem' not in set(t.family_name)
    print(f'"{{...}} problem" template family gone: {gone}')
    g = E[E['name'].str.contains(GRID)]
    print(f'bug-prediction grid: {len(g)} entities in {g.family_id.nunique()} families')
    K, n_new = pack
    print(f'\ndelta pack: {n_new} new v5 pairs not merged in v4 and not labelled; {len(K)} in the pack '
          f'{K.pair_type.value_counts().to_dict()}')


if __name__ == '__main__':
    sys.exit(main())
