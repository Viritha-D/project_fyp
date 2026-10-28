"""
Part 4 - entity resolution by name-key blocking, reconstructed from part4_methodology.md.
Every word list and regex lives in part4_rules.json.

Steps: name_key (filler words) -> CEC year key -> (Category, name_key) blocking -> acronym
merge -> text-hash dedupe (count only) -> suite/child split with the range-exclusion fix
(+ optional --series-split) -> digit-guard report.

Usage:
  python part4_entities.py --fidelity
      run on the old master (backup_v1/master_before_ingest.csv, 4,256 rows) with the
      original rules and compare with part4_answer_key_map.csv. Gates: name_key equal on
      >= 99% of rows and ARI >= 0.99; exits non-zero if either fails.
  python part4_entities.py --v2 [--no-series-split]
      run on papers_master_with_matching_text_v2.csv (series split on by default) and write
      paper_to_entity_map_v2.csv and digit_merge_report.csv.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RULES = json.loads((ROOT / 'part4_rules.json').read_text(encoding='utf-8'))
OLD_MASTER = ROOT / 'backup_v1' / 'master_before_ingest.csv'
ANSWER_KEY = ROOT / 'part4_answer_key_map.csv'
V2_MASTER = ROOT / 'papers_master_with_matching_text_v2.csv'
V2_MAP = ROOT / 'paper_to_entity_map_v2.csv'
DIGIT_REPORT = ROOT / 'digit_merge_report.csv'
DIGIT_REPORT_FIDELITY = ROOT / 'digit_merge_report_fidelity_old_master.csv'
MAP_COLS = ['paper_id', 'Category', 'Paper_Title', 'Benchmark_Name', 'name_key', 'entity_id',
            'resolution_method', 'parent_benchmark_id', 'entity_type', 'series_key']

R1, R2, R3, R4, R6, R7 = (RULES['1_name_key'], RULES['2_cec_year_key'], RULES['3_blocking'],
                          RULES['4_acronym_merge'], RULES['6_suite_child_split'], RULES['7_digit_guard'])
TOKEN = re.compile(R1['token_regex'])
FILLER = set(R1['filler_words'])
CEC = re.compile(R2['regex'], re.I)
NEVER_KEY = set(R3['never_a_key'])
ACRONYM = re.compile(R4['trailing_acronym_regex'])
INITIAL_WORD = re.compile(R4['initials_word_regex'])
RANGE = re.compile(R6['range_regex'], re.I)
FNUM = re.compile(R6['function_number_regex'], re.I)
GNUM = re.compile(R6['series_split_function_number_regex'], re.I)
TCONF = re.compile(R6['transformation_config_regex'], re.I)
SERIES = re.compile(R6['series_split_series']['series_regex'], re.I)
IDENT = re.compile(R7['identifier_regex'], re.I)
IGNORE = [re.compile(p, re.I) for p in R7['ignore_before_matching']]


def plain_key(name):
    return ''.join(w for w in TOKEN.findall(str(name).lower()) if w not in FILLER)


def name_key(name):
    m = CEC.search(str(name))
    if m:
        return R2['key_template'].format(year=m.group(1) or m.group(2))
    return plain_key(name)


def acronym_base(name):
    """Name without its trailing '(ACRONYM)' when the acronym is the initials of the words before it."""
    m = ACRONYM.match(str(name))
    if not m:
        return None
    words = INITIAL_WORD.findall(m.group(1))
    if len(words) < 2 or ''.join(w[0] for w in words).lower() != m.group(2).lower():
        return None
    return m.group(1)


def child_key(name, series_split):
    """('single_function', 'F7') / ('named_subset', ...) / None (suite-level) for a name in a cec group."""
    s = str(name)
    if RANGE.search(s):
        return None                                   # range description -> suite level
    t = TCONF.search(s)
    if t:
        return ('named_subset', f'config{t.group(2)}')
    nums = list(dict.fromkeys(int(n) for n in FNUM.findall(s)))
    prefix = 'F'
    if not nums and series_split:
        nums = list(dict.fromkeys(int(n) for n in GNUM.findall(s)))
        prefix = 'G'
    if len(nums) == 1:
        return ('single_function', f'{prefix}{nums[0]}')
    if len(nums) > 1:
        return ('named_subset', f'{prefix}' + ','.join(map(str, sorted(nums))))
    return None


def build(df, id_col, series_split, id_style='original'):
    """df: master rows (Paper_ID / paper_id, Category, Paper_Title, Benchmark_Name)."""
    n = len(df)
    out = pd.DataFrame({'paper_id': df[id_col].values, 'Category': df['Category'].values,
                        'Paper_Title': df['Paper_Title'].values, 'Benchmark_Name': df['Benchmark_Name'].values})
    root = out['paper_id'].str.replace(r'_Ext_\d+$', '', regex=True)
    unkeyed = out['Benchmark_Name'].str.strip().str.lower().isin(NEVER_KEY)
    out['name_key'] = out['Benchmark_Name'].map(name_key)
    out.loc[unkeyed, 'name_key'] = 'unkeyed:' + root[unkeyed]
    out['resolution_method'] = 'name_key'
    out.loc[unkeyed, 'resolution_method'] = 'no_benchmark_name'

    # ---- blocking: (Category, name_key) -> base entity, ids by first appearance ----
    block = list(zip(out['Category'], out['name_key']))
    base_id = {}
    for b in block:
        base_id.setdefault(b, len(base_id))
    eid = pd.Series([base_id[b] for b in block])
    n_base = len(base_id)

    # ---- acronym merge ----
    rows_per = Counter(eid)
    key_to_id = {b: i for b, i in base_id.items()}
    merged_away = {}
    for (cat, nk), i in list(base_id.items()):
        if nk.startswith(('cec_', 'unkeyed:')):
            continue
        names = out.loc[eid == i, 'Benchmark_Name'].unique()
        for nm in names:
            base = acronym_base(nm)
            if base is None:
                continue
            j = key_to_id.get((cat, name_key(base)))
            if j is None or j == i:
                continue
            a, b = (i, j)
            keep, drop = (a, b) if (rows_per[a], -a) > (rows_per[b], -b) else (b, a)
            merged_away[drop] = keep
    for drop, keep in merged_away.items():
        mask = eid == drop
        out.loc[mask, 'resolution_method'] = 'name_key+acronym_merge'
        eid[mask] = keep

    # ---- text-hash dedupe (count only) ----
    n_unique_text = None
    if 'matching_text' in df.columns:
        n_unique_text = df['matching_text'].map(lambda t: hashlib.sha256(str(t).encode('utf-8')).hexdigest()).nunique()

    # ---- suite / child split ----
    out['parent_benchmark_id'] = pd.Series([''] * n, dtype=object)   # holds int ids until formatted
    out['entity_type'] = 'single_function'
    out['series_key'] = ''
    next_id = n_base
    cec_groups = [(i, (eid == i).sum()) for (cat, nk), i in base_id.items()
                  if nk.startswith('cec_') and i not in merged_away]
    cec_groups.sort(key=lambda x: (-x[1], x[0]))
    n_split_groups = 0
    for i, _ in cec_groups:
        idx = out.index[eid == i]
        keys = {r: child_key(out.at[r, 'Benchmark_Name'], series_split) for r in idx}
        if not any(keys.values()):
            continue
        n_split_groups += 1
        has_suite_rows = any(v is None for v in keys.values())
        child_ids = {}
        for r in idx:                                   # first appearance order
            k = keys[r]
            if k is None:
                continue
            if k not in child_ids:
                child_ids[k] = next_id
                next_id += 1
            eid[r] = child_ids[k]
            out.at[r, 'entity_type'] = k[0]
            out.at[r, 'parent_benchmark_id'] = i if has_suite_rows else ''
            out.at[r, 'series_key'] = out.at[r, 'name_key'] if not has_suite_rows else ''
        if has_suite_rows:
            out.loc[eid == i, 'entity_type'] = 'suite'

    # ---- series tagging (MSTSP / RWMOP), no regrouping ----
    n_series_tagged = 0
    if series_split:
        for r, nm in out['Benchmark_Name'].items():
            m = SERIES.match(str(nm).strip())
            if m:
                out.at[r, 'series_key'] = f'{out.at[r, "Category"]}|{m.group(1).upper()}'
        n_series_tagged = out.loc[out['series_key'].str.contains(r'\|'), 'name_key'].nunique()

    # ---- ids ----
    if id_style == 'original':
        fmt = lambda x: f'E{int(x):05d}'
        out['entity_id'] = eid.map(fmt)
        out['parent_benchmark_id'] = out['parent_benchmark_id'].map(lambda x: fmt(x) if x != '' else '')
    else:                                               # fresh E00001.. in order of first appearance
        order = {}
        for x in eid:
            order.setdefault(x, len(order) + 1)
        fmt = lambda x: f'E{order[int(x)]:05d}'
        out['entity_id'] = eid.map(fmt)
        out['parent_benchmark_id'] = out['parent_benchmark_id'].map(lambda x: fmt(x) if x != '' else '')
    stats = dict(rows=n, base_entities=n_base, acronym_merges=len(merged_away), split_groups=n_split_groups,
                 entities=out['entity_id'].nunique(), unique_matching_texts=n_unique_text,
                 unkeyed_rows=int(unkeyed.sum()), series_tagged_entities=n_series_tagged)
    return out[MAP_COLS], stats


def digit_guard(m):
    """Pairs of distinct single-function names merged into one entity (report only)."""
    rows = []
    for e, g in m.groupby('entity_id', sort=False):
        idents = {}
        for nm in g['Benchmark_Name'].unique():
            if RANGE.search(nm):
                continue
            s = nm
            for p in IGNORE:
                s = p.sub(' ', s)
            ids = IDENT.findall(s)
            if len(ids) == 1:
                idents[nm] = (ids[0][0].lower(), int(ids[0][1]))
        names = list(idents)
        for x in range(len(names)):
            for y in range(x + 1, len(names)):
                (pa, na), (pb, nb) = idents[names[x]], idents[names[y]]
                if pa == pb and na != nb:
                    rows.append(dict(entity_id=e, entity_type=g['entity_type'].iloc[0], category=g['Category'].iloc[0],
                                     name_key=g['name_key'].iloc[0], name_a=names[x], name_b=names[y],
                                     rows_a=int((g['Benchmark_Name'] == names[x]).sum()),
                                     rows_b=int((g['Benchmark_Name'] == names[y]).sum()),
                                     rule=g.loc[g['Benchmark_Name'] == names[x], 'resolution_method'].iloc[0]))
    return pd.DataFrame(rows, columns=['entity_id', 'entity_type', 'category', 'name_key', 'name_a', 'name_b',
                                       'rows_a', 'rows_b', 'rule'])


def ari_nmi(a, b):
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    return adjusted_rand_score(a, b), normalized_mutual_info_score(a, b)


def fidelity():
    old = pd.read_csv(OLD_MASTER, dtype=str, keep_default_na=False)
    key = pd.read_csv(ANSWER_KEY, dtype=str, keep_default_na=False)
    assert old['paper_id'].tolist() == key['paper_id'].tolist(), 'old master and answer key are not row-aligned'
    m, st = build(old, 'paper_id', series_split=False, id_style='original')
    print(f'[fidelity] old master: {st}')
    nk_eq = (m['name_key'] == key['name_key']).mean()
    ari, nmi = ari_nmi(key['entity_id'], m['entity_id'])
    id_eq = (m['entity_id'] == key['entity_id']).mean()
    other = {c: (m[c] == key[c]).mean() for c in ['resolution_method', 'parent_benchmark_id', 'entity_type']}
    print(f'[fidelity] name_key equal: {nk_eq:.4%} ({int((m["name_key"] == key["name_key"]).sum())}/{len(m)})')
    print(f'[fidelity] grouping vs answer key: ARI {ari:.6f}, NMI {nmi:.6f}; entities {m["entity_id"].nunique()} '
          f'vs {key["entity_id"].nunique()}')
    print(f'[fidelity] identical entity_id: {id_eq:.4%}; ' + '; '.join(f'{c} equal {v:.4%}' for c, v in other.items()))
    g = digit_guard(m)
    g.to_csv(DIGIT_REPORT_FIDELITY, index=False)
    print(f'[fidelity] digit guard on the old master (original rules, report only): {len(g)} pairs in '
          f'{g["entity_id"].nunique() if len(g) else 0} entities -> {DIGIT_REPORT_FIDELITY.name}')
    ok = nk_eq >= 0.99 and ari >= 0.99
    if not ok:
        diff = m[(m['name_key'] != key['name_key']) | (m['entity_id'] != key['entity_id'])]
        print(f'[fidelity] FAILED; {len(diff)} differing rows:')
        print(diff.assign(key_name_key=key['name_key'], key_entity=key['entity_id']).head(50).to_string())
    print(f'[fidelity] gate (name_key >= 99% and ARI >= 0.99): {"PASSED" if ok else "FAILED"}')
    return ok, m


def run_v2(series_split):
    d = pd.read_csv(V2_MASTER, dtype=str, keep_default_na=False)
    m, st = build(d, 'Paper_ID', series_split=series_split, id_style='fresh')
    m.insert(1, 'Conference', d['Conference'].values)
    return m, st, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fidelity', action='store_true')
    ap.add_argument('--v2', action='store_true')
    ap.add_argument('--no-series-split', action='store_true')
    args = ap.parse_args()
    if args.fidelity:
        ok, _ = fidelity()
        return 0 if ok else 1
    if args.v2:
        m, st, _ = run_v2(not args.no_series_split)
        print(st)
        return 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
