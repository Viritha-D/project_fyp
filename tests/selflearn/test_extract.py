"""Schema and rule-based extractor (sub-step 4.1)."""
import pytest

from selflearn.extract import extract, extract_rules, in_scope
from selflearn.schema import UNKNOWN, empty_profile, known, validate


def test_unknown_stays_unknown():
    p = extract('I need some help with my project, please suggest something.')
    assert known(p) == {}
    assert all(v == UNKNOWN for k, v in p.items() if k != 'landscape') and p['landscape'] == []


def test_partial_text_only_fills_what_is_stated():
    p = extract('a genetic algorithm for a multi-objective problem')
    assert p['objectives'] == 'multi'
    for k in ('constraints', 'separability', 'modality', 'dimensionality', 'variable_type'):
        assert p[k] == UNKNOWN, k                                 # not stated -> unknown, never guessed


def test_constrained_continuous():
    p = extract('Differential evolution for real-valued problems with many equality and inequality constraints '
                'and a very small feasible region.')
    assert p['constraints'] == 'constrained' and p['variable_type'] == 'continuous'


def test_unconstrained_wins_over_constraint_word():
    assert extract('bound constrained single objective functions')['constraints'] == 'unconstrained'


@pytest.mark.parametrize('text,n', [('four conflicting objectives', 4), ('a bi-objective problem', 2),
                                     ('3 objectives with a concave front', 3), ('single objective, 30-dimensional', 1)])
def test_number_of_objectives(text, n):
    p = extract(text)
    assert p['n_objectives'] == n and p['objectives'] == ('single' if n == 1 else 'multi')


@pytest.mark.parametrize('text,d', [('30-dimensional problems', 30), ('100 decision variables', 100),
                                     ('dimension 10', 10), ('a high-dimensional problem', 'high')])
def test_dimensionality(text, d):
    assert extract(text)['dimensionality'] == d


def test_modality_separability_landscape():
    p = extract('non-separable multimodal functions with noise, a dynamic optimum and plateaus')
    assert p['separability'] == 'non-separable' and p['modality'] == 'multimodal'
    assert p['landscape'] == ['dynamic', 'noisy', 'plateau']


@pytest.mark.parametrize('text,vt', [('TSP heuristic for a few hundred cities', 'permutation'),
                                      ('OneMax and other pseudo-Boolean functions', 'binary'),
                                      ('half binary variables and half real ones', 'mixed'),
                                      ('symbolic regression with genetic programming', 'program')])
def test_variable_type(text, vt):
    assert extract(text)['variable_type'] == vt


def test_category():
    assert extract('runtime analysis of a (1+1) EA on pseudo-Boolean functions')['category'] == 'pure_math'
    assert extract('scheduling maintenance crews for an electricity grid')['category'] == 'applied'


def test_out_of_scope_gate():
    cookie = 'Please give me a recipe for chocolate chip cookies that stay soft for several days and use brown butter.'
    assert not in_scope(cookie)
    assert in_scope('need benchmarks for my GA asap, paper deadline is friday')
    assert in_scope('irrigation planning for farms')          # category found even without optimisation words


def test_schema_rejects_bad_values():
    p = empty_profile()
    p['objectives'] = 'several'
    with pytest.raises(ValueError):
        validate(p)
    q = empty_profile()
    q['landscape'] = ['noisy', 'noisy']
    with pytest.raises(ValueError):
        validate(q)


def test_deterministic():
    t = 'many-objective large-scale problems with 500 variables and noisy evaluations'
    assert extract_rules(t) == extract_rules(t)


def test_llm_extractor_is_off_by_default(monkeypatch):
    monkeypatch.delenv('SELFLEARN_LLM_EXTRACTOR', raising=False)
    extract('a multi-objective problem')                         # rule-based, no error
    monkeypatch.setenv('SELFLEARN_LLM_EXTRACTOR', '1')
    with pytest.raises(NotImplementedError):
        extract('a multi-objective problem')
