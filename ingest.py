"""
Ingest new extraction CSVs into papers_master_with_matching_text.csv.

Usage:
    python ingest.py --input <csv file or folder of CSVs> --source <venue label> [--dry-run]

Venue-agnostic and contributor-agnostic: no venue-specific logic and no content
filtering. Every paper is kept unless one of the duplicate rules below fires.

Input schema: the old extraction schema, i.e. Paper_ID plus the 26 data columns of
the master. Any missing or extra column stops the run with an error.

A paper is one distinct Source_File + Year + Title + Authors within an input file.
    identity = (source label, normalised Source_File, Year)

Duplicate rules, checked in this order (a paper is skipped by the first that fires):
    IDENTITY_IN_LOG          identity already appears in ingest_log.csv. Makes re-runs
                             idempotent, untitled papers included.
    CONTENT_IN_MASTER        normalised title AND normalised authors AND year all match a
    CONTENT_IN_RUN           paper already in the master / added earlier in this run.
                             Never title alone. A missing title, missing authors or
                             missing year can never match.
    SOURCE_FILE_YEAR_IN_MASTER
                             the Source_File (same Year) is already in the master. Not
                             applied to generic names matching ^\\d+_paper\\.pdf$, which
                             contributors reuse for different papers.
Source_File alone never dedupes.

Per input row:
    - null tokens (unknown, not reported, nan, none, n/a, na, '' - case-insensitive)
      map to the master's conventions: 'Not Reported', or 'N/A (Pure Math problem)' in
      Dataset_Name / Source_Platform on Pure Math rows. For Paper_Title the tokens
      'not provided', 'none provided' and 'conclusion' also mean "missing" (untitled).
    - raw_paper_id = the input Paper_ID, unchanged
    - paper_id = 'P' + sha1(norm_source_file|year|norm_title)[:10] + '_Ext_' + NN
      (NN = row index within the paper; the input file name is added to the hash input
      when two different papers would otherwise collide; norm_title is '' if untitled)
    - matching_text, language, matching_text_original, translated are left empty
      (Part 2 fills them).

Side files (next to this script):
    ingest_skipped.csv  skipped papers with the rule, the matching paper_id and its
                        Source_File (overwritten every run, also on --dry-run)
    ingest_log.csv      one line per paper per real run (appended): source, input file,
                        Source_File, Year, status, paper_id and title_suspect.
                        title_suspect = True when the title is shared by >= 3 different
                        Source_Files in this run whose authors differ, or has < 3 words
                        (an untitled paper has 0 words). Paper_Title in the master is
                        never changed.
    backup_v1/master_before_ingest.csv  copy of the master, made before the first real write
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
MISSING_TITLE_TOKENS = NULL_TOKENS | {'not provided', 'none provided', 'conclusion'}
NOT_REPORTED = 'Not Reported'
PURE_MATH_NA = 'N/A (Pure Math problem)'
PURE_MATH_NA_COLS = ['Dataset_Name', 'Source_Platform']
PURE_MATH = 'Pure Math'
GENERIC_SOURCE_RE = re.compile(r'^\d+_paper\.pdf$', re.I)
SUSPECT_MIN_SOURCES = 3
SUSPECT_MIN_WORDS = 3

RULE_LOG = 'IDENTITY_IN_LOG'
RULE_CONTENT_MASTER = 'CONTENT_IN_MASTER'
RULE_CONTENT_RUN = 'CONTENT_IN_RUN'
RULE_SOURCE_MASTER = 'SOURCE_FILE_YEAR_IN_MASTER'
RULE_TEXT = {
    RULE_LOG: 'source+Source_File+Year already in ingest_log.csv',
    RULE_CONTENT_MASTER: 'title+authors+year match a paper in the master',
    RULE_CONTENT_RUN: 'title+authors+year match a paper added earlier in this run',
    RULE_SOURCE_MASTER: 'Source_File (same Year) already in the master',
}

SKIPPED_FIELDS = ['run_timestamp', 'source', 'input_file', 'raw_paper_prefix', 'Paper_Title', 'Authors',
                  'Source_File', 'Year', 'n_rows', 'rule', 'reason', 'matching_paper_id',
                  'matching_Source_File', 'matching_location']
LOG_FIELDS = ['run_timestamp', 'source', 'input_file', 'paper_id', 'raw_paper_prefix', 'Source_File',
              'Paper_Title', 'Authors', 'Year', 'n_rows', 'status', 'rule', 'matching_paper_id',
              'title_suspect']


class IngestError(Exception):
    pass


def norm_text(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def basename(s):
    return re.split(r'[\\/]', str(s).strip())[-1]


def norm_source(s):
    # file name only, without folders or extension
    return norm_text(re.sub(r'\.[A-Za-z0-9]{1,5}$', '', basename(s)))


def norm_year(y):
    m = re.search(r'\d{4}', str(y))
    return m.group(0) if m else ''


def raw_prefix(pid):
    return re.sub(r'_Ext_\d+$', '', str(pid))


def word_count(title):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", str(title)))


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

    df = df[expected].copy()
    for c in expected:
        s = df[c].astype(str).str.strip()
        tokens = MISSING_TITLE_TOKENS if c == 'Paper_Title' else NULL_TOKENS
        df[c] = s.where(~s.str.lower().isin(tokens), None)

    df['_untitled'] = df['Paper_Title'].isna()   # flag before the master-convention fill below

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


def load_log_identities():
    """(source key, norm Source_File, Year) -> (paper_id or matching id, Source_File)."""
    if not LOG_CSV.exists():
        return {}
    log = read_csv_str(LOG_CSV)
    need = {'source', 'Source_File', 'Year', 'paper_id', 'matching_paper_id'}
    if not need <= set(log.columns):
        raise IngestError(f'{LOG_CSV}: expected columns {sorted(need)}, found {list(log.columns)}')
    out = {}
    for _, r in log.iterrows():
        ns = norm_source(r['Source_File']) if r['Source_File'] != NOT_REPORTED else ''
        if not ns:
            continue
        out.setdefault((norm_text(r['source']), ns, norm_year(r['Year'])),
                       (r['paper_id'] or r['matching_paper_id'], r['Source_File']))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input', required=True, help='CSV file or folder of CSVs')
    ap.add_argument('--source', required=True, help='venue label, free text (e.g. PReMI, CEC, GECCO)')
    ap.add_argument('--dry-run', action='store_true', help='report only; writes nothing except ingest_skipped.csv')
    args = ap.parse_args()
    source = args.source.strip()
    if not source:
        raise IngestError('--source must not be empty')
    src_key = norm_text(source)
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

    master_content = {}   # (title, authors, year) -> (paper prefix, Source_File)
    master_srcyear = {}   # (Source_File, year)    -> (paper prefix, Source_File)
    for pid, t, a, y, s in zip(master['paper_id'], master['Paper_Title'], master['Authors'],
                               master['Year'], master['Source_File']):
        pre, yy = raw_prefix(pid), norm_year(y)
        nt, na = norm_text(t), (norm_text(a) if a != NOT_REPORTED else '')
        if nt and na and yy:
            master_content.setdefault((nt, na, yy), (pre, s))
        ns = norm_source(s)
        if ns:
            master_srcyear.setdefault((ns, yy), (pre, s))
    master_ids = set(master['paper_id'])
    master_prefixes = {raw_prefix(p) for p in master_ids}

    log_identities = load_log_identities()

    # ---------------- inputs -> papers ----------------
    files = list_inputs(args.input)
    papers = []   # one dict per paper, in input order
    for path in files:
        df = load_input(path, data_cols)
        rel = os.path.relpath(path, ROOT)
        df['_untitled'] = df['_untitled'] | (df['Paper_Title'].map(norm_text) == '')
        df['_nt'] = df['Paper_Title'].map(norm_text).where(~df['_untitled'], '')
        df['_ns'] = df['Source_File'].map(lambda s: '' if s == NOT_REPORTED else norm_source(s))
        df['_na'] = df['Authors'].map(lambda a: '' if a == NOT_REPORTED else norm_text(a))
        df['_y'] = df['Year'].map(norm_year)
        for (ns, y, nt, na), g in df.groupby(['_ns', '_y', '_nt', '_na'], sort=False):
            first = g.iloc[0]
            papers.append(dict(
                file=rel, fname=Path(path).name, rows=g, n_rows=len(g), ns=ns, y=y, nt=nt, na=na,
                untitled=bool(first['_untitled']),
                title=NOT_REPORTED if first['_untitled'] else first['Paper_Title'],
                authors=first['Authors'], source_file=first['Source_File'], year=first['Year'],
                raw_prefix=';'.join(dict.fromkeys(g[INPUT_ID_COL].map(raw_prefix))),
                category=first['Category']))

    # title_suspect: title under >= 3 Source_Files with differing authors, or < 3 words
    by_title = {}
    for p in papers:
        if not p['untitled']:
            by_title.setdefault(p['nt'], []).append(p)
    for p in papers:
        spread = False
        if not p['untitled']:
            grp = by_title[p['nt']]
            spread = (len({q['ns'] for q in grp}) >= SUSPECT_MIN_SOURCES
                      and len({q['na'] for q in grp}) > 1)
        p['title_suspect'] = bool(spread or (0 if p['untitled'] else word_count(p['title'])) < SUSPECT_MIN_WORDS)

    # ---------------- dedupe ----------------
    run_content = {}     # (title, authors, year) -> kept paper dict
    kept, skipped = [], []
    for p in papers:
        rule = match = None   # match = (paper_id or paper dict, Source_File, location)
        ident = (src_key, p['ns'], p['y'])
        content = (p['nt'], p['na'], p['y'])
        can_match_content = bool(p['nt'] and p['na'] and p['y'])
        if p['ns'] and ident in log_identities:
            pid, sf = log_identities[ident]
            rule, match = RULE_LOG, (pid, sf, 'ingest_log.csv')
        elif can_match_content and content in master_content:
            pid, sf = master_content[content]
            rule, match = RULE_CONTENT_MASTER, (pid, sf, 'master')
        elif can_match_content and content in run_content:
            k = run_content[content]
            rule, match = RULE_CONTENT_RUN, (k, k['source_file'], 'earlier in this run')
        elif (p['ns'] and not GENERIC_SOURCE_RE.match(basename(p['source_file']))
              and (p['ns'], p['y']) in master_srcyear):
            pid, sf = master_srcyear[(p['ns'], p['y'])]
            rule, match = RULE_SOURCE_MASTER, (pid, sf, 'master')
        if rule:
            p['rule'], p['match'] = rule, match
            skipped.append(p)
        else:
            if can_match_content:
                run_content[content] = p
            kept.append(p)

    # ---------------- paper_id ----------------
    def phash(p, with_file):
        key = f'{p["ns"]}|{p["y"]}|{p["nt"]}' + (f'|{p["fname"]}' if with_file else '')
        return 'P' + hashlib.sha1(key.encode('utf-8')).hexdigest()[:10]

    for p in kept:
        p['prefix'] = phash(p, False)
    counts = {}
    for p in kept:
        counts[p['prefix']] = counts.get(p['prefix'], 0) + 1
    n_hash_collisions = 0
    for p in kept:
        if counts[p['prefix']] > 1 or p['prefix'] in master_prefixes:
            p['prefix'] = phash(p, True)
            n_hash_collisions += 1
    seen = {}
    unresolved = []
    for p in kept:
        if p['prefix'] in master_prefixes or p['prefix'] in seen:
            unresolved.append((p['file'], p['prefix'], p['title'], p['source_file']))
        seen[p['prefix']] = p

    # ---------------- rows ----------------
    new_rows = []
    for p in kept:
        rows = p['rows'][[INPUT_ID_COL] + data_cols]
        dedup = rows.drop_duplicates(subset=data_cols, keep='first')
        p['exact_dups'] = len(rows) - len(dedup)
        p['rows_added'] = len(dedup)
        p['cats'] = {}
        for i, (_, r) in enumerate(dedup.iterrows(), start=1):
            row = {c: '' for c in master_cols}
            row['paper_id'] = f'{p["prefix"]}_Ext_{i:02d}'
            row['raw_paper_id'] = r[INPUT_ID_COL]
            for c in data_cols:
                row[c] = r[c]
            new_rows.append(row)
            p['cats'][r['Category']] = p['cats'].get(r['Category'], 0) + 1

    new_ids = [r['paper_id'] for r in new_rows]
    id_dups = len(new_ids) - len(set(new_ids)) + len(set(new_ids) & master_ids)
    n_unresolved = len(unresolved) + id_dups

    warnings = []
    unknown_cats = sorted({r['Category'] for r in new_rows} - master_categories)
    if unknown_cats:
        warnings.append(f'Category values not used in the master: {unknown_cats} '
                        f'(master uses {sorted(master_categories)}). Rows are kept as-is.')

    # ---------------- skipped / log entries ----------------
    def match_id(p):
        m = p['match'][0]
        return m['prefix'] if isinstance(m, dict) else m

    skipped_out, log_out = [], []
    for p in skipped:
        skipped_out.append(dict(
            run_timestamp=run_ts, source=source, input_file=p['file'], raw_paper_prefix=p['raw_prefix'],
            Paper_Title=p['title'], Authors=p['authors'], Source_File=p['source_file'], Year=p['year'],
            n_rows=p['n_rows'], rule=p['rule'], reason=RULE_TEXT[p['rule']], matching_paper_id=match_id(p),
            matching_Source_File=p['match'][1], matching_location=p['match'][2]))
    for p in papers:   # log in input order
        base = dict(run_timestamp=run_ts, source=source, input_file=p['file'], raw_paper_prefix=p['raw_prefix'],
                    Source_File=p['source_file'], Paper_Title=p['title'], Authors=p['authors'],
                    Year=p['year'], title_suspect=p['title_suspect'])
        if 'rule' in p:
            log_out.append({**base, 'paper_id': '', 'n_rows': p['n_rows'], 'status': 'skipped_duplicate',
                            'rule': p['rule'], 'matching_paper_id': match_id(p)})
        else:
            log_out.append({**base, 'paper_id': p['prefix'], 'n_rows': p['rows_added'], 'status': 'added',
                            'rule': '', 'matching_paper_id': ''})

    # ---------------- report ----------------
    mode = 'DRY RUN' if args.dry_run else 'WRITE'
    print(f'=== ingest.py [{mode}]  source={source!r}  run={run_ts} ===')
    print(f'master: {MASTER_CSV.name}  rows={n_master}  columns={len(master_cols)}')
    print(f'input files: {len(files)}   ingest_log identities known: {len(log_identities)}\n')
    hdr = (f'{"file":<22} {"rows_in":>7} {"papers_in":>9} {"skipped":>7} {"added":>6} {"rows_add":>8} '
           f'{"exact_dup_rows":>14}  category split (rows added)')
    print(hdr)
    print('-' * len(hdr))
    tot = dict(rows_in=0, papers_in=0, skipped=0, added=0, rows_added=0, exact=0)
    tot_cats = {}
    for f in files:
        rel = os.path.relpath(f, ROOT)
        pf = [p for p in papers if p['file'] == rel]
        kf = [p for p in pf if 'rule' not in p]
        st = dict(rows_in=sum(p['n_rows'] for p in pf), papers_in=len(pf), skipped=len(pf) - len(kf),
                  added=len(kf), rows_added=sum(p['rows_added'] for p in kf),
                  exact=sum(p['exact_dups'] for p in kf))
        cats = {}
        for p in kf:
            for k, v in p['cats'].items():
                cats[k] = cats.get(k, 0) + v
                tot_cats[k] = tot_cats.get(k, 0) + v
        for k in tot:
            tot[k] += st[k]
        cs = ', '.join(f'{k}: {v}' for k, v in sorted(cats.items())) or '-'
        print(f'{f.name:<22} {st["rows_in"]:>7} {st["papers_in"]:>9} {st["skipped"]:>7} {st["added"]:>6} '
              f'{st["rows_added"]:>8} {st["exact"]:>14}  {cs}')
    print('-' * len(hdr))
    cs = ', '.join(f'{k}: {v}' for k, v in sorted(tot_cats.items())) or '-'
    print(f'{"TOTAL":<22} {tot["rows_in"]:>7} {tot["papers_in"]:>9} {tot["skipped"]:>7} {tot["added"]:>6} '
          f'{tot["rows_added"]:>8} {tot["exact"]:>14}  {cs}')
    paper_cats = {}
    for p in kept:
        paper_cats[p['category']] = paper_cats.get(p['category'], 0) + 1
    print(f'category split (papers added, by first row): '
          f'{", ".join(f"{k}: {v}" for k, v in sorted(paper_cats.items())) or "-"}')
    rules = {}
    for p in skipped:
        rules[p['rule']] = rules.get(p['rule'], 0) + 1
    print('skipped by rule: ' + (', '.join(f'{k}: {v}' for k, v in rules.items()) or '-'))
    sus = [p for p in kept if p['title_suspect']]
    print(f'untitled papers added: {sum(1 for p in kept if p["untitled"])}')
    print(f'title_suspect papers added: {len(sus)} ({sum(p["rows_added"] for p in sus)} rows); '
          f'in the whole input incl. skipped: {sum(1 for p in papers if p["title_suspect"])}')
    print(f'paper_id hash collisions resolved with the input file name: {n_hash_collisions}; '
          f'unresolved: {n_unresolved}')
    for c in unresolved:
        print(f'  UNRESOLVED COLLISION {c}')
    for w in warnings:
        print(f'WARNING: {w}')

    if skipped_out:
        print(f'\nskipped papers ({len(skipped_out)}):')
        for s in skipped_out:
            print(f'  [{s["rule"]}] {s["input_file"].split("/")[-1][0]}:{s["raw_paper_prefix"]} '
                  f'{s["Source_File"]} ({s["Year"]}) "{s["Paper_Title"][:50]}"  '
                  f'-> {s["matching_paper_id"]} {s["matching_Source_File"]} [{s["matching_location"]}]')

    pd.DataFrame(skipped_out, columns=SKIPPED_FIELDS).to_csv(SKIPPED_CSV, index=False)
    print(f'\nwrote {SKIPPED_CSV.name} ({len(skipped_out)} skipped papers)')

    if n_unresolved:
        raise IngestError(f'{n_unresolved} unresolved paper_id collision(s); nothing written to the master.')

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
        w.writerows(log_out)
    print(f'appended {len(log_out)} entries to {LOG_CSV.name}')


if __name__ == '__main__':
    try:
        main()
    except IngestError as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
