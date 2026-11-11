"""
Shared logic of the benchmark-recommender demo. The frozen retrieval system (retrieval_v2, tag retrieval-v2.2) is
only imported and called, never changed; every ranking shown comes from recommend_v21.recommend_v21 with its default
settings (lambda 1.0).

- validate_query: input rules.
- frozen_hash_status: sha256 of retrieval_v2/recommend_v21.py against FROZEN_HASHES.txt (shown in the footer).
- FamilyNotes / build_note: data-only notes from the repository files; no generated text.
- run_with_timeout: live calls with a 20-second limit and a friendly error.
- TestQueryGuard: refuses live queries that match a held-out test query (exact or dense cosine >= 0.8) until the
  independent test is reported in RESULTS.md.
- to_csv / to_markdown: downloads.
"""

import concurrent.futures
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = Path(__file__).resolve().parent
FROZEN_FILE = 'retrieval_v2/recommend_v21.py'
MIN_WORDS = 6
MAX_CHARS = 2000
TIMEOUT_S = 20
SIM_LIMIT = 0.8
MISSING = {'', 'not reported', 'n/a', 'na', 'none', 'unknown', 'n/a (pure math problem)', 'none / pure synthetic', 'nan'}
NOTE_FIELDS = ['Problem_Context', 'Landscape_Characteristics', 'Dimensionality', 'Modality', 'Separability']


# ---------------------------------------------------------------- input
def validate_query(text):
    """Returns (ok, message). ok is False for empty, non-text or too-short input; message says what to add."""
    if not isinstance(text, str):
        return False, 'Please type a text description.'
    t = text.strip()
    if not t:
        return False, 'Please describe your algorithm or problem.'
    if len(t) > MAX_CHARS:
        return False, f'Please keep the description under {MAX_CHARS} characters.'
    if not re.search(r'[A-Za-z]{2,}', t):
        return False, 'Please describe the problem in words.'
    if len(re.findall(r'[A-Za-z0-9][A-Za-z0-9+\-/().]*', t)) < MIN_WORDS:
        return False, ('Please add a little more: the problem type (e.g. continuous, combinatorial, multi-objective), '
                       'the representation (e.g. real vector, permutation, bit string, tree) or the objective.')
    return True, ''


# ---------------------------------------------------------------- frozen system hash
def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frozen_hash_status():
    """(hash of retrieval_v2/recommend_v21.py, expected hash from FROZEN_HASHES.txt, ok)."""
    expected = None
    for line in (ROOT / 'retrieval_v2/evaluation/FROZEN_HASHES.txt').read_text(encoding='utf-8').splitlines():
        if not line.startswith('#') and line.strip().endswith('  ' + FROZEN_FILE):
            expected = line.split()[0]
    actual = sha256_file(ROOT / FROZEN_FILE)
    return actual, expected, expected is not None and actual == expected


# ---------------------------------------------------------------- notes (data only)
def _clean(v):
    v = str(v).strip()
    return '' if v.lower() in MISSING else v


def _common(values, k=2):
    c = Counter(v for v in values if v)
    return [v for v, _ in c.most_common(k)]


class FamilyNotes:
    """Per-family facts from papers_master_with_matching_text_v2.csv, paper_to_entity_map_v2.csv,
    entity_to_family_v5.csv and families_v5.json (read once)."""

    def __init__(self, root=ROOT):
        rows = list(csv.DictReader(open(root / 'papers_master_with_matching_text_v2.csv', encoding='utf-8')))
        emap = list(csv.DictReader(open(root / 'paper_to_entity_map_v2.csv', encoding='utf-8')))
        assert [r['paper_id'] for r in emap] == [r['Paper_ID'] for r in rows]
        e2f = {r['entity_id']: r for r in csv.DictReader(open(root / 'entity_to_family_v5.csv', encoding='utf-8'))}
        self.fams = {f['family_id']: f for f in json.loads((root / 'families_v5.json').read_text(encoding='utf-8'))}
        self.e2f = e2f
        self.rows_by_family = {}
        for i, (r, m) in enumerate(zip(rows, emap)):
            f = e2f[m['entity_id']]['family_id']
            self.rows_by_family.setdefault(f, []).append((i, r, m['paper_key']))

    def build_note(self, family_id, query_vec=None, paper_emb=None, members_first=()):
        """All facts come from repository data. query_vec / paper_emb (L2-normalised) give the two closest
        evidence papers by dense cosine; without them the evidence papers are left out."""
        fam = self.fams[family_id]
        rows = self.rows_by_family.get(family_id, [])
        papers = {}
        for i, r, pk in rows:
            papers.setdefault(pk, []).append((i, r))
        years = sorted({int(r['Year']) for _, r, _ in rows if str(r['Year']).isdigit()})
        cats = Counter(r['Category'] for _, r, _ in rows)
        total = sum(cats.values()) or 1
        common = {}
        for fld in NOTE_FIELDS:
            vals = []
            for _, r, _ in rows:
                if fld == 'Landscape_Characteristics':
                    vals += [_clean(x) for x in str(r[fld]).split(';')]
                else:
                    vals.append(_clean(r[fld]))
            common[fld] = _common(vals)
        evidence = []
        if query_vec is not None and paper_emb is not None and papers:
            scored = []
            for pk, prs in papers.items():
                best = max(prs, key=lambda x: float(paper_emb[x[0]] @ query_vec))
                scored.append((float(paper_emb[best[0]] @ query_vec), pk, best[1]))
            scored.sort(key=lambda x: (-x[0], x[1]))
            evidence = [{'title': r['Paper_Title'], 'conference': r['Conference'], 'year': r['Year'], 'cosine': round(s, 3)}
                        for s, _, r in scored[:2]]
        member_ids = list(dict.fromkeys(list(members_first) + sorted(
            fam['member_entity_ids'], key=lambda e: (-int(self.e2f[e]['n_papers']), e))))
        members = [self.e2f[e]['canonical_name'] for e in member_ids if e in self.e2f][:5]
        return {'family_id': family_id, 'family_name': fam['family_name'], 'n_papers': fam['n_papers'],
                'n_records': len(rows), 'years': [years[0], years[-1]] if years else [],
                'pure_math_share': round(cats.get('Pure Math', 0) / total, 3),
                'applied_share': round(cats.get('Applied', 0) / total, 3),
                'common': common, 'evidence_papers': evidence, 'members': members,
                'single_paper': fam['n_papers'] < 2,
                'paper_categories': {pk: Counter(r['Category'] for _, r in prs).most_common(1)[0][0] for pk, prs in papers.items()}}


def note_lines(note):
    """Fixed-template text for one card (no generated text)."""
    yrs = f"{note['years'][0]}–{note['years'][1]}" if note['years'] and note['years'][0] != note['years'][1] else (
        str(note['years'][0]) if note['years'] else 'year not reported')
    lines = [f"{note['n_papers']} paper{'s' if note['n_papers'] != 1 else ''} ({note['n_records']} records), {yrs}; "
             f"Pure Math {note['pure_math_share']:.0%} / Applied {note['applied_share']:.0%}."]
    labels = {'Problem_Context': 'Problem context', 'Landscape_Characteristics': 'Landscape', 'Dimensionality': 'Dimensionality',
              'Modality': 'Modality', 'Separability': 'Separability'}
    for fld, lab in labels.items():
        if note['common'].get(fld):
            lines.append(f"{lab}: {'; '.join(note['common'][fld])}")
    return lines


def applied_share_of_papers(notes):
    """Share of the distinct papers behind the given families whose records there are mostly Applied."""
    cats = {}
    for n in notes:
        cats.update(n['paper_categories'])
    return (sum(c == 'Applied' for c in cats.values()) / len(cats)) if cats else 0.0


# ---------------------------------------------------------------- live calls
def run_with_timeout(fn, *args, timeout=TIMEOUT_S, **kwargs):
    """Runs fn in a worker thread. Returns (result, None) or (None, friendly error message)."""
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    fut = ex.submit(fn, *args, **kwargs)
    try:
        return fut.result(timeout=timeout), None
    except concurrent.futures.TimeoutError:
        return None, (f'This took longer than {timeout} seconds, so it was stopped. The first query after start-up '
                      'loads the models; please try again in a moment.')
    except Exception as e:  # noqa: BLE001
        return None, f'Something went wrong while ranking ({type(e).__name__}). Please try again.'
    finally:
        ex.shutdown(wait=False, cancel_futures=True)


# ---------------------------------------------------------------- held-out test queries
def norm_text(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(s)).casefold()).strip()


def test_query_texts(root=ROOT):
    """Query texts of every held-out test file (t1..t5, t2b), from CSV where present, else from the xlsx / docx."""
    ev = root / 'retrieval_v2/evaluation'
    out = []
    for p in sorted(ev.glob('queries_t*')):
        stem = p.stem.replace('_original', '')
        if p.suffix == '.csv' and not p.stem.endswith('_resolved'):
            out += [(stem, r['query_id'], r['query_text']) for r in csv.DictReader(open(p, encoding='utf-8'))]
        elif p.suffix in ('.xlsx', '.docx') and not (ev / f'{stem}.csv').exists():
            out += _read_table(p, stem)
    return out


def _read_table(p, stem):
    rows = []
    if p.suffix == '.xlsx':
        import openpyxl
        ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]
        rows = [['' if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
    else:
        import docx
        rows = [[c.text for c in r.cells] for r in docx.Document(p).tables[0].rows]
    head = rows[0]
    i, t = head.index('query_id'), head.index('query_text')
    return [(stem, r[i], r[t]) for r in rows[1:] if any(c.strip() for c in r)]


def independent_test_reported(root=ROOT):
    return bool(re.search(r'^#+\s*Independent test', (root / 'retrieval_v2/RESULTS.md').read_text(encoding='utf-8'), re.M))


class TestQueryGuard:
    """Blocks live queries that match a held-out test query until the independent test is in RESULTS.md."""

    def __init__(self, encode, root=ROOT):
        self.active = not independent_test_reported(root)
        self.items = test_query_texts(root) if self.active else []
        self.exact = {norm_text(t) for _, _, t in self.items}
        self.vecs = encode([t for _, _, t in self.items]) if self.items else None
        self.encode = encode

    def check(self, text):
        """(blocked, max_cosine)."""
        if not self.active or not self.items:
            return False, 0.0
        if norm_text(text) in self.exact:
            return True, 1.0
        c = float((self.vecs @ self.encode([text])[0]).max())
        return c >= SIM_LIMIT, c


# ---------------------------------------------------------------- downloads
def to_rows(result):
    ts = result['timestamp']
    out = []
    for i, f in enumerate(result['families'], 1):
        ev = '; '.join(f"{p['title']} ({p['conference']} {p['year']})" for p in f['note']['evidence_papers'])
        out.append({'query': result['query'], 'rank': i, 'family': f['family_name'], 'n_papers': f['note']['n_papers'],
                    'tier': result['tier'], 'evidence_papers': ev, 'timestamp': ts, 'system_hash': result['system_hash']})
    return out


def to_csv(result):
    buf = io.StringIO()
    rows = to_rows(result)
    w = csv.DictWriter(buf, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def to_markdown(result):
    L = [f"# Benchmark recommendation", '', f"**Query:** {result['query']}", '',
         f"**Evidence tier:** {result['tier']} · **Generated:** {result['timestamp']} · **System:** recommend_v21.py "
         f"sha256 `{result['system_hash']}`", '', '| rank | family | papers | evidence papers |', '|---|---|---|---|']
    for r in to_rows(result):
        L.append(f"| {r['rank']} | {r['family']} | {r['n_papers']} | {r['evidence_papers'] or '-'} |")
    return '\n'.join(L) + '\n'


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')
