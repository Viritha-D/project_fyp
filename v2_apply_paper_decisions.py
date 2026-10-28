"""
Apply the reviewer's paper-identity decisions to paper_index.csv (the masters are never touched).

Run after v2_step1_validate.py, which regenerates paper_index.csv from scratch.

1. Every premi2023_review.csv row whose classification is "same paper, title variants"
   (the 6 proposed merges, approved by the reviewer) gets my_decision = "merge", and the
   merge is applied in paper_index.csv: the absorbed paper_key's row is folded into the
   target row (Source_Files, n_rows, paper_id_roots combined; absorbed keys listed in
   merged_keys; flag "merged").
2. year_unverified: titled PReMI 2023 papers whose title is not in the PReMI 2023
   proceedings (premi2023_proceedings_check.csv match == none). No Year value is changed.
3. ppsn_partial: every PPSN paper (each PPSN file counts as one paper).

A row of the master maps to its paper through its Paper_ID root, listed in paper_id_roots.
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / 'paper_index.csv'
REVIEW = ROOT / 'premi2023_review.csv'
CHECK = ROOT / 'premi2023_proceedings_check.csv'
MASTER = ROOT / 'papers_master_v2.csv'
MERGE_CLASS = 'same paper, title variants'
EXPECTED_MERGES = 6


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def add_flag(flags, flag):
    parts = [f for f in flags.split(';') if f]
    return ';'.join(parts + [flag]) if flag not in parts else flags


def merge_pairs(review):
    """(absorbed paper_key, target paper_key, review row index) for every approved merge."""
    out = []
    for i, r in review[review['classification'] == MERGE_CLASS].iterrows():
        titles = r['titles'].split(' || ')
        m = re.search(r'merge into (\S+\|\d{4}\|\S+)', r['proposed_action'])
        if r['scope'] == 'other_year_in_2023_proceedings':
            year = re.search(r'labelled PReMI (\d{4})', r['notes']).group(1)
            out.append((f'PReMI|{year}|{norm(titles[0])}', m.group(1), i))
        elif r['scope'] == 'same_2023_proceedings_paper':
            target = m.group(1)
            for t in titles:
                key = f'PReMI|2023|{norm(t)}'
                if key != target:
                    out.append((key, target, i))
        elif r['scope'] == 'cross_file_title_pair':   # "merge <b roots> into <a roots>": a is the first title
            out.append((f'PReMI|2023|{norm(titles[1])}', f'PReMI|2023|{norm(titles[0])}', i))
        else:
            raise SystemExit(f'unexpected scope for a merge: {r["scope"]}')
    return out


def main():
    idx = pd.read_csv(INDEX, dtype=str, keep_default_na=False)
    if 'merged_keys' in idx.columns:
        raise SystemExit('paper_index.csv already has the decisions applied; re-run v2_step1_validate.py first')
    review = pd.read_csv(REVIEW, dtype=str, keep_default_na=False)
    n_before = len(idx)

    pairs = merge_pairs(review)
    assert len(pairs) == EXPECTED_MERGES, f'expected {EXPECTED_MERGES} merges, found {len(pairs)}'
    keys = set(idx['paper_key'])
    for a, t, _ in pairs:
        assert a in keys and t in keys and a != t, f'merge keys not in paper_index: {a} -> {t}'
    assert len({a for a, _, _ in pairs}) == len(pairs), 'a paper is absorbed twice'
    assert not ({a for a, _, _ in pairs} & {t for _, t, _ in pairs}), 'a merge target is itself absorbed'

    review.loc[sorted({i for _, _, i in pairs}), 'my_decision'] = 'merge'
    review.to_csv(REVIEW, index=False)

    idx['merged_keys'] = ''
    pos = {k: i for i, k in idx['paper_key'].items()}
    for a, t, _ in pairs:
        ra, rt = idx.loc[pos[a]], idx.loc[pos[t]]
        files = list(dict.fromkeys(rt['Source_Files'].split(';') + ra['Source_Files'].split(';')))
        roots = list(dict.fromkeys(rt['paper_id_roots'].split(';') + ra['paper_id_roots'].split(';')))
        idx.loc[pos[t], 'Source_Files'] = ';'.join(files)
        idx.loc[pos[t], 'n_source_files'] = str(len(files))
        idx.loc[pos[t], 'paper_id_roots'] = ';'.join(roots)
        idx.loc[pos[t], 'n_rows'] = str(int(rt['n_rows']) + int(ra['n_rows']))
        idx.loc[pos[t], 'merged_keys'] = ';'.join(filter(None, [rt['merged_keys'], a]))
        idx.loc[pos[t], 'flags'] = add_flag(idx.loc[pos[t], 'flags'], 'merged')
        for fl in filter(None, ra['flags'].split(';')):   # keep the absorbed paper's flags
            idx.loc[pos[t], 'flags'] = add_flag(idx.loc[pos[t], 'flags'], fl)
    idx = idx.drop(index=[pos[a] for a, _, _ in pairs]).reset_index(drop=True)

    chk = pd.read_csv(CHECK, dtype=str, keep_default_na=False)
    unverified = set(chk[(chk['Year'] == '2023') & (chk['match'] == 'none')]['paper_key'])
    n_unverified_titles = len(unverified)
    absorbed_unverified = {a for a, _, _ in pairs} & unverified
    targets = {a: t for a, t, _ in pairs}
    unverified = {targets.get(k, k) for k in unverified}
    mask = idx['paper_key'].isin(unverified)
    idx.loc[mask, 'flags'] = idx.loc[mask, 'flags'].map(lambda f: add_flag(f, 'year_unverified'))

    ppsn = idx['Conference'] == 'PPSN'
    idx.loc[ppsn, 'flags'] = idx.loc[ppsn, 'flags'].map(lambda f: add_flag(f, 'ppsn_partial'))

    # ---------------- assertions ----------------
    assert len(idx) == n_before - EXPECTED_MERGES, (n_before, len(idx))
    assert idx['paper_key'].is_unique
    d = pd.read_csv(MASTER, dtype=str, keep_default_na=False)
    roots = d['Paper_ID'].str.replace(r'_Ext_\d+$', '', regex=True)
    root_to_key = {r: k for k, rs in zip(idx['paper_key'], idx['paper_id_roots']) for r in rs.split(';')}
    assert len(root_to_key) == sum(len(rs.split(';')) for rs in idx['paper_id_roots']), 'a Paper_ID root is in two papers'
    assert roots.map(root_to_key).notna().all(), 'a master row maps to no paper'
    assert int(idx['n_rows'].astype(int).sum()) == len(d), 'n_rows does not add up to the master'

    idx.to_csv(INDEX, index=False)
    print(f'merges applied: {len(pairs)} -> papers {n_before} -> {len(idx)}')
    for a, t, _ in pairs:
        print(f'  {a}\n    -> {t}')
    print(f'year_unverified: {n_unverified_titles} titled PReMI 2023 papers not in the proceedings -> '
          f'{int(mask.sum())} paper_keys after merges ({len(absorbed_unverified)} absorbed by a merge)')
    print(f'ppsn_partial: {int(ppsn.sum())} PPSN papers')
    print(f'my_decision = "merge" on {review["my_decision"].eq("merge").sum()} review rows')
    print('assertions passed: every master row maps to exactly one paper_key; n_rows sums to '
          f'{len(d)}; paper_key unique')


if __name__ == '__main__':
    sys.exit(main())
