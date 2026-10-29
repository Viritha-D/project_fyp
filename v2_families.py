"""
v2 family layer, Part 2: group entities into families by rule (family_rules_v2.json).

Rules (all within one Category, applied with union-find): equal name stem, equal library cue
(from the rows' Dataset_Name / Source_Platform), template names (>= 5 tokens, <= 2 token
edits). Embedding similarity never merges; it only lists candidates. Entities, entity ids,
notes, embeddings and paper_index.csv are read, never written.

Outputs: families_v2.json, entity_to_family_v2.csv, family_notes_v2.json,
family_candidates_v2.csv, possible_duplicate_entities_v2.csv, family_review_sample.csv
Usage: python v2_families.py
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

ROOT = Path(__file__).resolve().parent
R = json.loads((ROOT / 'family_rules_v2.json').read_text(encoding='utf-8'))
US = {k: v for k, v in R['spelling_us'].items() if not k.startswith('_')}
S, IID, LC, T = R['stem'], R['instance_ids'], R['library_cue'], R['template']
MISSING = {'', 'Not Reported', 'N/A (Pure Math problem)'}
MISSING_RE = re.compile(r'(?i)^\s*(not reported|n/?a\b.*|unknown|none|)\s*$')
CUSTOM = 'custom simulated data'
VENUES = ['CEC', 'GECCO', 'FOGA', 'PPSN', 'PReMI']

PAREN = re.compile(S['parenthetical_regex'])
TOK = re.compile(S['token_regex'])
YEAR = re.compile(S['year_regex'])
SIZE = re.compile(S['size_token_regex'])
DROP = set(S['drop_words'])
GENERIC = set(S['generic_stems'])
PREFIX_LIB = {p: lib for lib, ps in IID['instance_prefixes'].items() for p in ps
              if len(p) >= IID['min_prefix_letters']}
INST = re.compile(r'^(' + '|'.join(sorted(PREFIX_LIB, key=len, reverse=True)) + r')\d+[a-z]?$')
EXPLICIT = set(IID['explicit_instances'])
CUES = [(c['cue'], re.compile(c['regex'], re.I)) for c in LC['cues']]
STD = [re.compile(p, re.I) for p in R['standard_suite_regex']['patterns']]

OUT_FAM = ROOT / 'families_v2.json'
OUT_E2F = ROOT / 'entity_to_family_v2.csv'
OUT_NOTES = ROOT / 'family_notes_v2.json'
OUT_CAND = ROOT / 'family_candidates_v2.csv'
OUT_DUP = ROOT / 'possible_duplicate_entities_v2.csv'
OUT_REVIEW = ROOT / 'family_review_sample.csv'


def us(text):
    return re.sub(r'[a-z]+', lambda m: US.get(m.group(0), m.group(0)), text.lower())


def unparen(text):
    prev = None
    while prev != text:
        prev, text = text, PAREN.sub(' ', text)
    return text


def stem(name):
    s = unparen(us(name))
    words = re.findall(r'[a-z0-9]+', s)
    libs, keep = [], []
    for w in words:
        if w in EXPLICIT:
            libs.append('tsplib')
            continue
        m = INST.match(w)
        if m:
            libs.append(PREFIX_LIB[m.group(1)].lower())
            continue
        for t in TOK.findall(w):
            if t.isdigit():
                if YEAR.match(t):
                    keep.append(t)
                continue
            if t in DROP or SIZE.match(t):
                continue
            keep.append(t)
    st = ' '.join(keep)
    if not st and libs:
        return f'{libs[0]} instance'
    if len(st.replace(' ', '')) < S['min_stem_chars'] or st in GENERIC or not re.search('[a-z]', st):
        return ''
    return st


def template_tokens(name):
    return re.findall(r'[a-z0-9]+', unparen(us(name)))


def token_edits(a, b, cap):
    """Levenshtein distance on token lists, early exit above cap."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, y in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y))
        if min(cur) > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def char_edits_le1(a, b):
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def cue_of(values):
    found = Counter()
    for v in values:
        for cue, rx in CUES:
            m = rx.search(v)
            if m:
                if '{year}' in cue:
                    y = m.group(1)
                    cue = cue.format(year=y if len(y) == 4 else '20' + y)
                found[cue] += 1
    if not found:
        return ''
    order = {c: i for i, (c, _) in enumerate(CUES)}
    return sorted(found, key=lambda c: (-found[c], order.get(c if not c.startswith('CEC ') else 'CEC {year}', 99)))[0]


class UF:
    def __init__(self, items):
        self.p = {x: x for x in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def top(counter, k):
    return [{'value': v, 'count': int(c)} for v, c in counter.most_common(k)]


def plain_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def main():
    notes = json.loads((ROOT / 'entity_notes_v2.json').read_text(encoding='utf-8'))
    ents = json.loads((ROOT / 'problem_entities_enriched_v2.json').read_text(encoding='utf-8'))
    emb = np.load(ROOT / 'entity_embeddings_v2.npy')
    order = (ROOT / 'entity_ids_order_v2.txt').read_text(encoding='utf-8').splitlines()
    m = pd.read_csv(ROOT / 'paper_to_entity_map_v2.csv', dtype=str, keep_default_na=False)
    d = pd.read_csv(ROOT / 'papers_master_with_matching_text_v2.csv', dtype=str, keep_default_na=False)
    idx = pd.read_csv(ROOT / 'paper_index.csv', dtype=str, keep_default_na=False)
    assert order == [n['entity_id'] for n in notes] == [e['entity_id'] for e in ents] and emb.shape[0] == len(order)
    assert m['paper_id'].tolist() == d['Paper_ID'].tolist()

    N = pd.DataFrame(notes).set_index('entity_id')
    aliases = {e['entity_id']: e['aliases']['benchmark_names'] for e in ents}
    rows = d.assign(entity_id=m['entity_id'].values, paper_key=m['paper_key'].values)
    by_e = {e: g for e, g in rows.groupby('entity_id')}
    eids = order

    # ---------------- per-entity keys ----------------
    E = pd.DataFrame({'entity_id': eids, 'name': [N.at[e, 'canonical_name'] for e in eids],
                      'category': [N.at[e, 'category'] for e in eids],
                      'n_papers': [int(N.at[e, 'n_papers']) for e in eids],
                      'n_records': [int(N.at[e, 'n_records']) for e in eids]})
    E['stem'] = E['name'].map(stem)
    E['cue'] = [cue_of(list(by_e[e]['Dataset_Name']) + list(by_e[e]['Source_Platform'])) for e in eids]
    E['ttok'] = E['name'].map(template_tokens)
    E['std'] = [any(rx.search(x) for rx in STD for x in [N.at[e, 'canonical_name']] + aliases[e]) for e in eids]

    uf = UF(eids)
    linked = defaultdict(set)     # method -> entities joined by it
    edges = defaultdict(list)     # method -> (a, b) pairs, for the review sample

    for method, col in [('stem', 'stem'), ('library_cue', 'cue')]:
        for (cat, key), g in E[E[col] != ''].groupby(['category', col]):
            ids = g['entity_id'].tolist()
            if len(ids) < 2:
                continue
            linked[method].update(ids)
            for a, b in zip(ids, ids[1:]):
                uf.union(a, b)
            edges[method].extend((a, b, key) for a, b in combinations(ids, 2))

    cap = T['max_token_edits']
    for cat, g in E.groupby('category'):
        cand = [(r.entity_id, r.ttok, set(r.ttok)) for r in g.itertuples() if len(r.ttok) >= T['min_tokens']]
        for (a, ta, sa), (b, tb, sb) in combinations(cand, 2):
            if abs(len(ta) - len(tb)) > cap or len(sa & sb) < max(len(ta), len(tb)) - cap:
                continue
            if ta != tb and token_edits(ta, tb, cap) <= cap:
                uf.union(a, b)
                linked['template'].update((a, b))
                edges['template'].append((a, b, f'{token_edits(ta, tb, cap)} token edit(s)'))

    # ---------------- families ----------------
    root = {e: uf.find(e) for e in eids}
    groups = defaultdict(list)
    for e in eids:
        groups[root[e]].append(e)
    fam_order = sorted(groups.values(), key=lambda ids: min(ids))
    fid = {}
    for i, ids in enumerate(fam_order, 1):
        for e in ids:
            fid[e] = f'F{i:05d}'
    E['family_id'] = E['entity_id'].map(fid)
    methods_of = {e: [k for k in ('stem', 'library_cue', 'template') if e in linked[k]] for e in eids}

    flags = dict(zip(idx['paper_key'], idx['flags']))
    rows['family_id'] = rows['entity_id'].map(fid)
    real = lambda s: [v for v in s if v.strip() and v.strip() not in MISSING]
    families, fnotes = [], []
    for ids in fam_order:
        f = fid[ids[0]]
        g = rows[rows['family_id'] == f]
        mem = E[E['entity_id'].isin(ids)].sort_values(['n_papers', 'n_records', 'entity_id'], ascending=[False, False, True])
        name = mem.iloc[0]['name']
        cats = sorted(set(mem['category']))
        n_pap = int(g['paper_key'].nunique())
        venues = {v: int((g.drop_duplicates('paper_key')['Conference'] == v).sum()) for v in VENUES}
        cues = sorted(set(mem['cue']) - {''})
        ds = [v.strip() for v in g['Dataset_Name']]
        has_real_ds = any(v and not MISSING_RE.match(v) and v.lower() != CUSTOM for v in ds)
        signals = []
        if cues:
            signals.append('library_cue')
        if n_pap >= 2:
            signals.append('n_papers>=2')
        if sum(1 for c in venues.values() if c) >= 2:
            signals.append('multiple_venues')
        if mem['std'].any():
            signals.append('standard_suite_name')
        if not has_real_ds and any(v.lower() == CUSTOM for v in ds):
            signals.append('custom_data_only')
        if n_pap == 1:
            signals.append('single_paper')
        fam = {'family_id': f, 'family_name': name, 'category': cats[0] if len(cats) == 1 else 'mixed',
               'member_entity_ids': mem['entity_id'].tolist(), 'n_members': len(ids), 'n_papers': n_pap,
               'n_records': int(len(g)), 'venues': venues, 'library_cues': cues,
               'merge_methods': sorted({x for e in ids for x in methods_of[e]}), 'reuse_signals': signals}
        families.append(fam)

        # family note: same fields as the entity notes, computed over all member rows
        yrs = g[(g['Conference'] != 'PReMI') & ~g['paper_key'].map(lambda k: 'year_unverified' in flags[k])]['Year']
        yrs = sorted(int(y) for y in yrs if y.isdigit())
        tags = Counter(t.strip() for v in g['Landscape_Characteristics'] for t in v.split(';')
                       if t.strip() and t.strip() not in MISSING)
        algs = g[g['Algorithm_Name'].map(lambda v: v not in MISSING)].groupby('Algorithm_Name')['paper_key'].nunique()
        alias_papers = g.groupby('Benchmark_Name')['paper_key'].nunique().sort_values(ascending=False, kind='stable')
        n = {'family_id': f, 'family_name': name, 'category': fam['category'],
             'aliases': alias_papers.index[:8].tolist(), 'n_papers': n_pap, 'n_records': int(len(g)),
             'venues': venues, 'year_range': [yrs[0], yrs[-1]] if yrs else None,
             'typical_dimensions': top(Counter(real(g['Dimensionality'])), 3),
             'landscape': {'Modality': top(Counter(real(g['Modality'])), 3),
                           'Separability': top(Counter(real(g['Separability'])), 3),
                           'Landscape_Characteristics': top(tags, 5)},
             'metrics': top(Counter(real(g['Performance_Metric'])), 3),
             'commonly_compared_algorithms': [{'value': a, 'n_papers': int(c)} for a, c in
                                              algs.sort_values(ascending=False, kind='stable').head(5).items()],
             'industries': top(Counter(real(g['Industry'])), 3) if (g['Category'] == 'Applied').any() else []}
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
        n['members'] = [{'entity_id': r.entity_id, 'name': r.name, 'n_papers': int(r.n_papers)} for r in mem.head(10).itertuples()]
        n['reuse_signals'] = signals
        n['note_text'], k = family_note_text(n, len(ids))
        assert 2 <= k <= 4
        fnotes.append(n)

    # ---------------- assertions ----------------
    e2f = E[['entity_id', 'family_id', 'name', 'category', 'n_papers', 'n_records', 'stem', 'cue']].copy()
    e2f['linked_by'] = e2f['entity_id'].map(lambda e: ';'.join(methods_of[e]))
    e2f = e2f.rename(columns={'name': 'canonical_name', 'cue': 'library_cue'})
    assert e2f['entity_id'].is_unique and len(e2f) == len(eids) and e2f['family_id'].notna().all(), 'entity not in exactly one family'
    root_to_key = {r: k for k, rs in zip(idx['paper_key'], idx['paper_id_roots']) for r in rs.split(';')}
    pk_idx = d['Paper_ID'].str.replace(r'_Ext_\d+$', '', regex=True).map(root_to_key)
    fam_pk = pd.Series(pk_idx.values).groupby(rows['family_id'].values).nunique()
    assert all(fam_pk[f['family_id']] == f['n_papers'] for f in families), 'family n_papers != paper_index count'
    assert all(f['n_papers'] > 0 for f in families), 'family with 0 papers'
    assert sum(f['n_records'] for f in families) == len(d)
    print(f'assertions passed: {len(eids)} entities each in exactly one of {len(families)} families; family n_papers '
          f'equals the paper_index count of its members\' rows; no family has 0 papers; records sum to {len(d)}')

    (OUT_FAM).write_text(json.dumps(families, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    e2f.to_csv(OUT_E2F, index=False)
    (OUT_NOTES).write_text(json.dumps(fnotes, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    # ---------------- embedding candidates (review only) ----------------
    th = R['embedding_candidates']['threshold']
    pos = {e: i for i, e in enumerate(order)}
    cand = []
    for cat, g in E.groupby('category'):
        ids = g['entity_id'].tolist()
        v = emb[[pos[e] for e in ids]]
        sims = v @ v.T
        ii, jj = np.where(np.triu(sims, 1) >= th)
        for i, j in zip(ii, jj):
            a, b = ids[i], ids[j]
            if fid[a] != fid[b]:
                cand.append(dict(similarity=round(float(sims[i, j]), 4), category=cat, entity_id_a=a,
                                 name_a=N.at[a, 'canonical_name'], family_a=fid[a], entity_id_b=b,
                                 name_b=N.at[b, 'canonical_name'], family_b=fid[b]))
    C = pd.DataFrame(cand).sort_values('similarity', ascending=False)
    C.to_csv(OUT_CAND, index=False)

    # ---------------- possible duplicate entities (report only) ----------------
    normed = {e: ' '.join(re.findall(r'[a-z0-9]+', us(N.at[e, 'canonical_name']))) for e in eids}
    dup = {}
    byset = defaultdict(list)
    for e in eids:
        byset[frozenset(normed[e].split())].append(e)
    for ids in byset.values():
        for a, b in combinations(ids, 2):
            dup[(a, b)] = 'same token set'
    neigh = defaultdict(set)
    for e in eids:
        s = normed[e]
        neigh[s].add(e)
        for i in range(len(s)):
            neigh[s[:i] + s[i + 1:]].add(e)
    for ids in neigh.values():
        for a, b in combinations(sorted(ids), 2):
            if (a, b) not in dup and char_edits_le1(normed[a], normed[b]):
                dup[(a, b)] = 'edit distance <= 1'
    D = pd.DataFrame([dict(entity_id_a=a, name_a=N.at[a, 'canonical_name'], category_a=N.at[a, 'category'],
                           entity_id_b=b, name_b=N.at[b, 'canonical_name'], category_b=N.at[b, 'category'],
                           same_category=N.at[a, 'category'] == N.at[b, 'category'], reason=r,
                           same_family=fid[a] == fid[b],
                           differs_only_in_digits=re.sub(r'\d+', '#', normed[a]) == re.sub(r'\d+', '#', normed[b]))
                      for (a, b), r in sorted(dup.items())])
    D.to_csv(OUT_DUP, index=False)

    # ---------------- review sample (80 pairs) ----------------
    rnd = random.Random(0)
    def row(kind, a, b, evidence):
        return {'entity_id_a': a, 'name_a': N.at[a, 'canonical_name'], 'category_a': N.at[a, 'category'],
                'n_papers_a': int(N.at[a, 'n_papers']), 'entity_id_b': b, 'name_b': N.at[b, 'canonical_name'],
                'category_b': N.at[b, 'category'], 'n_papers_b': int(N.at[b, 'n_papers']),
                'same_family (y/n)': '', 'notes': '', 'pair_type': kind, 'evidence': evidence,
                'family_a': fid[a], 'family_b': fid[b]}
    sample = []
    for method in ('stem', 'library_cue', 'template'):
        pool = edges[method]
        by_key = defaultdict(list)
        for a, b, k in pool:
            by_key[k if method != 'template' else (fid[a])].append((a, b, k))
        keys = rnd.sample(sorted(by_key, key=str), min(10, len(by_key)))
        picks = [rnd.choice(by_key[k]) for k in keys]
        while len(picks) < 10 and len(picks) < len(pool):
            p = rnd.choice(pool)
            if p not in picks:
                picks.append(p)
        sample += [row(f'merged_by_{method}', a, b, f'{method}: {k}') for a, b, k in picks]
    for _, r in C.sample(min(30, len(C)), random_state=0).iterrows():
        sample.append(row('candidate_not_merged', r.entity_id_a, r.entity_id_b, f'cosine {r.similarity:.3f}'))
    negs = set()
    while len(negs) < 20:
        a, b = rnd.sample(eids, 2)
        if fid[a] != fid[b]:
            negs.add(tuple(sorted((a, b))))
    sample += [row('negative_control', a, b, 'random pair, different families') for a, b in sorted(negs)]
    rnd.shuffle(sample)
    pd.DataFrame(sample).to_csv(OUT_REVIEW, index=False)

    report(E, families, fnotes, linked, C, D, sample, len(d))


def family_note_text(n, n_members):
    venues = [f"{v} ({c})" for v, c in n['venues'].items() if c]
    s1 = (f"The {n['family_name']} family groups {n_members} entit{'ies' if n_members != 1 else 'y'} "
          f"({n['category']}), used in {n['n_papers']} paper{'s' if n['n_papers'] != 1 else ''} "
          f"({n['n_records']} records) at {plain_list(venues)}")
    if n['year_range']:
        y0, y1 = n['year_range']
        s1 += f", {y0}" if y0 == y1 else f", {y0}-{y1}"
    sentences = [s1 + '.']
    bits = []
    if n['typical_dimensions']:
        bits.append('typical dimensions ' + '; '.join(f"{x['value']} ({x['count']})" for x in n['typical_dimensions']))
    land = [x['value'] for f in ('Modality', 'Separability') for x in n['landscape'][f][:1]]
    land += [x['value'] for x in n['landscape']['Landscape_Characteristics'][:3]]
    if land:
        bits.append('reported landscape: ' + ', '.join(land))
    if bits:
        t = ', '.join(bits)
        sentences.append(t[0].upper() + t[1:] + '.')
    perf = []
    if n['metrics']:
        perf.append('results are reported as ' + '; '.join(x['value'] for x in n['metrics']))
    if n['commonly_compared_algorithms']:
        perf.append('commonly compared algorithms: ' + ', '.join(x['value'] for x in n['commonly_compared_algorithms']))
    if perf:
        t = '; '.join(perf)
        sentences.append(t[0].upper() + t[1:] + '.')
    cav = {'ppsn_partial': 'some records come from PPSN files whose paper titles are not per-paper',
           'premi_year_unverified': 'some PReMI years could not be verified',
           'single_paper': 'it is supported by a single paper',
           'sparse_metadata': 'most landscape and dimension fields are not reported'}
    if n['evidence_caveats']:
        sentences.append('Caveats: ' + '; '.join(cav[c] for c in n['evidence_caveats']) + '.')
    if len(sentences) == 1:
        sentences.append('No dimension, landscape or metric details were reported.')
    return ' '.join(sentences), len(sentences)


def report(E, families, fnotes, linked, C, D, sample, n_records):
    F = pd.DataFrame(families)
    print(f'\nfamilies: {len(F)} (from {len(E)} entities); singletons {int((F.n_members == 1).sum())}; '
          f'multi-member families {int((F.n_members > 1).sum())} holding {int(F[F.n_members > 1].n_members.sum())} entities')
    print('entities grouped (in a group of >= 2) by each rule (an entity can be linked by more than one):')
    for k in ('stem', 'library_cue', 'template'):
        only = linked[k] - set().union(*[linked[j] for j in ('stem', 'library_cue', 'template') if j != k])
        print(f'  {k:12s} {len(linked[k]):5d} entities ({len(only)} by this rule only)')
    print(f'  any rule     {len(set().union(*linked.values())):5d} entities')
    print('families by n_papers:')
    for lo, hi, lab in [(1, 1, '1'), (2, 2, '2'), (3, 5, '3-5'), (6, 10, '6-10'), (11, 10**9, '11+')]:
        s = F[(F.n_papers >= lo) & (F.n_papers <= hi)]
        print(f'  {lab:5s} {len(s):5d} families ({len(s) / len(F):.1%}), {s.n_records.sum():5d} records '
              f'({s.n_records.sum() / n_records:.1%})')
    multi = F[F.n_papers >= 2]
    print(f'share of records in families with >= 2 papers: {multi.n_records.sum() / n_records:.1%} '
          f'({multi.n_records.sum()} of {n_records}; entity-level baseline 26.3%)')
    print('reuse_signals combinations (families, records):')
    combo = F.assign(sig=F.reuse_signals.map(lambda s: ' + '.join(s) if s else '(none)')).groupby('sig').agg(
        families=('family_id', 'size'), records=('n_records', 'sum')).sort_values('records', ascending=False)
    for sig, r in combo.iterrows():
        print(f'  {r.families:5d} families {r.records:5d} records  {sig}')
    print(f'library cues: {Counter(c for f in families for c in f["library_cues"]).most_common()}')
    print(f'\nembedding candidates (different families, same Category, cosine >= threshold): {len(C)} pairs')
    print(f'possible duplicate entities: {len(D)} pairs ({D.reason.value_counts().to_dict()}); '
          f'same Category {int(D.same_category.sum())}; already in one family {int(D.same_family.sum())}; '
          f'differ only in digits (numbered variants) {int(D.differs_only_in_digits.sum())}')
    print(f'review sample: {len(sample)} pairs {Counter(s["pair_type"] for s in sample)}')
    print('\nTOP 25 families by n_papers (members, top 6 by papers):')
    for f in F.sort_values(['n_papers', 'n_records'], ascending=False).head(25).itertuples():
        mem = next(n['members'] for n in fnotes if n['family_id'] == f.family_id)
        print(f'  {f.family_id} {f.n_papers:4d} papers {f.n_records:5d} rec {f.n_members:4d} ent [{f.category}] '
              f'{f.family_name[:50]!r} via {f.merge_methods} cues={f.library_cues}')
        print('        ' + '; '.join(f"{x['name'][:40]} ({x['n_papers']})" for x in mem[:6]))
    print('\n15 random families (seed 1) with members:')
    for f in F.sample(15, random_state=1).itertuples():
        mem = next(n['members'] for n in fnotes if n['family_id'] == f.family_id)
        print(f'  {f.family_id} [{f.category}] {f.n_papers} papers, {f.n_members} entities: '
              + '; '.join(f"{x['name'][:45]} ({x['n_papers']})" for x in mem[:6]))
    print('\n10 family notes:')
    NN = pd.DataFrame(fnotes).merge(F[['family_id', 'n_members']], on='family_id')
    rng = np.random.default_rng(0)
    pick = lambda fr, k: fr.iloc[sorted(rng.choice(len(fr), size=min(k, len(fr)), replace=False))]
    has = lambda v: NN.venues.map(lambda x: x[v] > 0)
    big = NN[NN.n_members > 1]
    for lab, fr in [('Pure Math, multi-member', pick(big[big.category == 'Pure Math'], 3)),
                    ('Applied, multi-member', pick(big[big.category == 'Applied'], 3)),
                    ('with PReMI', pick(NN[has('PReMI') & (NN.n_members > 1)], 1)),
                    ('with FOGA', pick(NN[has('FOGA') & (NN.n_members > 1)], 1)),
                    ('with PPSN', pick(NN[has('PPSN')], 1)), ('singleton', pick(NN[NN.n_members == 1], 1))]:
        for _, r in fr.iterrows():
            print(f'  [{lab}] {r.family_id}: {r.note_text}')


if __name__ == '__main__':
    sys.exit(main())
