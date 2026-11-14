"""End to end: live mode (v2.3 = blend 0.5) on the six gallery queries reproduces the recorded blend 0.5 top 5 on
queries_v2 (v22/results_v22_queries_v2.csv, 'blend lambda=0.5') and the precomputed gallery. Needs the live
environment (FROZEN_ENV.txt)."""
import csv
import json

import pytest

import core

pytest.importorskip('sentence_transformers')


@pytest.fixture(scope='module')
def recorded():
    rows = csv.DictReader(open(core.ROOT / 'retrieval_v2/v22/results_v22_queries_v2.csv', encoding='utf-8'))
    return {r['key']: r['top5'].split(';') for r in rows if r['system'] == 'blend lambda=0.5'}


@pytest.fixture(scope='module')
def gallery():
    return json.loads((core.APP / 'gallery.json').read_text(encoding='utf-8'))


def test_gallery_rule_is_fixed(gallery):
    assert [i['query_id'] for i in gallery['items']] == ['Q01', 'Q11', 'Q21', 'Q31', 'Q41', 'Q51']
    assert gallery['label'] == 'development set; lambda was selected on it'
    assert gallery['system'] == 'v2.3 = blend 0.5'
    assert gallery['system_hash'] == core.frozen_hash_status()[0]


@pytest.mark.parametrize('qid', ['Q01', 'Q11', 'Q21', 'Q31', 'Q41', 'Q51'])
def test_live_top5_equals_recorded(qid, recorded, gallery):
    import live
    item = next(i for i in gallery['items'] if i['query_id'] == qid)
    res = live.recommend(item['query_text'], write=False)
    top5 = [f['family_id'] for f in res['families']]
    assert top5 == recorded[qid]
    assert top5 == [f['family_id'] for f in item['result']['families']]
    assert res['tier'] == item['result']['tier']
    assert item['hit'] == any(g in top5 for g in item['gold_ids'])


def test_out_of_scope_gives_message_no_shortlist_no_store():
    import live
    store = core.ROOT / 'selflearn' / 'store' / 'learned.jsonl'
    before = store.read_bytes() if store.exists() else None
    res = live.recommend('Please give me a recipe for chocolate chip cookies that stay soft for several days.')
    assert res['status'] == 'out_of_scope' and res['message'] == 'this does not look like an optimisation problem'
    assert res['families'] == [] and res['selflearn']['shortlist'] == []
    assert (store.read_bytes() if store.exists() else None) == before


def test_unverified_tag_shown_for_earlier_suggestion(tmp_path, monkeypatch):
    """A stored unverified suggestion appears for a later similar query, labelled unverified."""
    import live
    from selflearn.store import Store
    s = live.load()
    tmp = Store(tmp_path / 'learned.jsonl')
    monkeypatch.setattr(s['fb'], 'store', tmp)
    g = json.loads((core.APP / 'gallery.json').read_text(encoding='utf-8'))
    q = next(i['query_text'] for i in g['items'] if i['result'].get('status') == 'fallback')
    first = live.recommend(q)
    if first['status'] != 'fallback':
        pytest.skip('this query is not below the threshold')
    assert tmp.records() and tmp.records()[0]['status'] == 'unverified'
    second = live.recommend(q + ' please', write=False)
    tags = [c['status'] for c in second['selflearn'].get('earlier_suggestions', [])]
    assert 'unverified' in tags
