"""
v2 Part B - PPSN review (read-only on the master).

Writes ppsn_review.csv (every PPSN row) and prints, per Source_File, the rows grouped by
Problem_Context. The number of distinct Problem_Context values per file is reported as an
ESTIMATE of the number of underlying papers: it is a heuristic, not a fact, because one
paper can use several contexts and several papers can share a generic context such as
"Evaluating mathematical landscapes". The PPSN flags themselves are added to
paper_index.csv by v2_step1_validate.py.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / 'papers_master_v2.csv'
OLD_MASTER = ROOT / 'backup_v1' / 'master_before_ingest.csv'
OUT = ROOT / 'ppsn_review.csv'
COLS = ['Paper_ID', 'Year', 'Source_File', 'Problem_Context', 'Benchmark_Name', 'Algorithm_Name',
        'Evaluation_Dataset', 'Authors']
CONTENT_KEY = ['Paper_Title', 'Source_File', 'Benchmark_Name', 'Algorithm_Name', 'Evaluation_Dataset',
               'Problem_Context', 'Environment', 'Performance_Metric']


def main():
    d = pd.read_csv(MASTER, dtype=str, keep_default_na=False)
    pp = d[d['Conference'] == 'PPSN']
    assert len(pp) == 92 and pp['Source_File'].nunique() == 5, (len(pp), pp['Source_File'].nunique())
    pp[COLS].to_csv(OUT, index=False)
    print(f'wrote {OUT.name}: {len(pp)} rows, columns {COLS}\n')

    print('ESTIMATE of distinct underlying papers per file (= distinct Problem_Context values):')
    total = 0
    for f, g in pp.groupby('Source_File', sort=True):
        ctx = g.groupby('Problem_Context', sort=False).agg(rows=('Paper_ID', 'size'),
                                                           ext=('Paper_ID', lambda s: f'{s.iloc[0][-6:]}..{s.iloc[-1][-6:]}'),
                                                           algorithms=('Algorithm_Name', 'nunique'))
        total += len(ctx)
        print(f'\n{f} (Year {g["Year"].iloc[0]}, title "{g["Paper_Title"].iloc[0][:70]}"): {len(g)} rows, '
              f'ESTIMATE {len(ctx)} papers')
        for c, r in ctx.iterrows():
            print(f'  - {c[:80]!r}: {r.rows} rows ({r.ext}), {r.algorithms} algorithms')
    print(f'\nESTIMATE total: {total} underlying papers across the 5 PPSN files (vs 5 paper_keys now)')

    if OLD_MASTER.exists():
        o = pd.read_csv(OLD_MASTER, dtype=str, keep_default_na=False)
        old = o[o['Source_File'].isin(pp['Source_File'])]
        m = pp.merge(old[CONTENT_KEY].drop_duplicates(), on=CONTENT_KEY, how='left', indicator=True)
        print(f'\nold master ({OLD_MASTER.name}): {len(old)} rows from the same 5 PPSN files; '
              f'{int((m["_merge"] == "both").sum())} of {len(pp)} v2 PPSN rows match an old row on {len(CONTENT_KEY)} '
              f'content columns. Rows per file old -> v2: '
              f'{ {f: f"{(old.Source_File == f).sum()} -> {(pp.Source_File == f).sum()}" for f in sorted(pp.Source_File.unique())} }')
        new = m[m['_merge'] == 'left_only']
        for _, r in new.iterrows():
            print(f'  not in old master: {r.Paper_ID} | {r.Source_File} | {r.Benchmark_Name[:50]} | {r.Algorithm_Name[:40]}')


if __name__ == '__main__':
    sys.exit(main())
