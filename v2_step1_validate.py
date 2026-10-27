"""
v2 Step 1 - validate and freeze master_dataset_clean.csv (read-only on the input).

Outputs:
    audit_report.md      counts, missing-value rates, paper identity, PPSN, repeats
    paper_index.csv      one row per paper (paper_key = Conference|Year|normalised title)
    papers_master_v2.csv byte-identical frozen copy of the input
    gold_standard_labels_remapped.csv  only when gold_standard_labels.csv exists

Paper identity never uses Source_File alone. An untitled paper ("Not Reported") gets the
key Conference|Year|<Source_File>|untitled, so untitled papers are never merged; the run
asserts that each such key holds exactly one Paper_ID root.
"""

import os
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'master_dataset_clean.csv'
FROZEN = ROOT / 'papers_master_v2.csv'
REPORT = ROOT / 'audit_report.md'
INDEX = ROOT / 'paper_index.csv'
OLD_MASTER = ROOT / 'backup_v2' / 'papers_master_with_matching_text.csv'
GOLD = ROOT / 'gold_standard_labels.csv'
GOLD_OUT = ROOT / 'gold_standard_labels_remapped.csv'

EXPECTED_ROWS = 11342
EXPECTED_COLS = ['Conference', 'Paper_ID', 'Original_Paper_ID', 'Category', 'Evaluation_Dataset', 'Environment',
                 'Target_Landscape', 'Winning_Strategy', 'Paper_Title', 'Authors', 'Year', 'Source_File',
                 'GECCO_Track', 'Industry', 'Problem_Context', 'Dataset_Name', 'Source_Platform', 'Benchmark_Name',
                 'Dimensionality', 'Modality', 'Separability', 'Landscape_Characteristics', 'Algorithm_Name',
                 'Population_Size', 'Max_Evaluations_or_Generations', 'Mutation_Rate', 'Crossover_Rate',
                 'Performance_Metric', 'Is_Optimal_Found']
REPEAT_KEY = ['Paper_Title', 'Benchmark_Name', 'Algorithm_Name', 'Evaluation_Dataset']
NOT_REPORTED = 'not reported'
MISSING_TITLES = {'', 'not reported', 'unknown', 'n/a', 'na', 'none', 'nan'}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def root_id(s):
    return re.sub(r'_Ext_\d+$', '', str(s))


def md_table(df, index=True):
    df = df.reset_index() if index else df
    cols = [str(c) for c in df.columns]
    lines = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for row in df.itertuples(index=False):
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in row) + ' |')
    return '\n'.join(lines)


def short(s, n=70):
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + '…'


def main():
    out = []   # report lines
    say = out.append

    d = pd.read_csv(INPUT, dtype=str, keep_default_na=False)

    # ---------------- b) assertions ----------------
    assert len(d) == EXPECTED_ROWS, f'expected {EXPECTED_ROWS} rows, got {len(d)}'
    assert list(d.columns) == EXPECTED_COLS, f'column mismatch: {list(d.columns)}'
    assert (d['Paper_ID'].str.strip() != '').all(), 'empty Paper_ID'
    assert d['Paper_ID'].is_unique, 'Paper_ID not unique'
    print(f'[1b] PASSED: {len(d)} rows, {len(d.columns)} columns, Paper_ID unique and never empty')

    # ---------------- d) paper identity ----------------
    d['_nt'] = d['Paper_Title'].map(norm)
    d['_untitled'] = d['Paper_Title'].str.strip().str.lower().isin(MISSING_TITLES) | (d['_nt'] == '')
    d['_ns'] = d['Source_File'].map(norm)
    d['_cy'] = d['Conference'] + '|' + d['Year']
    d['paper_key'] = (d['_cy'] + '|' + d['_nt']).where(~d['_untitled'], d['_cy'] + '|' + d['Source_File'] + '|untitled')
    u = d[d['_untitled']]
    roots_per_key = u.groupby('paper_key')['Paper_ID'].apply(lambda s: s.map(root_id).nunique())
    assert (roots_per_key == 1).all(), f'untitled key holds several papers: {roots_per_key[roots_per_key > 1]}'
    print(f'[1d] untitled: {len(u)} rows -> {len(roots_per_key)} paper_keys, each exactly one Paper_ID root')

    titles_per_file = d[~d['_untitled']].groupby(['_cy', '_ns'])['_nt'].nunique()
    multi_title_files = set(titles_per_file[titles_per_file > 1].index)

    rows = []
    for key, g in d.groupby('paper_key', sort=False):
        first = g.iloc[0]
        files = list(dict.fromkeys(g['Source_File']))
        flags = []
        if first['_untitled']:
            flags.append('untitled')
        if len({norm(f) for f in files}) > 1:
            flags.append('title_under_multiple_source_files')
        if any((first['_cy'], norm(f)) in multi_title_files for f in files):
            flags.append('source_file_has_multiple_titles')
        rows.append(dict(paper_key=key, Conference=first['Conference'], Year=first['Year'],
                         Source_Files=';'.join(files), title=first['Paper_Title'], n_rows=len(g),
                         n_source_files=len(files), paper_id_roots=';'.join(dict.fromkeys(g['Paper_ID'].map(root_id))),
                         flags=';'.join(flags)))
    idx = pd.DataFrame(rows)
    idx.to_csv(INDEX, index=False)
    flagged = idx[idx['flags'].str.contains('title_under|source_file_has')]
    print(f'[1d] paper_index.csv: {len(idx)} papers, {len(flagged)} flagged '
          f'(title under >1 file or file with >1 title), {int((idx["flags"].str.contains("untitled")).sum())} untitled')

    # ---------------- c) audit ----------------
    say('# Audit report: master_dataset_clean.csv\n')
    say(f'Input: `{INPUT.name}`, {len(d)} rows x {len(EXPECTED_COLS)} columns, read with every column as text. '
        f'The input is not modified; `{FROZEN.name}` is a byte-identical frozen copy.\n')
    say('Checks passed: 11,342 rows; 29 columns in the expected order; Paper_ID unique and never empty.\n')

    say('## Rows by Conference x Year\n')
    say(md_table(pd.crosstab(d['Conference'], d['Year'], margins=True, margins_name='Total')) + '\n')
    say('## Papers by Conference x Year\n')
    say('Paper = distinct `paper_key` (Conference|Year|normalised title; an untitled paper is keyed Conference|Year|Source_File|untitled).\n')
    say(md_table(pd.crosstab(idx['Conference'], idx['Year'], margins=True, margins_name='Total')) + '\n')

    say('## Category counts\n')
    cat = d['Category'].value_counts().rename('rows').to_frame()
    cat['papers'] = d.groupby('Category')['paper_key'].nunique()
    say(md_table(cat) + '\n')

    say('## Blank or "Not Reported" per column\n')
    say('Blank = empty after trimming; "Not Reported" = exact text, case-insensitive. '
        'The `N/A (...)` column counts other `N/A`-style placeholders for information only.\n')
    miss = []
    for c in EXPECTED_COLS:
        s = d[c].str.strip()
        blank = (s == '').mean() * 100
        nr = (s.str.lower() == NOT_REPORTED).mean() * 100
        na = s.str.match(r'(?i)^n/?a\b').mean() * 100
        miss.append(dict(column=c, blank_pct=f'{blank:.1f}', not_reported_pct=f'{nr:.1f}',
                         blank_or_not_reported_pct=f'{blank + nr:.1f}', n_a_style_pct=f'{na:.1f}'))
    say(md_table(pd.DataFrame(miss), index=False) + '\n')

    bn = d['Benchmark_Name']
    say('## Benchmark_Name variety\n')
    say(f'- unique raw values: **{bn.nunique()}**')
    say(f'- unique after lowercasing and removing non-alphanumerics: **{bn.map(norm).nunique()}** '
        f'(empty after normalising: {int((bn.map(norm) == "").sum())} rows)\n')

    # ---------------- d) report ----------------
    say('## Paper identity (paper_index.csv)\n')
    say(f'{len(idx)} papers. Flags: `title_under_multiple_source_files` (the same normalised title in one '
        f'Conference+Year appears under more than one Source_File), `source_file_has_multiple_titles` (one '
        f'Source_File within a Conference+Year carries more than one title), `untitled` (title missing). '
        f'Source_File scope is Conference+Year, because generic file names repeat across years.\n')
    fl = idx.assign(
        flagged=idx['flags'].str.contains('title_under|source_file_has'),
        title_multi_file=idx['flags'].str.contains('title_under'),
        file_multi_title=idx['flags'].str.contains('source_file_has'),
        untitled=idx['flags'].str.contains('untitled'))
    t = fl.groupby(['Conference', 'Year']).agg(papers=('paper_key', 'size'), flagged=('flagged', 'sum'),
                                               title_under_multiple_files=('title_multi_file', 'sum'),
                                               file_with_multiple_titles=('file_multi_title', 'sum'),
                                               untitled=('untitled', 'sum'))
    t = t[t['flagged'] + t['untitled'] > 0]
    say('Conference/Year combinations with at least one flag:\n')
    say(md_table(t) + '\n')
    say(f'Total flagged papers: **{int(fl.flagged.sum())}** of {len(idx)}; untitled: {int(fl.untitled.sum())}.\n')
    p23 = d[(d['Conference'] == 'PReMI') & (d['Year'] == '2023')]
    say(f'PReMI 2023: {len(p23)} rows, {p23["Source_File"].nunique()} Source_Files, '
        f'{p23.loc[~p23["_untitled"], "_nt"].nunique()} distinct titles, '
        f'{int(fl[(fl.Conference == "PReMI") & (fl.Year == "2023")].flagged.sum())} flagged papers.\n')

    # ---------------- e) PPSN ----------------
    say('## PPSN: one paper or a whole proceedings per file?\n')
    pp = d[d['Conference'] == 'PPSN']
    say(f'PPSN: {len(pp)} rows in {pp["Source_File"].nunique()} Source_Files.\n')
    for f, g in pp.groupby('Source_File', sort=True):
        titles = list(dict.fromkeys(g['Paper_Title']))
        roots = list(dict.fromkeys(g['Original_Paper_ID'].map(root_id)))
        say(f'### {f} (Year {", ".join(sorted(g["Year"].unique()))})\n')
        say(f'- rows: {len(g)}; distinct titles: {len(titles)}; distinct Original_Paper_ID roots: {len(roots)} '
            f'({", ".join(roots[:12])}{" …" if len(roots) > 12 else ""})')
        say(f'- distinct Authors values: {g["Authors"].nunique()} ({short(g["Authors"].iloc[0], 110)})')
        say('- sample titles:')
        for tt in titles[:5]:
            say(f'  - {short(tt, 110)}')
        ctx = list(dict.fromkeys(g['Problem_Context']))
        say(f'- extra evidence: distinct Problem_Context {len(ctx)}, Benchmark_Name {g["Benchmark_Name"].nunique()}, '
            f'Algorithm_Name {g["Algorithm_Name"].nunique()}; Problem_Context values: '
            f'{"; ".join(short(c, 70) for c in ctx[:5])}')
        say('')

    # ---------------- f) report-only checks ----------------
    say('## Report-only checks (nothing deleted)\n')
    ws = int((d['Winning_Strategy'] != d['Algorithm_Name']).sum())
    say(f'### Winning_Strategy != Algorithm_Name\n\nRows: **{ws}** (expected 0).\n')

    dup_extra = d.duplicated(REPEAT_KEY)
    dup_all = d.duplicated(REPEAT_KEY, keep=False)
    groups = d[dup_all].groupby(REPEAT_KEY, sort=False)
    compare = [c for c in EXPECTED_COLS if c not in REPEAT_KEY + ['Paper_ID', 'Original_Paper_ID']]
    differ_counts = {c: 0 for c in compare}
    identical_groups = 0
    group_info = []
    for key, g in groups:
        diffs = [c for c in compare if g[c].nunique() > 1]
        for c in diffs:
            differ_counts[c] += 1
        identical_groups += not diffs
        group_info.append((key, g, diffs))
    say('### Repeated title + Benchmark_Name + Algorithm_Name + Evaluation_Dataset\n')
    say(f'Exact (raw-value) repeats: **{int(dup_extra.sum())}** extra rows beyond the first, in '
        f'{len(group_info)} groups ({int(dup_all.sum())} rows including the first of each group). '
        f'Groups where every other column (except Paper_ID / Original_Paper_ID) is also identical: '
        f'**{identical_groups}**.\n')
    say('How many groups differ in each column:\n')
    dc = pd.DataFrame(sorted(differ_counts.items(), key=lambda x: -x[1]), columns=['column', 'groups_differing'])
    say(md_table(dc[dc.groups_differing > 0], index=False) + '\n')
    say('10 sample groups (random, seed 0):\n')
    sample = pd.Series(range(len(group_info))).sample(min(10, len(group_info)), random_state=0).tolist()
    for i in sample:
        key, g, diffs = group_info[i]
        say(f'- **{short(key[0], 80)}** | Benchmark `{short(key[1], 40)}` | Algorithm `{short(key[2], 40)}` | '
            f'Dataset `{short(key[3], 40)}`; {len(g)} rows; {", ".join(sorted(g["Conference"].unique()))} '
            f'{", ".join(sorted(g["Year"].unique()))}; Paper_IDs {", ".join(g["Paper_ID"])}')
        if not diffs:
            say('  - differs in: nothing (identical apart from IDs)')
        for c in diffs:
            vals = ' / '.join(short(v, 50) for v in dict.fromkeys(g[c]))
            say(f'  - differs in **{c}**: {vals}')
    say('')

    say('### Original_Paper_ID under more than one Conference or Year\n')
    for label, ser in [('full Original_Paper_ID', d['Original_Paper_ID']),
                       ('Original_Paper_ID root (without _Ext_NN)', d['Original_Paper_ID'].map(root_id))]:
        g = d.assign(_k=ser).groupby('_k').agg(conferences=('Conference', lambda s: ','.join(sorted(set(s)))),
                                               years=('Year', lambda s: ','.join(sorted(set(s)))),
                                               n_conf=('Conference', 'nunique'), n_year=('Year', 'nunique'),
                                               rows=('Paper_ID', 'size'))
        multi = g[(g.n_conf > 1) | (g.n_year > 1)].sort_values('rows', ascending=False)
        say(f'- {label}: **{len(multi)}** of {len(g)} values occur under more than one Conference or Year '
            f'({int((multi.n_conf > 1).sum())} across conferences).')
        if label.startswith('Original_Paper_ID root'):
            say('\n  Top 15 roots by rows:\n')
            say(md_table(multi.head(15)[['conferences', 'years', 'rows']].rename_axis('Original_Paper_ID root')) + '\n')
    say('Original_Paper_ID is a per-file extraction counter that restarts per source, so it is not a '
        'paper identifier; Paper_ID is used instead.\n')

    # ---------------- g) gold labels ----------------
    say('## Gold labels\n')
    if GOLD.exists() and OLD_MASTER.exists():
        raise SystemExit('gold_standard_labels.csv exists: remapping not implemented in this run')
    missing = [p.name for p in (GOLD, OLD_MASTER) if not p.exists()]
    say(f'Skipped: {", ".join(missing)} not found (searched the repo, backups and git history). '
        f'No `{GOLD_OUT.name}` written.\n')
    print(f'[1g] SKIPPED: {", ".join(missing)} not found')

    # ---------------- freeze ----------------
    shutil.copyfile(INPUT, FROZEN)
    assert FROZEN.read_bytes() == INPUT.read_bytes(), 'frozen copy differs'
    f2 = pd.read_csv(FROZEN, dtype=str, keep_default_na=False)
    assert f2.equals(pd.read_csv(INPUT, dtype=str, keep_default_na=False))
    say(f'## Frozen copy\n\n`{FROZEN.name}`: byte-identical to `{INPUT.name}` (verified).\n')
    print(f'[freeze] PASSED: {FROZEN.name} byte-identical to {INPUT.name}')

    REPORT.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'wrote {REPORT.name}, {INDEX.name}')


if __name__ == '__main__':
    sys.exit(main())
