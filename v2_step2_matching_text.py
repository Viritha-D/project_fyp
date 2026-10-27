"""
v2 Step 2 - Part 2 (matching_text, language, matching_text_original, translated) on all rows
of papers_master_v2.csv -> papers_master_with_matching_text_v2.csv (29 columns + those 4).

Recipe: part2_matching_text.build_matching_text, unchanged.
    Applied  "<Problem_Context>. <Paper_Title>", title dropped when title_suspect or missing
    other    "<Benchmark_Name>. <Target_Landscape>. <Landscape_Characteristics>"

title_suspect: the same rule ingest.py writes to ingest_log.csv, applied per Conference
(one Conference = one ingest run): the normalised title appears under >= 3 different
Source_Files whose authors differ, or the title has fewer than 3 words, or it is missing.

Language: safe_detect (langdetect): 'en' if the text is under 25 characters, has no
non-ASCII character, the top language is 'en', or its probability is under 0.90.
Translations: when the same source text exists in the old master
(backup_v2/papers_master_with_matching_text.csv, column matching_text_original), its
matching_text and translated are reused (language = the detected source code for
translated rows). Remaining non-English rows are
translated from TRANSLATIONS below; any without one stay translated=False and are listed
in needs_translation.csv.

Usage:  PYTHONPATH=<dir containing langdetect> python v2_step2_matching_text.py
"""

import re
import sys
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, detect_langs

import part2_matching_text as p2
from ingest import SUSPECT_MIN_SOURCES, SUSPECT_MIN_WORDS, word_count

DetectorFactory.seed = 0

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'papers_master_v2.csv'
OLD_MASTER = ROOT / 'backup_v2' / 'papers_master_with_matching_text.csv'
OUTPUT = ROOT / 'papers_master_with_matching_text_v2.csv'
NEEDS_TRANSLATION = ROOT / 'needs_translation.csv'
NEEDS_REVIEW = ROOT / 'needs_manual_review_empty_text.csv'
PART2_COLS = ['matching_text', 'language', 'matching_text_original', 'translated']
MIN_ALNUM = 3

# English translations for non-English source texts not found in the old master.
TRANSLATIONS = {}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def safe_detect(text):
    if len(text) < 25 or text.isascii():
        return 'en'
    try:
        top = detect_langs(text)[0]
    except Exception:
        return 'en'
    return 'en' if top.lang == 'en' or top.prob < 0.90 else top.lang


def title_suspect_flags(d):
    untitled = d['Paper_Title'].str.strip().isin(p2.MISSING) | (d['Paper_Title'].map(norm) == '')
    nt = d['Paper_Title'].map(norm)
    na = d['Authors'].map(lambda a: '' if a.strip() in p2.MISSING else norm(a))
    ns = d['Source_File'].map(norm)
    g = pd.DataFrame({'c': d['Conference'], 'nt': nt, 'ns': ns, 'na': na})[~untitled]
    stats = g.groupby(['c', 'nt']).agg(n_src=('ns', 'nunique'), n_auth=('na', 'nunique'))
    spread_keys = set(stats[(stats.n_src >= SUSPECT_MIN_SOURCES) & (stats.n_auth > 1)].index)
    spread = pd.Series([(c, t) in spread_keys for c, t in zip(d['Conference'], nt)], index=d.index) & ~untitled
    short = ~untitled & (d['Paper_Title'].map(word_count) < SUSPECT_MIN_WORDS)
    return untitled | spread | short, dict(untitled=int(untitled.sum()), spread=int(spread.sum()),
                                          short=int(short.sum()))


def main():
    d = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    cols29 = list(d.columns)
    assert len(d) == 11342 and len(cols29) == 29, d.shape

    suspect, parts = title_suspect_flags(d)
    applied = d['Category'] == p2.APPLIED
    print(f'title_suspect rows: {int(suspect.sum())} (untitled {parts["untitled"]}, title under '
          f'>={SUSPECT_MIN_SOURCES} files with differing authors {parts["spread"]}, '
          f'<{SUSPECT_MIN_WORDS} words {parts["short"]}); Applied rows affected: {int((suspect & applied).sum())}')

    original = pd.Series([p2.build_matching_text(r, s) for (_, r), s in zip(d.iterrows(), suspect)], index=d.index)

    bad = original.map(lambda t: len(re.findall(r'[A-Za-z0-9]', t)) < MIN_ALNUM)
    if bad.any():
        d.loc[bad, ['Paper_ID', 'Conference', 'Category', 'Source_File']].to_csv(NEEDS_REVIEW, index=False)
        raise SystemExit(f'STOP: {int(bad.sum())} rows with fewer than {MIN_ALNUM} alphanumeric characters; '
                         f'listed in {NEEDS_REVIEW.name}')

    old = pd.read_csv(OLD_MASTER, dtype=str, keep_default_na=False)
    old_map = {}
    for o, t, lang, tr in zip(old['matching_text_original'], old['matching_text'], old['language'], old['translated']):
        old_map.setdefault(o, (t, lang, tr))

    text, language, translated, source = [], [], [], []
    needs = []
    for i, o in original.items():
        if o in old_map:
            t, lang, tr = old_map[o]
            if tr == 'True':
                lang = safe_detect(o)   # the old master stored 'en' after translating; keep the source code
            text.append(t), language.append(lang), translated.append(tr)
            source.append('old_master_translation' if tr == 'True' else 'old_master')
            continue
        lang = safe_detect(o)
        if lang == 'en':
            text.append(o), language.append('en'), translated.append('False'), source.append('new_en')
        elif o in TRANSLATIONS:
            text.append(TRANSLATIONS[o]), language.append(lang), translated.append('True'), source.append('new_translated')
        else:
            text.append(o), language.append(lang), translated.append('False'), source.append('needs_translation')
            needs.append(i)

    out = d.copy()
    out['matching_text'] = text
    out['language'] = language
    out['matching_text_original'] = original.values
    out['translated'] = translated

    # ---------------- assertions ----------------
    assert list(out.columns) == cols29 + PART2_COLS, list(out.columns)
    assert len(out) == len(d) and out['Paper_ID'].equals(d['Paper_ID'])
    assert out[cols29].equals(d), 'master columns changed'
    alnum = out['matching_text'].map(lambda t: len(re.findall(r'[A-Za-z0-9]', t)))
    assert (alnum >= MIN_ALNUM).all(), 'empty matching_text'
    print(f'[2] PASSED: {len(out)} rows, {len(out.columns)} columns (29 + 4), matching_text has >= '
          f'{MIN_ALNUM} alphanumeric characters on every row, master columns unchanged')

    if needs:
        d.loc[needs, ['Paper_ID', 'Conference', 'Category']].assign(
            matching_text_original=original[needs], language=[language[i] for i in needs]
        ).to_csv(NEEDS_TRANSLATION, index=False)
        print(f'{len(needs)} rows need translation -> {NEEDS_TRANSLATION.name}')
    elif NEEDS_TRANSLATION.exists():
        NEEDS_TRANSLATION.unlink()

    out.to_csv(OUTPUT, index=False, lineterminator='\n')
    back = pd.read_csv(OUTPUT, dtype=str, keep_default_na=False)
    assert back.equals(out), 'written file does not read back identically'

    src = pd.Series(source, index=d.index)
    print(f'wrote {OUTPUT.name}')
    print('\nrows by Conference:')
    print(out['Conference'].value_counts().sort_index().to_string())
    print(f'\ntranslated=True: {int((out["translated"] == "True").sum())}; '
          f'source of the text: {src.value_counts().to_dict()}')
    lens = out['matching_text'].str.len()
    print(f'matching_text length: min {lens.min()}, median {int(lens.median())}, max {lens.max()}')

    print('\n10 samples (3 Pure Math, 3 Applied, 2 PReMI, 2 FOGA; random, seed 0):')
    picks = [('Pure Math', out[out['Category'] == 'Pure Math'], 3),
             ('Applied', out[out['Category'] == 'Applied'], 3),
             ('PReMI', out[out['Conference'] == 'PReMI'], 2),
             ('FOGA', out[out['Conference'] == 'FOGA'], 2)]
    for label, g, k in picks:
        for _, r in g.sample(k, random_state=0).iterrows():
            print(f'  [{label}] {r.Paper_ID} ({r.Conference} {r.Year}, {r.Category}): {r.matching_text!r}')


if __name__ == '__main__':
    sys.exit(main())
