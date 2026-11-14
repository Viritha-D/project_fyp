"""Matcher (sub-step 4.2): a certain conflict removes a family; a conflict or an unknown lowers its score."""
from selflearn.matcher import BEST_LABEL, UNKNOWN_PENALTY, Matcher, compare, conflicts_with_all, feature_score
from selflearn.schema import empty_profile


def fam(fid, n_papers=1, dims=(), landscape=(), **counts):
    return {'family_id': fid, 'family_name': fid, 'n_papers': n_papers, 'counts': counts, 'dims': list(dims),
            'landscape': list(landscape), 'records': [], 'suite_memberships': [], 'member_entity_ids': []}


def q(**kw):
    p = empty_profile()
    p.update(kw)
    return p


def test_certain_conflict_removes_family():
    profiles = {'SO': fam('SO', objectives={'single': 12}), 'MO': fam('MO', objectives={'multi': 9})}
    out = Matcher(profiles).match(q(objectives='multi'))
    assert [r['family_id'] for r in out] == ['MO']              # single-objective benchmark removed for a MO problem


def test_non_unanimous_conflict_lowers_but_keeps():
    profiles = {'MIXED': fam('MIXED', objectives={'single': 8, 'multi': 2}), 'MO': fam('MO', objectives={'multi': 3})}
    out = Matcher(profiles).match(q(objectives='multi'))
    assert [r['family_id'] for r in out] == ['MO', 'MIXED']
    assert out[1]['conflicting'] == ['objectives'] and out[1]['score'] < out[0]['score']


def test_unknown_lowers_score():
    qp = q(constraints='constrained', variable_type='continuous')
    a = fam('A', constraints={'constrained': 4}, variable_type={'continuous': 4})
    b = fam('B', constraints={'constrained': 4})                 # variable type unknown for B
    m_a, c_a, u_a, _ = compare(qp, a)
    m_b, c_b, u_b, _ = compare(qp, b)
    assert u_b == ['variable_type'] and not c_b
    assert feature_score(qp, m_b, c_b, u_b) == (1 - UNKNOWN_PENALTY) / 2 < feature_score(qp, m_a, c_a, u_a) == 1.0


def test_conflict_lowers_more_than_unknown():
    qp = q(constraints='constrained')
    conflict = fam('C', constraints={'unconstrained': 5})
    unknown = fam('U')
    sc = feature_score(qp, *compare(qp, conflict)[:3])
    su = feature_score(qp, *compare(qp, unknown)[:3])
    assert sc == -1.0 and su == -UNKNOWN_PENALTY and sc < su


def test_dimensionality_and_landscape():
    qp = q(dimensionality=30, landscape=['noisy'])
    m, c, u, _ = compare(qp, fam('F', dims=[10, 50], landscape=['noisy']))
    assert 'dimensionality' in m and 'landscape:noisy' in m
    m, c, u, _ = compare(qp, fam('G', dims=[2]))
    assert 'dimensionality' in c and 'landscape:noisy' in u      # absent tag is unknown, not a conflict


def test_best_is_labelled_and_three_to_five_returned():
    profiles = {f'F{i}': fam(f'F{i}', constraints={'constrained': 1}) for i in range(8)}
    out = Matcher(profiles).match(q(constraints='constrained'))
    assert 3 <= len(out) <= 5 and out[0]['label'] == BEST_LABEL and all(r['label'] == '' for r in out[1:])
    for r in out:
        assert set(r) >= {'matched', 'conflicting', 'unknown', 'source'}


def test_excluded_ids_not_returned():
    profiles = {f'F{i}': fam(f'F{i}') for i in range(6)}
    out = Matcher(profiles).match(q(), exclude={'F0', 'F1'})
    assert not {'F0', 'F1'} & {r['family_id'] for r in out}


def test_conflicts_with_all():
    profiles = {'U1': fam('U1', constraints={'unconstrained': 3}), 'U2': fam('U2', constraints={'unconstrained': 9}),
                'C': fam('C', constraints={'constrained': 2})}
    qp = q(constraints='constrained')
    assert conflicts_with_all(qp, profiles, ['U1', 'U2'])
    assert not conflicts_with_all(qp, profiles, ['U1', 'C'])
    assert not conflicts_with_all(q(), profiles, ['U1', 'U2'])  # nothing stated -> no conflict trigger
