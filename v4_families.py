"""
Family layer v4 (family_rules_v4.json), revised after the labelled v3 sample.

One key per entity: standard_suite > template > numbered_series > single. Library cues are
attribute-only (suite_memberships). Entities, ids, notes, embeddings, paper_index.csv and all v3
files are read, never written.

Outputs: families_v4.json, entity_to_family_v4.csv, family_notes_v4.json,
labeling/family_review_sample_v4_blind.csv, labeling/family_review_key_v4.csv,
labeling/labeling_instructions_v4.md
Usage: python v4_families.py
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
R = json.loads((ROOT / 'family_rules_v4.json').read_text(encoding='utf-8'))
assert R['standard_suites'] == v3.R['standard_suites'] and R['stem'] == v3.R['stem']
assert R['instance_ids'] == v3.R['instance_ids'] and R['library_cue']['cues'] == v3.R['library_cue']['cues']
KIND = R['primary_key']['family_kind']
TPL, NS = R['template'], R['numbered_series']
GENERIC_Q = set(NS['generic_qualifiers'])
MISSING = v2.MISSING
GRID = re.compile(r'Hyper-parameter Optimization .*Software Bug Prediction', re.I)
OUT_FAM, OUT_E2F, OUT_NOTES = ROOT / 'families_v4.json', ROOT / 'entity_to_family_v4.csv', ROOT / 'family_notes_v4.json'
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
    return v2.token_edits(wa, wb, TPL['max_token_edits']) <= TPL['max_token_edits']


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
        cap = TPL['max_token_edits']
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
    # pass 3: numbered series (same Category)
    groups = defaultdict(list)
    for r in E[~E['entity_id'].isin(key)].itertuples():
        base, q, nums = parts[r.entity_id]
        if not nums or not base:
            continue
        letters = len(base.replace(' ', ''))
        if letters >= NS['min_base_letters']:
            groups[(r.category, base, '')].append(r.entity_id)
        elif q:
            groups[(r.category, base, q)].append(r.entity_id)
    for (cat, base, q), ids in groups.items():
        if len(ids) >= NS['min_series_members'] and len({parts[e][2] for e in ids}) >= 2:
            label = f'{base} ({q}) series' if q else f'{base} series'
            for e in ids:
                key[e] = ('numbered_series', f'series:{cat}:{base}|{q}', label)
    for e in order:
        key.setdefault(e, ('single', f'single:{e}', None))
    E['key_type'] = E['entity_id'].map(lambda e: key[e][0])
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
    assert all(f['category'] != 'mixed' or f['family_kind'] == 'suite_series' for f in families)
    print(f'assertions passed: {len(order)} entities each in exactly one of {len(families)} families (one key each); '
          f'family n_papers equals the paper_index count of its members\' rows; no family has 0 papers; records sum to {len(d)}')
    OUT_FAM.write_text(json.dumps(families, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    e2f.to_csv(OUT_E2F, index=False)
    OUT_NOTES.write_text(json.dumps(fnotes, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    labelled = {frozenset(p) for p in pd.read_csv(LAB / 'family_review_key_v3.csv', dtype=str)[['entity_id_a', 'entity_id_b']].values}
    pack = build_pack(E, key, fid, parts, by_e, N, labelled)
    report(E, families, v3e, v3f, fid, key, len(d), pack)


# ---------------------------------------------------------------- labelling pack
def build_pack(E, key, fid, parts, by_e, N, labelled):
    rnd = random.Random(4)
    used = set(labelled)
    grid = {e for e, nm in zip(E['entity_id'], E['name']) if GRID.search(nm)}

    def take(pool, k):
        out = []
        pool = [p for p in pool if frozenset(p[:2]) not in used]
        rnd.shuffle(pool)
        for p in pool:
            if frozenset(p[:2]) in used:
                continue
            out.append(p)
            used.add(frozenset(p[:2]))
            if len(out) == k:
                break
        assert len(out) == k, f'only {len(out)} of {k} pairs available'
        return out

    def within(kt, exclude=frozenset(), per_family=2):
        fams = defaultdict(list)
        for e in E['entity_id']:
            if key[e][0] == kt and e not in exclude:
                fams[fid[e]].append(e)
        pool = []
        for ids in fams.values():
            pairs = list(combinations(sorted(ids), 2))
            rnd.shuffle(pairs)
            pool += [(a, b, f'{kt}: {key[a][2]}') for a, b in pairs[:per_family]]
        return pool

    suite = take(within('standard_suite'), 20)
    series = take(within('numbered_series'), 15)
    tmpl = take(within('template', exclude=grid), 10)
    ids = E['entity_id'].tolist()
    rand = []
    while len(rand) < 8:
        a, b = rnd.sample(ids, 2)
        if fid[a] != fid[b] and frozenset((a, b)) not in used:
            rand.append((a, b, 'random pair, different families'))
            used.add(frozenset((a, b)))
    by_base = defaultdict(list)
    for e in ids:
        base, q, _ = parts[e]
        if base:
            by_base[base].append(e)
    hard_pool = []
    for base, members in by_base.items():
        for a, b in combinations(members, 2):
            if fid[a] == fid[b]:
                continue
            ca, cb = N.at[a, 'category'], N.at[b, 'category']
            qa, qb = parts[a][1], parts[b][1]
            if ca != cb:
                hard_pool.append((a, b, f'same stem "{base}", different Category'))
            elif qa != qb and qa and qb:
                hard_pool.append((a, b, f'same stem "{base}", different qualifier'))
    hard = take(hard_pool, 7)
    rows = ([('merged_by_standard_suite',) + p for p in suite] + [('merged_by_numbered_series',) + p for p in series] +
            [('merged_by_template_outside_grid',) + p for p in tmpl] + [('negative_random',) + p for p in rand] +
            [('negative_hard',) + p for p in hard])
    rnd.shuffle(rows)
    assert len(rows) == 60 and len({frozenset(r[1:3]) for r in rows}) == 60
    assert not ({frozenset(r[1:3]) for r in rows} & labelled), 'pair already labelled'

    def ctx2(e):
        g = by_e[e][by_e[e]['Problem_Context'].map(lambda v: v.strip() not in MISSING)]
        return g.groupby('Problem_Context')['paper_key'].nunique().sort_values(ascending=False, kind='stable').index[:2].tolist()

    def side(e, s):
        return {f'name_{s}': N.at[e, 'canonical_name'], f'aliases_{s}': ' | '.join(N.at[e, 'aliases'][:5]),
                f'category_{s}': N.at[e, 'category'],
                f'venues_{s}': '; '.join(f'{v} ({c})' for v, c in N.at[e, 'venues'].items() if c),
                f'sample_problem_contexts_{s}': ' | '.join(ctx2(e))}
    blind, keyf = [], []
    for i, (kind, a, b, ev) in enumerate(rows, 1):
        pid = f'Q{i:02d}'
        blind.append({'pair_id': pid, **side(a, 'a'), **side(b, 'b'), 'same_family (y/n/unsure)': '', 'notes': ''})
        keyf.append({'pair_id': pid, 'entity_id_a': a, 'entity_id_b': b, 'pair_type': kind, 'evidence': ev,
                     'family_a': fid[a], 'family_b': fid[b]})
    B, K = pd.DataFrame(blind), pd.DataFrame(keyf)
    text = ' '.join(B.astype(str).agg(' '.join, axis=1))
    assert not any(t in text for t in ('merged_by_', 'negative_', 'suite:', 'series:', 'template:')), 'answer leak'
    B.to_csv(LAB / 'family_review_sample_v4_blind.csv', index=False)
    K.to_csv(LAB / 'family_review_key_v4.csv', index=False)
    instr = (LAB / 'labeling_instructions.md').read_text(encoding='utf-8')
    instr = instr.replace('You will label 80 pairs of benchmark problems in `family_review_sample_v3_blind.csv`.',
                          'You will label 60 pairs of benchmark problems in `family_review_sample_v4_blind.csv`.')
    assert '60 pairs' in instr
    (LAB / 'labeling_instructions_v4.md').write_text(instr, encoding='utf-8')
    return K


def report(E, families, v3e, v3f, fid, key, n_records, pack):
    F = pd.DataFrame(families)
    print(f'\nfamilies: {len(F)} (v3: 2,027); by kind {F.family_kind.value_counts().to_dict()}')
    print(f'entities by key type: {E.key_type.value_counts().to_dict()}')
    multi = F[F.n_papers >= 2]
    print(f'share of records in families with >= 2 papers: {multi.n_records.sum() / n_records:.1%} '
          f'({multi.n_records.sum()} of {n_records}; v3 46.7%)')
    for lo, hi, lab in [(1, 1, '1'), (2, 2, '2'), (3, 5, '3-5'), (6, 10, '6-10'), (11, 10**9, '11+')]:
        s = F[(F.n_papers >= lo) & (F.n_papers <= hi)]
        print(f'  n_papers {lab:5s} {len(s):5d} families, {s.n_records.sum():5d} records ({s.n_records.sum() / n_records:.1%})')
    # former repository collections
    print('\nformer v3 repository collections (library cue is now attribute-only):')
    for f in v3f.values():
        if f['family_kind'] == 'repository_collection':
            now = Counter(key[e][0] for e in f['member_entity_ids'])
            print(f'  {f["family_id"]} {f["family_name"]!r}: {f["n_members"]} entities -> now {dict(now)}')
    # changed family = different set of co-members
    v3fam = dict(zip(v3e.entity_id, v3e.family_id))
    v3sets = v3e.groupby('family_id')['entity_id'].apply(frozenset).to_dict()
    v4sets = E.groupby('family_id')['entity_id'].apply(frozenset).to_dict()
    changed = [e for e in E['entity_id'] if v3sets[v3fam[e]] != v4sets[fid[e]]]
    print(f'\nentities whose family (set of co-members) changed vs v3: {len(changed)} of {len(E)}')
    ex = pd.Series(changed).sample(15, random_state=0)
    for e in ex:
        f3, f4 = v3f[v3fam[e]], next(f for f in families if f['family_id'] == fid[e])
        print(f'  {E.set_index("entity_id").at[e, "name"][:50]!r}: v3 {f3["family_name"][:38]!r} [{f3["family_kind"]}, '
              f'{f3["n_members"]}] -> v4 {f4["family_name"][:38]!r} [{f4["family_kind"]}, {f4["n_members"]}]')
    g = E[E['name'].str.contains(GRID)]
    print(f'\nbug-prediction grid: {len(g)} entities in {g.family_id.nunique()} families (v3: 9); '
          f'sizes {sorted(g.groupby("family_id").size().tolist(), reverse=True)}; key types {g.key_type.value_counts().to_dict()}')
    print('\nlargest families:')
    for f in F.sort_values('n_members', ascending=False).head(8).itertuples():
        print(f'  {f.family_id} {f.family_name[:60]!r} [{f.family_kind}, {f.category}] {f.n_members} entities, {f.n_papers} papers')
    for kind in ('numbered_series', 'template_grid'):
        s = F[F.family_kind == kind]
        print(f'\n{kind}: {len(s)} families, {int(s.n_members.sum())} entities; 8 largest:')
        for f in s.sort_values('n_members', ascending=False).head(8).itertuples():
            print(f'  {f.family_id} {f.family_name[:70]!r} [{f.category}] {f.n_members} entities, {f.n_papers} papers')
    print(f'\nlabelling pack v4: {len(pack)} pairs {pack.pair_type.value_counts().to_dict()}')


if __name__ == '__main__':
    sys.exit(main())
