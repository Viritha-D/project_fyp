"""
Part 2 - build matching_text for master rows that do not have one yet (e.g. after ingest.py).

Recipes (reproduce the existing master exactly - see --check):
    Applied      "<Problem_Context>. <Paper_Title>"
                 If the paper is marked title_suspect in ingest_log.csv (title shared by
                 several different papers, or fewer than 3 words), or has no title, the
                 text is Problem_Context only, without Paper_Title.
    other        "<Benchmark_Name>. <Target_Landscape>. <Landscape_Characteristics>"
    (Pure Math, and the new 'Benchmark' category), skipping "Not Reported" / N/A parts.
                 If all three are missing, falls back to Problem_Context (the existing
                 master never needs this; it is reported when used).

Usage:
    python part2_matching_text.py --check   # read-only: rebuild the existing rows and compare
    python part2_matching_text.py           # fill rows whose matching_text is empty

Filling sets matching_text and matching_text_original only. Language detection and
translation (language, translated) are a separate step and are left untouched.
"""

import argparse
import io
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
MASTER_CSV = ROOT / 'papers_master_with_matching_text.csv'
LOG_CSV = ROOT / 'ingest_log.csv'

APPLIED = 'Applied'
MISSING = {'', 'Not Reported', 'N/A (Pure Math problem)'}


def paper_prefix(paper_id):
    return paper_id.rsplit('_Ext_', 1)[0] if '_Ext_' in paper_id else paper_id


def load_suspect_prefixes():
    """paper_id prefixes marked title_suspect in ingest_log.csv (added papers only)."""
    if not LOG_CSV.exists():
        return set()
    log = pd.read_csv(LOG_CSV, dtype=str, keep_default_na=False)
    if 'title_suspect' not in log.columns:
        return set()
    added = log[(log['status'] == 'added') & (log['title_suspect'] == 'True')]
    return set(added['paper_id'])


def build_matching_text(row, title_suspect=False):
    """Matching text for one master row ('' if the row has no usable part)."""
    if row['Category'] == APPLIED:
        context = row['Problem_Context'].strip()
        title = row['Paper_Title'].strip()
        if title_suspect or title in MISSING:
            title = ''
        parts = [p for p in (context if context not in MISSING else '', title) if p]
        return '. '.join(parts)
    parts = [row['Benchmark_Name'], row['Target_Landscape'], row['Landscape_Characteristics']]
    text = '. '.join(p for p in parts if p not in MISSING)
    return text or (row['Problem_Context'].strip() if row['Problem_Context'].strip() not in MISSING else '')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='read-only: compare the recipe with existing rows')
    args = ap.parse_args()

    raw = MASTER_CSV.read_bytes()
    master = pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False)
    suspects = load_suspect_prefixes()
    prefixes = master['paper_id'].map(paper_prefix)
    is_suspect = prefixes.isin(suspects)

    texts = pd.Series([build_matching_text(r, s) for (_, r), s in zip(master.iterrows(), is_suspect)],
                      index=master.index)

    filled = master['matching_text'] != ''
    if args.check:
        # translated rows hold English text built from the original-language fields, so skip them
        comparable = filled & (master['translated'] != 'True') & ~is_suspect
        ok = (texts == master['matching_text'])[comparable]
        print(f'rows with matching_text: {int(filled.sum())}; comparable (not translated, not suspect): '
              f'{int(comparable.sum())}; recipe reproduces them exactly: {int(ok.sum())}')
        for cat, g in master[comparable].groupby('Category'):
            print(f'  {cat}: {int(ok[g.index].sum())}/{len(g)}')
        print(f'rows marked title_suspect in ingest_log.csv: {int(is_suspect.sum())} '
              f'(Applied: {int((is_suspect & (master["Category"] == APPLIED)).sum())})')
        empty = ~filled
        print(f'rows still without matching_text: {int(empty.sum())}; of those empty after build: '
              f'{int((texts[empty] == "").sum())}')
        return 0 if ok.all() else 1

    todo = ~filled
    if not todo.any():
        print('nothing to do: every row already has matching_text')
        return 0
    if (texts[todo] == '').any():
        bad = master.loc[todo & (texts == ''), 'paper_id'].tolist()
        raise SystemExit(f'ERROR: no usable text for {len(bad)} rows, e.g. {bad[:5]}; nothing written')
    out = master.copy()
    out.loc[todo, 'matching_text'] = texts[todo]
    out.loc[todo, 'matching_text_original'] = texts[todo]
    n_susp = int((todo & is_suspect & (master['Category'] == APPLIED)).sum())
    n_fb = int((todo & (master['Category'] != APPLIED) & (texts == master['Problem_Context'])).sum())
    tmp = MASTER_CSV.with_suffix('.csv.tmp')
    out.to_csv(tmp, index=False, lineterminator='\n')
    os.replace(tmp, MASTER_CSV)
    print(f'filled matching_text for {int(todo.sum())} rows ({n_susp} Applied rows built from Problem_Context only; '
          f'{n_fb} non-Applied rows fell back to Problem_Context)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
