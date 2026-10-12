"""
Ingest new extraction CSVs into papers_master_with_matching_text.csv.

Usage:
    python ingest.py --input <csv file or folder of CSVs> --source <venue label> [--dry-run]

Venue-agnostic and contributor-agnostic: there is no venue-specific logic and no
content filtering. Every paper is kept unless it is a duplicate of a paper that is
already in the master (or was already added earlier in the same run).

Input schema: the old extraction schema, i.e. Paper_ID plus the 26 data columns of
the master. Any missing or extra column stops the run with an error.

Duplicates: a paper is skipped when its normalised title or normalised Source_File
already exists in the master, or its title was already added earlier in this run.
Source_File is not used to dedupe within a run, because contributors' file names are
not unique (generic names like "018_paper.pdf" are reused for different papers).

Per input row:
    - null tokens (unknown, not reported, nan, none, n/a, na, '' - case-insensitive)
      are mapped to the master's conventions:
        Dataset_Name / Source_Platform on a 'Pure Math' row -> 'N/A (Pure Math problem)'
        everything else                                      -> 'Not Reported'
    - raw_paper_id = the input Paper_ID, unchanged
    - paper_id     = 'P' + sha1(normalised_title)[:10] + '_Ext_' + NN
      (Year is added to the hash input when two different papers - different
      normalised Source_File - share a normalised title in this run).
      A row with no Paper_Title is kept (title 'Not Reported'); its paper is
      identified, and hashed, by Source_File + Authors + Year instead.
    - matching_text, language, matching_text_original, translated are left empty
      (Part 2 fills them).

Side files (next to this script):
    ingest_skipped.csv  - papers skipped as duplicates in this run (overwritten every run)
    ingest_log.csv      - per-paper source / input file / year / status (appended, real runs only)
    backup_v1/master_before_ingest.csv - copy of the master taken before the first real write
"""

import argparse
import csv
import hashlib
import io
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
MASTER_CSV = ROOT / 'papers_master_with_matching_text.csv'
BACKUP_DIR = ROOT / 'backup_v1'
BACKUP_MASTER = BACKUP_DIR / 'master_before_ingest.csv'
SKIPPED_CSV = ROOT / 'ingest_skipped.csv'
LOG_CSV = ROOT / 'ingest_log.csv'

ID_COLS = ['paper_id', 'raw_paper_id']
PART2_COLS = ['matching_text', 'language', 'matching_text_original', 'translated']
INPUT_ID_COL = 'Paper_ID'

NULL_TOKENS = {'unknown', 'not reported', 'nan', 'none', 'n/a', 'na', ''}
NOT_REPORTED = 'Not Reported'
PURE_MATH_NA = 'N/A (Pure Math problem)'
PURE_MATH_NA_COLS = ['Dataset_Name', 'Source_Platform']
PURE_MATH = 'Pure Math'

SKIPPED_FIELDS = ['run_timestamp', 'source', 'input_file', 'raw_paper_prefix', 'Paper_Title',
                  'Source_File', 'Year', 'n_rows', 'reason', 'matching_paper_id']
LOG_FIELDS = ['run_timestamp', 'source', 'input_file', 'paper_id', 'raw_paper_prefix', 'Source_File',
              'Paper_Title', 'Year', 'n_rows', 'status', 'reason', 'matching_paper_id']


class IngestError(Exception):
    pass


def norm_text(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def norm_source(s):
    # compare the file name only, without folders or extension (".pdf")
    name = re.split(r'[\\/]', str(s).strip())[-1]
    return norm_text(re.sub(r'\.[A-Za-z0-9]{1,5}$', '', name))


def norm_year(y):
    m = re.search(r'\d{4}', str(y))
    return m.group(0) if m else ''


def raw_prefix(pid):
    return re.sub(r'_Ext_\d+$', '', str(pid))


def read_csv_str(path):
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    except UnicodeDecodeError as e:
        raise IngestError(f'{path}: not valid UTF-8 ({e}). Re-save the file as UTF-8.')


def list_inputs(inp):
    p = Path(inp)
    if p.is_dir():
        files = sorted(f for f in p.iterdir() if f.is_file() and f.suffix.lower() == '.csv')
        if not files:
            raise IngestError(f'{p}: folder contains no .csv files')
        return files
    if p.is_file():
        if p.suffix.lower() != '.csv':
            raise IngestError(f'{p}: only CSV input is supported for now')
        return [p]
    raise IngestError(f'{p}: no such file or folder')


def load_input(path, data_cols):
    df = read_csv_str(path)
    cols = list(df.columns)
    dup = sorted({c for c in cols if cols.count(c) > 1})
    expected = [INPUT_ID_COL] + data_cols
    missing = [c for c in expected if c not in cols]
    extra = [c for c in cols if c not in expected]
    if dup or missing or extra:
        msg = [f'{path}: column mismatch with the expected input schema.']
        if missing:
            msg.append(f'  missing columns: {missing}')
        if extra:
            msg.append(f'  extra columns:   {extra}')
        if dup:
            msg.append(f'  duplicated columns: {dup}')
        msg.append(f'  expected exactly: {expected}')
        raise IngestError('\n'.join(msg))

    # pandas renames duplicated headers, so the checks above are complete
    df = df[expected].copy()
    for c in expected:
        s = df[c].astype(str)
        is_null = s.str.strip().str.lower().isin(NULL_TOKENS)
        df[c] = s.str.strip().where(~is_null, None)

    # rows without a title are kept; their paper is identified by Source_File + Authors + Year
    df['_untitled'] = df['Paper_Title'].isna()
    bad = df.index[df[INPUT_ID_COL].isna()].tolist()
    if bad:
        raise IngestError(f'{path}: Paper_ID is empty on data rows {[i + 2 for i in bad][:20]} '
                          f'(line numbers in the file).')

    # master null conventions
    for c in data_cols:
        fill = pd.Series(NOT_REPORTED, index=df.index)
        if c in PURE_MATH_NA_COLS:
            fill = fill.mask(df['Category'] == PURE_MATH, PURE_MATH_NA)
        df[c] = df[c].fillna(fill)
    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input', required=True, help='CSV file or folder of CSVs')
    ap.add_argument('--source', required=True, help='venue label, free text (e.g. PReMI, CEC, GECCO)')
    ap.add_argument('--dry-run', action='store_true', help='report only; writes nothing except ingest_skipped.csv')
    args = ap.parse_args()
    source = args.source.strip()
    if not source:
        raise IngestError('--source must not be empty')
    run_ts = datetime.now().isoformat(timespec='seconds')

    # ---------------- master ----------------
    master_bytes = MASTER_CSV.read_bytes()
    master = pd.read_csv(io.BytesIO(master_bytes), dtype=str, keep_default_na=False)
    master_cols = list(master.columns)
    for c in ID_COLS + PART2_COLS:
        if c not in master_cols:
            raise IngestError(f'{MASTER_CSV}: expected column {c!r} not found')
    data_cols = [c for c in master_cols if c not in ID_COLS + PART2_COLS]
    n_master = len(master)
    master_categories = set(master['Category'])

    master_title = {}
    master_src = {}
    for pid, t, s in zip(master['paper_id'], master['Paper_Title'], master['Source_File']):
        master_title.setdefault(norm_text(t), raw_prefix(pid))
        master_src.setdefault(norm_source(s), raw_prefix(pid))
    master_ids = set(master['paper_id'])
    master_prefixes = {raw_prefix(p) for p in master_ids}

    # ---------------- inputs ----------------
    files = list_inputs(args.input)
    inputs = [(f, load_input(f, data_cols)) for f in files]

    # papers = distinct (normalised title, normalised Source_File) pairs.
    # An untitled paper's "title" key is built from Source_File + Authors + Year instead.
    for _, df in inputs:
        df['_ns'] = df['Source_File'].map(lambda s: '' if s == NOT_REPORTED else norm_source(s))
        df['_nt'] = df['Paper_Title'].map(norm_text)
        untitled_key = ('untitled' + df['_ns'] + 'by' + df['Authors'].map(norm_text)
                        + 'in' + df['Year'].map(norm_year))
        df['_nt'] = df['_nt'].where(~df['_untitled'], untitled_key)

    # titles shared by different papers anywhere in this run -> add Year to the hash
    srcs_per_title = {}
    for _, df in inputs:
        for nt, ns in zip(df['_nt'], df['_ns']):
            srcs_per_title.setdefault(nt, set()).add(ns)
    ambiguous_titles = {t for t, s in srcs_per_title.items() if len(s) > 1}

    def paper_hash(nt, year):
        key = nt + (norm_year(year) if nt in ambiguous_titles else '')
        return 'P' + hashlib.sha1(key.encode('utf-8')).hexdigest()[:10]

    # within a run only the title key dedupes: Source_File names are not unique across
    # contributors (e.g. generic "018_paper.pdf"), so they are matched against the master only
    added_title = {}   # norm title  -> new paper prefix (added earlier in this run)
    prefix_owner = {}  # new paper prefix -> (nt, ns) that claimed it
    new_rows = []
    skipped = []
    log = []
    per_file = []
    collisions = []
    warnings = []

    for path, df in inputs:
        rel = os.path.relpath(path, ROOT)
        st = dict(file=rel, rows_in=len(df), papers_in=0, papers_skipped=0, papers_added=0,
                  rows_added=0, exact_dup_rows=0, untitled_added=0, cats={})
        papers = df.groupby(['_nt', '_ns'], sort=False)
        st['papers_in'] = papers.ngroups
        for (nt, ns), g in papers:
            first = g.iloc[0]
            years = sorted({norm_year(y) for y in g['Year']} - {''})
            if len(years) > 1:
                warnings.append(f'{rel}: paper "{first["Paper_Title"][:60]}" has several Years {years}; '
                                f'using {norm_year(first["Year"]) or "none"} for the ID')
            info = dict(run_timestamp=run_ts, source=source, input_file=rel,
                        raw_paper_prefix=';'.join(dict.fromkeys(g[INPUT_ID_COL].map(raw_prefix))),
                        Paper_Title=first['Paper_Title'], Source_File=first['Source_File'],
                        Year=first['Year'], n_rows=len(g))

            reason = match = None
            if nt in master_title:
                reason, match = 'title already in master', master_title[nt]
            elif ns and ns in master_src:
                reason, match = 'Source_File already in master', master_src[ns]
            elif nt in added_title:
                reason, match = 'title already added earlier in this run', added_title[nt]
            if reason:
                st['papers_skipped'] += 1
                skipped.append({**info, 'reason': reason, 'matching_paper_id': match})
                log.append({**info, 'paper_id': '', 'status': 'skipped_duplicate',
                            'reason': reason, 'matching_paper_id': match})
                continue

            prefix = paper_hash(nt, first['Year'])
            if prefix in master_prefixes or (prefix in prefix_owner and prefix_owner[prefix] != (nt, ns)):
                collisions.append((rel, prefix, first['Paper_Title']))
            prefix_owner[prefix] = (nt, ns)

            rows = g[[INPUT_ID_COL] + data_cols]
            dedup = rows.drop_duplicates(subset=data_cols, keep='first')
            st['exact_dup_rows'] += len(rows) - len(dedup)

            for i, (_, r) in enumerate(dedup.iterrows(), start=1):
                row = {c: '' for c in master_cols}
                row['paper_id'] = f'{prefix}_Ext_{i:02d}'
                row['raw_paper_id'] = r[INPUT_ID_COL]
                for c in data_cols:
                    row[c] = r[c]
                new_rows.append(row)
                cat = r['Category']
                st['cats'][cat] = st['cats'].get(cat, 0) + 1

            added_title[nt] = prefix
            if first['_untitled']:
                st['untitled_added'] += 1
            st['papers_added'] += 1
            st['rows_added'] += len(dedup)
            log.append({**info, 'n_rows': len(dedup), 'paper_id': prefix, 'status': 'added',
                        'reason': '', 'matching_paper_id': ''})
        per_file.append(st)

    new_ids = [r['paper_id'] for r in new_rows]
    id_dups = len(new_ids) - len(set(new_ids)) + len(set(new_ids) & master_ids)
    n_collisions = len(collisions) + id_dups

    unknown_cats = sorted({c for r in new_rows for c in [r['Category']]} - master_categories)
    if unknown_cats:
        warnings.append(f'Category values not used in the master: {unknown_cats} '
                        f'(master uses {sorted(master_categories)}). Rows are kept as-is.')

    # ---------------- report ----------------
    mode = 'DRY RUN' if args.dry_run else 'WRITE'
    print(f'=== ingest.py [{mode}]  source={source!r}  run={run_ts} ===')
    print(f'master: {MASTER_CSV.name}  rows={n_master}  columns={len(master_cols)}')
    print(f'input files: {len(files)}\n')
    hdr = f'{"file":<45} {"rows_in":>7} {"papers_in":>9} {"skip_dup":>8} {"added":>6} {"rows_add":>8} {"exact_dup_rows":>14}  category split (rows added)'
    print(hdr)
    print('-' * len(hdr))
    tot = dict(rows_in=0, papers_in=0, papers_skipped=0, papers_added=0, rows_added=0, exact_dup_rows=0)
    tot_cats = {}
    for st in per_file:
        for k in tot:
            tot[k] += st[k]
        for k, v in st['cats'].items():
            tot_cats[k] = tot_cats.get(k, 0) + v
        cats = ', '.join(f'{k}: {v}' for k, v in sorted(st['cats'].items())) or '-'
        print(f'{Path(st["file"]).name:<45} {st["rows_in"]:>7} {st["papers_in"]:>9} {st["papers_skipped"]:>8} '
              f'{st["papers_added"]:>6} {st["rows_added"]:>8} {st["exact_dup_rows"]:>14}  {cats}')
    print('-' * len(hdr))
    cats = ', '.join(f'{k}: {v}' for k, v in sorted(tot_cats.items())) or '-'
    print(f'{"TOTAL":<45} {tot["rows_in"]:>7} {tot["papers_in"]:>9} {tot["papers_skipped"]:>8} '
          f'{tot["papers_added"]:>6} {tot["rows_added"]:>8} {tot["exact_dup_rows"]:>14}  {cats}')
    paper_cats = {}
    for r in new_rows:
        if r['paper_id'].endswith('_Ext_01'):
            paper_cats[r['Category']] = paper_cats.get(r['Category'], 0) + 1
    print(f'category split (papers added, by first row): '
          f'{", ".join(f"{k}: {v}" for k, v in sorted(paper_cats.items())) or "-"}')
    n_untitled = sum(st['untitled_added'] for st in per_file)
    print(f'untitled papers added (ID from Source_File + Authors + Year): {n_untitled}'
          + (' [' + ', '.join(f'{st["file"].split("/")[-1]}: {st["untitled_added"]}' for st in per_file) + ']'
             if n_untitled else ''))
    print(f'paper_id collisions: {n_collisions}')
    for c in collisions:
        print(f'  COLLISION {c}')
    print(f'titles hashed with Year (shared by different papers): {len(ambiguous_titles)}')
    for w in warnings:
        print(f'WARNING: {w}')

    reasons = {}
    for s in skipped:
        reasons[s['reason']] = reasons.get(s['reason'], 0) + 1
    if reasons:
        print('skip reasons: ' + ', '.join(f'{k}: {v}' for k, v in reasons.items()))

    pd.DataFrame(skipped, columns=SKIPPED_FIELDS).to_csv(SKIPPED_CSV, index=False)
    print(f'\nwrote {SKIPPED_CSV.name} ({len(skipped)} skipped papers)')

    if n_collisions:
        raise IngestError(f'{n_collisions} paper_id collision(s); nothing written to the master.')

    if args.dry_run:
        print(f'DRY RUN: master not modified. Would append {len(new_rows)} rows -> {n_master + len(new_rows)} rows.')
        return

    # ---------------- write ----------------
    if not new_rows:
        print('nothing to add; master not modified.')
    else:
        BACKUP_DIR.mkdir(exist_ok=True)
        if not BACKUP_MASTER.exists():
            shutil.copy2(MASTER_CSV, BACKUP_MASTER)
            print(f'backup: {BACKUP_MASTER.relative_to(ROOT)}')

        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=master_cols, lineterminator='\n')
        w.writerows(new_rows)
        prefix_bytes = master_bytes if master_bytes.endswith(b'\n') else master_bytes + b'\n'
        out_bytes = prefix_bytes + buf.getvalue().encode('utf-8')

        # verify before replacing the master
        new_master = pd.read_csv(io.BytesIO(out_bytes), dtype=str, keep_default_na=False)
        assert list(new_master.columns) == master_cols, 'column list/order changed'
        assert new_master['paper_id'].is_unique, 'paper_id values are not unique'
        assert len(new_master) == n_master + len(new_rows), 'unexpected row count'
        assert new_master.iloc[:n_master].reset_index(drop=True).equals(master), 'first N rows differ from old master'

        tmp = MASTER_CSV.with_suffix('.csv.tmp')
        tmp.write_bytes(out_bytes)
        os.replace(tmp, MASTER_CSV)

        check = pd.read_csv(MASTER_CSV, dtype=str, keep_default_na=False)
        assert list(check.columns) == master_cols
        assert check['paper_id'].is_unique
        assert check.iloc[:n_master].reset_index(drop=True).equals(master)
        print(f'appended {len(new_rows)} rows: master {n_master} -> {len(check)} rows (checks passed)')

    log_exists = LOG_CSV.exists()
    with open(LOG_CSV, 'a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS, lineterminator='\n')
        if not log_exists:
            w.writeheader()
        w.writerows(log)
    print(f'appended {len(log)} entries to {LOG_CSV.name}')


if __name__ == '__main__':
    try:
        main()
    except IngestError as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
