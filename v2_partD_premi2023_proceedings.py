"""
v2 Part D - check PReMI titles against the PReMI 2023 proceedings PDF (read-only).

The proceedings (Springer LNCS 14301, "2023-fyp.pdf", stored in Git LFS on main) has one
top-level bookmark per paper. For each bookmark this script takes the title, the page
range and the author line printed under the title on the first page, then matches every
PReMI title in papers_master_v2.csv against that list:
    exact         normalised titles equal
    running_head  equals one of the paper's running-head candidates (lines repeated across
                  its pages, which include the short title Springer prints on odd pages)
    prefix     one normalised title starts with the other (truncated / added subtitle)
    fuzzy      difflib ratio >= 0.90 on normalised titles
    none       no match
Authors are compared by surname overlap (at least one surname in common).

Outputs:
    premi2023_proceedings_toc.csv     one row per paper in the proceedings
    premi2023_proceedings_check.csv   one row per PReMI paper_key in the master
Usage:
    python v2_partD_premi2023_proceedings.py --pdf <path to 2023-fyp.pdf>
"""

import argparse
import difflib
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / 'papers_master_v2.csv'
INDEX = ROOT / 'paper_index.csv'
TOC_OUT = ROOT / 'premi2023_proceedings_toc.csv'
CHECK_OUT = ROOT / 'premi2023_proceedings_check.csv'
SECTION_HEADINGS = {'foreword', 'preface', 'messagefromthehonorarychair', 'organization', 'authorindex',
                    'abstractsofkeynoteinvitedandspecialtalks'}
FUZZY = 0.90


def norm(s):
    s = unicodedata.normalize('NFKC', str(s))
    return re.sub(r'[^a-z0-9]', '', s.lower())


def surnames(authors):
    out = set()
    for a in re.split(r';|,|\band\b', unicodedata.normalize('NFKC', str(authors))):
        words = re.findall(r'[A-Za-zÀ-ÿ\-]+', a)
        words = [w for w in words if len(w) > 1 and w.lower() not in {'et', 'al'}]
        if words:
            out.add(words[-1].lower())
    return out


def all_pages(pdf):
    """Text of every page (index 0 = page 1), from one pdftotext run."""
    text = subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    return text.split('\f')


def running_heads(pages, start, end, keep=5):
    """Candidate running heads: lines repeated on at least 2 of the paper's later pages
    (counted once per page), most frequent first, excluding page numbers, 'Author et al.'
    heads and section words. pdftotext does not always put the head first on the page, so
    the whole page is searched; the even-page author line may also appear, which is
    harmless because it never equals a paper title."""
    counts, first = {}, {}
    for pg in range(start + 1, end + 1):
        lines = [unicodedata.normalize('NFKC', l).strip() for l in pages[pg - 1].splitlines() if l.strip()]
        for pos, l in enumerate(dict.fromkeys(lines)):
            if (re.fullmatch(r'[\divxlc]+', l.lower()) or re.search(r'(?i)\bet al\.?$', l) or len(norm(l)) < 10
                    or norm(l) in {'references', 'acknowledgements', 'acknowledgments'}):
                continue
            counts[l] = counts.get(l, 0) + 1
            first[l] = min(first.get(l, pos), pos)
    ranked = sorted((l for l in counts if counts[l] >= 2), key=lambda l: (-counts[l], first[l]))
    return ranked[:keep]


def author_line(text, title):
    """Text printed between the title and the first affiliation line on a paper's first page."""
    lines = [unicodedata.normalize('NFKC', l).strip() for l in text.splitlines()]
    lines = [l for l in lines if l]
    nt, acc, i = norm(title), '', 0
    while i < len(lines) and len(acc) < len(nt):   # skip the title lines
        acc += norm(lines[i])
        i += 1
    names = []
    for l in lines[i:]:
        if re.match(r'^\d', l) or re.search(r'(?i)universit|institut|department|college|school|laborator|centre|center|@', l):
            break
        names.append(l)
    s = ' '.join(names)
    s = re.sub(r'\(B\)|\s*\d+(,\d+)*(\(B\))?', '', s)   # footnote digits, corresponding-author marks
    return re.sub(r'\s+', ' ', s).strip(' ,')


def build_toc(pdf):
    r = PdfReader(str(pdf))
    entries = []

    def walk(items, depth):
        for x in items:
            if isinstance(x, list):
                walk(x, depth + 1)
            else:
                entries.append((depth, x.title.replace('\xa0', ' ').strip(), r.get_destination_page_number(x) + 1))
    walk(r.outline, 0)
    # a paper is a top-level entry whose next entry is a child section
    papers = []
    for k, (depth, title, page) in enumerate(entries):
        if depth != 0 or norm(title) in SECTION_HEADINGS:
            continue
        nxt = entries[k + 1] if k + 1 < len(entries) else None
        if nxt and nxt[0] == 1:
            papers.append(dict(title=title, start_page=page))
    pages = all_pages(pdf)
    starts = [p['start_page'] for p in papers] + [len(r.pages) + 1]
    for i, p in enumerate(papers):
        p['end_page'] = starts[i + 1] - 1
        p['authors_on_first_page'] = author_line(pages[p['start_page'] - 1], p['title'])
        p['running_heads'] = ' || '.join(running_heads(pages, p['start_page'], p['end_page']))
    return pd.DataFrame(papers)


def match(title, toc_norm, head_norm):
    nt = norm(title)
    if nt in toc_norm:
        return 'exact', toc_norm[nt], 1.0
    if nt in head_norm:
        return 'running_head', head_norm[nt], 1.0
    for k, i in toc_norm.items():
        if len(nt) >= 15 and (k.startswith(nt) or nt.startswith(k)):
            return 'prefix', i, round(difflib.SequenceMatcher(None, nt, k).ratio(), 3)
    best = max(toc_norm, key=lambda k: difflib.SequenceMatcher(None, nt, k).ratio())
    ratio = difflib.SequenceMatcher(None, nt, best).ratio()
    if ratio >= FUZZY:
        return 'fuzzy', toc_norm[best], round(ratio, 3)
    return 'none', toc_norm[best], round(ratio, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', required=True, type=Path)
    args = ap.parse_args()

    toc = build_toc(args.pdf)
    assert len(toc) > 0, 'no papers found in the outline'
    toc.to_csv(TOC_OUT, index=False)
    print(f'proceedings: {len(toc)} papers (pages {toc.start_page.min()}-{toc.end_page.max()}); wrote {TOC_OUT.name}')
    toc_norm = {norm(t): i for i, t in toc['title'].items()}
    head_norm = {}
    for i, hs in toc['running_heads'].items():
        for h in filter(None, hs.split(' || ')):
            head_norm.setdefault(norm(h), i)
    print(f'running-head candidates found for {int((toc["running_heads"] != "").sum())} of {len(toc)} papers')

    d = pd.read_csv(MASTER, dtype=str, keep_default_na=False)
    idx = pd.read_csv(INDEX, dtype=str, keep_default_na=False)
    pi = idx[idx['Conference'] == 'PReMI'].copy()
    authors = d[d['Conference'] == 'PReMI'].assign(
        paper_key=lambda x: x['Conference'] + '|' + x['Year'] + '|' + x['Paper_Title'].map(norm)
    ).groupby('paper_key')['Authors'].first()

    rows = []
    for _, p in pi.iterrows():
        if 'untitled' in p['flags']:
            rows.append(dict(paper_key=p['paper_key'], Year=p['Year'], Source_Files=p['Source_Files'], title=p['title'],
                             master_authors='', match='untitled', ratio='', toc_title='', toc_pages='',
                             toc_authors='', author_overlap=''))
            continue
        kind, i, ratio = match(p['title'], toc_norm, head_norm)
        t = toc.loc[i]
        ma = authors.get(p['paper_key'], '')
        overlap = sorted(surnames(ma) & surnames(t['authors_on_first_page']))
        rows.append(dict(paper_key=p['paper_key'], Year=p['Year'], Source_Files=p['Source_Files'], title=p['title'],
                         master_authors=ma, match=kind, ratio=ratio,
                         toc_title=t['title'] if kind != 'none' else '',
                         toc_pages=f'{t.start_page}-{t.end_page}' if kind != 'none' else '',
                         toc_authors=t['authors_on_first_page'] if kind != 'none' else '',
                         author_overlap=';'.join(overlap) if kind != 'none' else ''))
    chk = pd.DataFrame(rows)
    chk.to_csv(CHECK_OUT, index=False)

    p23 = chk[chk['Year'] == '2023']
    print(f'\nPReMI 2023 paper_keys in the master: {len(p23)}; match against the proceedings: '
          f'{p23["match"].value_counts().to_dict()}')
    m = p23[p23['match'].isin(['exact', 'running_head', 'prefix', 'fuzzy'])]
    print(f'  matched with at least one shared author surname: {int((m["author_overlap"] != "").sum())} of {len(m)}')
    print(f'  distinct proceedings papers matched: {m["toc_title"].nunique()} of {len(toc)}')
    other = chk[(chk['Year'] != '2023') & chk['match'].isin(['exact', 'running_head', 'prefix', 'fuzzy'])]
    print(f'PReMI papers labelled with another Year whose title is in the 2023 proceedings: {len(other)}'
          + (f' -> years {other["Year"].value_counts().sort_index().to_dict()}' if len(other) else ''))
    print(f'wrote {CHECK_OUT.name} ({len(chk)} PReMI paper_keys)')


if __name__ == '__main__':
    sys.exit(main())
