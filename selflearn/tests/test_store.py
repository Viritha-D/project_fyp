"""Store and verify CLI (sub-step 4.4)."""
import json

import pytest

from selflearn import verify
from selflearn.schema import empty_profile
from selflearn.store import ReadOnlyStore, Store, similar
from selflearn.trigger import decide


def prof(**kw):
    p = empty_profile()
    p.update(kw)
    return p


P = prof(objectives='multi', constraints='constrained', variable_type='continuous')
SHORT = [{'family_id': 'F1', 'family_name': 'One'}, {'family_id': 'F2', 'family_name': 'Two'}]


@pytest.fixture
def st(tmp_path):
    return Store(tmp_path / 'learned.jsonl')


def test_added_as_unverified_and_text_only_with_consent(st):
    r, why = st.add(P, SHORT, SHORT[0], query_text='secret query', consent=False)
    assert why is None and r['status'] == 'unverified' and r['query_text'] is None and r['consent'] is False
    r2, _ = st.add(prof(objectives='single', constraints='constrained'), SHORT, SHORT[1], query_text='kept', consent=True)
    assert r2['query_text'] == 'kept'


def test_duplicates_not_added(st):
    assert st.add(P, SHORT, SHORT[0])[0] is not None
    rec, why = st.add(P, SHORT, SHORT[0])
    assert rec is None and why == 'duplicate' and len(st.records()) == 1


def test_rejected_not_repeated(st):
    r, _ = st.add(P, SHORT, SHORT[0])
    st.set_status(r['id'], 'rejected', 'reviewer', 'not a constrained suite')
    similar_profile = prof(objectives='multi', constraints='constrained')       # similar, not identical
    assert 'F1' in st.rejected_for(similar_profile)
    rec, why = st.add(similar_profile, SHORT, SHORT[0])
    assert rec is None and 'rejected' in why
    assert 'F1' not in {c['family_id'] for c in st.candidates_for(similar_profile)}


def test_unverified_never_counts_as_evidence(st):
    r, _ = st.add(P, SHORT, SHORT[0])
    assert st.evidence_count(P) == 0                                            # unverified -> no evidence
    st.set_status(r['id'], 'verified', 'reviewer', 'checked against the paper')
    assert st.evidence_count(P) == 1


def test_confidence_ignores_the_store(st, monkeypatch):
    ranking = {'families': [{'family_id': 'F1', 'probability': 0.05}, {'family_id': 'F2', 'probability': 0.01}]}
    before = decide(ranking, P, {}, threshold=0.1)
    for i in range(5):
        st.add(prof(objectives='multi', constraints='constrained', modality='multimodal', dimensionality=i + 1),
               SHORT, SHORT[0])
    assert decide(ranking, P, {}, threshold=0.1) == before                      # store never consulted


def test_candidates_labelled_with_status(st):
    r, _ = st.add(P, SHORT, SHORT[0])
    c = st.candidates_for(prof(objectives='multi', constraints='constrained'))
    assert c == [{'family_id': 'F1', 'family_name': 'One', 'status': 'unverified', 'record_id': r['id']}]


def test_similarity_rule():
    assert similar(P, prof(objectives='multi', constraints='constrained'))
    assert not similar(P, prof(objectives='single', constraints='constrained'))      # disagreement
    assert not similar(P, prof(objectives='multi'))                                   # only 1 shared feature


def test_read_only_store_refuses_writes(tmp_path):
    ro = Store(tmp_path / 'x.jsonl', read_only=True)
    assert ro.add(P, SHORT, SHORT[0]) == (None, 'read-only store')
    with pytest.raises(ReadOnlyStore):
        ro._write_all([])


def test_verify_cli(st, monkeypatch, capsys):
    monkeypatch.setenv('SELFLEARN_STORE', str(st.path))
    r, _ = st.add(P, SHORT, SHORT[0])
    assert verify.main(['list']) == 0 and r['id'] in capsys.readouterr().out
    assert verify.main(['verify', r['id'], '--by', 'Darshan', '--how', 'read the paper']) == 0
    rec = json.loads(st.path.read_text().splitlines()[0])
    assert rec['status'] == 'verified' and rec['verified_by'] == 'Darshan' and rec['verified_at']
    capsys.readouterr()
    verify.main(['list'])
    assert capsys.readouterr().out.startswith('0 record(s)')                     # nothing left unverified
    with pytest.raises(SystemExit):
        verify.main(['reject', r['id']])                                        # --by and --how are required
