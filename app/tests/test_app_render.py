"""The page renders without errors in precomputed mode, validates input and does not run retrieval there."""
import json
import re

from streamlit.testing.v1 import AppTest

import core

APP_FILE = str(core.APP / 'streamlit_app.py')


def _run(text=None, click=False, mode='precomputed', monkeypatch=None):
    monkeypatch.setenv('DEMO_MODE', mode)
    at = AppTest.from_file(APP_FILE, default_timeout=60)
    at.run()
    if text is not None:
        at.text_area[0].input(text)
    if click:
        at.button[0].click()
    at.run()
    assert not at.exception, at.exception
    return at


def test_renders_gallery_and_footer(monkeypatch):
    at = _run(monkeypatch=monkeypatch)
    g = json.loads((core.APP / 'gallery.json').read_text())
    labels = [e.label for e in at.expander]
    assert any(l.startswith('How reliable') for l in labels)
    for item in g['items']:
        assert any(l.startswith(item['query_id']) for l in labels)
    assert any('sha256' in c.value for c in at.caption)


def test_short_input_prompt(monkeypatch):
    at = _run('TSP heuristic', click=True, monkeypatch=monkeypatch)
    assert any('representation' in w.value for w in at.warning)


def test_precomputed_mode_does_not_run_retrieval(monkeypatch):
    at = _run('a genetic algorithm for multi objective job shop scheduling', click=True, monkeypatch=monkeypatch)
    assert any('not available in the hosted demo' in w.value for w in at.warning)


def test_reliability_numbers_come_from_site_data(monkeypatch):
    site = json.loads((core.APP / 'site_data.json').read_text())
    src = (core.APP / 'streamlit_app.py').read_text()
    for t in ('low', 'medium', 'high'):
        assert f"{site['tiers_seed42'][t]['hit@1']}" not in src           # no hand-typed tier numbers in the UI
    assert '0.127' not in src and '0.475' not in src


def test_score_band_line_replaces_tier_words(monkeypatch):
    at = _run(monkeypatch=monkeypatch)
    lines = [m.value for m in at.markdown if m.value.startswith('**Score band (experimental, not validated on the independent test): ')]
    assert len(lines) == len(json.loads((core.APP / 'gallery.json').read_text())['items'])   # one line per answer
    assert all(re.search(r': [123]\*\* of 3 \(1 = top\)$', l) for l in lines)
    assert not any(c.value.startswith('Evidence tier') for c in at.caption)                # no per-card tier text
    assert not any(re.search(r'\b(high|medium|low)\b', l) for l in lines)
    assert not any('hit@1' in l for l in lines)


def test_banner_shows_both_evaluations():
    import importlib.util
    site = json.loads((core.APP / 'site_data.json').read_text())
    src = (core.APP / 'streamlit_app.py').read_text()
    assert 'Results depend on whether the problem has a named benchmark' in src
    g = site['independent_test']['stacked_hit@5_by_group']
    assert {round(v['stacked_hit@5'], 3) for v in g.values()} == {0.619, 0.429, 0.222}
    assert site['by_category_seed42']['Applied']['hit@5']['mean'] == 0.127
    assert site['by_category_seed42']['Pure Math']['hit@5']['mean'] == 0.475


def test_panel_reports_independent_test(monkeypatch):
    at = _run(monkeypatch=monkeypatch)
    text = ' '.join(m.value for m in at.markdown)
    assert 'The blend was chosen after seeing the test' in text
    assert 'SUPPORTED' in text
    assert any('recommend_v23.py' in c.value and 'matches FROZEN_HASHES_v23.txt' in c.value for c in at.caption)


def test_answer_shows_version_and_short_hash(monkeypatch):
    at = _run(monkeypatch=monkeypatch)
    h = core.frozen_hash_status()[0][:12]
    lines = [c.value for c in at.caption if c.value.startswith('Produced by v2.3 (blend 0.5)')]
    assert len(lines) == len(json.loads((core.APP / 'gallery.json').read_text())['items'])   # one per rendered answer
    assert all(h in l for l in lines)
