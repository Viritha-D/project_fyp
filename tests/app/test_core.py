"""Unit tests: input validation, the data-only note builder, timeout path, downloads, hash and test-query guard."""
import time

import numpy as np
import pytest

import core


# ---------------- input validation
@pytest.mark.parametrize('text', [None, 42, b'bytes', ['a list']])
def test_rejects_non_text(text):
    ok, msg = core.validate_query(text)
    assert not ok and 'text' in msg.lower()


@pytest.mark.parametrize('text', ['', '   ', '\n\t'])
def test_rejects_empty(text):
    assert core.validate_query(text) == (False, 'Please describe your algorithm or problem.')


@pytest.mark.parametrize('text', ['12345 67890 ++ -- // ()', '!!! ??? ...'])
def test_rejects_no_words(text):
    ok, msg = core.validate_query(text)
    assert not ok and 'words' in msg


@pytest.mark.parametrize('text', ['TSP heuristic', 'my GA for scheduling', 'one two three four five'])
def test_short_input_asks_for_type_representation_objective(text):
    ok, msg = core.validate_query(text)
    assert not ok
    assert 'problem type' in msg and 'representation' in msg and 'objective' in msg


def test_six_words_pass():
    assert core.validate_query('a genetic algorithm for job shop scheduling') == (True, '')


def test_too_long():
    ok, msg = core.validate_query('word ' * 1000)
    assert not ok and str(core.MAX_CHARS) in msg


# ---------------- note builder (data only)
@pytest.fixture(scope='module')
def notes():
    return core.FamilyNotes()


def test_note_multi_paper_family(notes):
    n = notes.build_note('F00033')                       # DTLZ
    assert n['family_name'] == 'DTLZ' and n['n_papers'] == 45 and not n['single_paper']
    assert n['n_records'] == len(notes.rows_by_family['F00033'])
    assert n['years'] and n['years'][0] <= n['years'][1]
    assert abs(n['pure_math_share'] + n['applied_share'] - 1) < 1e-6
    assert 1 <= len(n['members']) <= 5
    assert n['evidence_papers'] == []                   # no query vector given
    for fld in core.NOTE_FIELDS:
        for v in n['common'][fld]:
            assert v and v.lower() not in core.MISSING


def test_note_values_come_from_the_data(notes):
    n = notes.build_note('F00033')
    rows = [r for _, r, _ in notes.rows_by_family['F00033']]
    for v in n['common']['Modality']:
        assert any(r['Modality'].strip() == v for r in rows)
    assert {str(y) for y in n['years']} <= {r['Year'] for r in rows}


def test_single_paper_caution(notes):
    fid = next(f for f, x in notes.fams.items() if x['n_papers'] == 1 and f in notes.rows_by_family)
    assert notes.build_note(fid)['single_paper']


def test_evidence_papers_by_cosine(notes):
    emb = np.load(core.ROOT / 'paper_embeddings.npy')
    i, r, pk = notes.rows_by_family['F00033'][0]
    n = notes.build_note('F00033', emb[i], emb)
    assert len(n['evidence_papers']) == 2
    assert n['evidence_papers'][0]['title'] == r['Paper_Title']          # the row's own paper is closest (cosine 1)
    assert n['evidence_papers'][0]['cosine'] >= n['evidence_papers'][1]['cosine']


def test_members_first_order(notes):
    fam = notes.fams['F00033']
    last = fam['member_entity_ids'][-1]
    n = notes.build_note('F00033', members_first=[last])
    assert n['members'][0] == notes.e2f[last]['canonical_name']


def test_note_lines_template(notes):
    lines = core.note_lines(notes.build_note('F00033'))
    assert lines[0].startswith('45 papers (') and 'Pure Math' in lines[0] and 'Applied' in lines[0]


def test_applied_share():
    a = {'paper_categories': {'p1': 'Applied', 'p2': 'Applied'}}
    b = {'paper_categories': {'p2': 'Applied', 'p3': 'Pure Math'}}
    assert core.applied_share_of_papers([a, b]) == pytest.approx(2 / 3)
    assert core.applied_share_of_papers([]) == 0.0


# ---------------- timeout path
def test_timeout_default_is_20_seconds():
    assert core.TIMEOUT_S == 20


def test_timeout_gives_friendly_error():
    t0 = time.perf_counter()
    res, err = core.run_with_timeout(time.sleep, 3, timeout=0.5)
    assert res is None and 'longer than 0.5 seconds' in err and 'try again' in err
    assert time.perf_counter() - t0 < 2.5


def test_exception_gives_friendly_error():
    res, err = core.run_with_timeout(lambda: 1 / 0)
    assert res is None and 'ZeroDivisionError' in err


def test_fast_call_passes():
    assert core.run_with_timeout(lambda x: x + 1, 1) == (2, None)


# ---------------- downloads, hash
def _result():
    note = {'n_papers': 3, 'evidence_papers': [{'title': 'T', 'conference': 'GECCO', 'year': '2020', 'cosine': 0.5}]}
    return {'query': 'q', 'tier': 'medium', 'timestamp': '2026-11-11T00:00:00+00:00', 'system_hash': 'abc',
            'families': [{'family_name': 'DTLZ', 'note': note}]}


def test_downloads_have_required_fields():
    c = core.to_csv(_result())
    assert c.splitlines()[0] == 'query,rank,family,n_papers,score_band,evidence_papers,timestamp,system_hash'
    assert c.splitlines()[1].split(',')[4] == '2'                                  # medium -> band 2
    m = core.to_markdown(_result())
    assert 'DTLZ' in m and 'Score band' in m and '2 of 3' in m and 'abc' in m and 'T (GECCO 2020)' in m
    assert 'medium' not in m


def test_frozen_hash_matches():
    actual, expected, ok = core.frozen_hash_status()
    assert ok and actual == expected and len(actual) == 64


# ---------------- held-out test-query guard
def test_guard_blocks_exact_test_query(monkeypatch):
    items = core.test_query_texts()
    assert {s for s, _, _ in items} >= {'queries_t1', 'queries_t3', 'queries_t4'}
    rng = np.random.default_rng(0)

    def fake_encode(xs):
        v = rng.normal(size=(len(xs), 8))
        return v / np.linalg.norm(v, axis=1, keepdims=True)
    g = core.TestQueryGuard(fake_encode)
    if not g.active:
        pytest.skip('independent test already reported; guard inactive')
    assert g.check('  ' + items[0][2].upper() + ' ')[0]           # exact after normalisation
