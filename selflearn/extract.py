"""
Rule-based feature extractor (deterministic; keywords and regular expressions; no network, no API key).

extract(text) -> profile following selflearn.schema; a feature not stated in the text stays "unknown".
in_scope(text, profile) -> False when the text has no optimisation vocabulary and no problem category or other
problem feature at all (every extracted feature unknown).

An optional LLM extractor could sit behind SELFLEARN_LLM_EXTRACTOR=1. It is NOT implemented: setting the variable
raises an error instead of silently falling back, so the default behaviour is always the rule-based extractor.
"""

import os
import re

from .schema import UNKNOWN, empty_profile, validate

WORDNUM = {'one': 1, 'single': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
           'nine': 9, 'ten': 10, 'bi': 2, 'tri': 3}

# vocabulary that marks an optimisation / benchmarking question
OPT_VOCAB = re.compile(
    r'\b(optimi[sz](e|es|ed|ing|ation|ations|er|ers)|evolutionary|evolution strateg\w*|genetic (algorithm|programming)|'
    r'\bga\b|\bgp\b|\bea\b|\bmoea\w*|\bde\b|differential evolution|\bpso\b|particle swarm|cma-?es|metaheuristic\w*|'
    r'heuristic\w*|benchmark\w*|test (problem|function|suite|instance)s?|objective\w*|fitness|minimi[sz]\w*|'
    r'maximi[sz]\w*|pareto|solver\w*|local search|hill climb\w*|simulated annealing|swarm|nsga\w*|moea/d|'
    r'search space|landscape\w*|scheduling|routing|travel+ing salesman|\btsp\b|knapsack|neuroevolution|'
    r'hyper-?parameter\w*|surrogate\w*|black-?box|runtime analysis|\(1\s*\+\s*1\)|crossover|mutation|evolv\w*|'
    r'population|\bes\b|local (optima|minima|maxima)|tsplib|time windows?|nodes|reward\w*|reinforcement learning|'
    r'controller)',
    re.I)

CATEGORY_RULES = [
    ('pure_math', r'\b(test functions?|benchmark functions?|synthetic|toy functions?|runtime analysis|theory|theoretical|'
                  r'pseudo-?boolean|onemax|leadingones|black-?box optimi[sz]ation benchmark|bbob|cec ?20\d\d|'
                  r'fitness landscapes?|tunable (epistasis|landscape)|nk[- ]landscape)\b'),
    ('applied', r'\b(real[- ]world|industrial|engineering design|application|scheduling|routing|vehicle|logistics|'
                r'supply chain|energy|power (grid|system)|electricity|grid|water|irrigation|farm|crop|hospital|'
                r'nurse|traffic|manufactur\w*|robot\w*|antenna|circuit|chemical|finance|portfolio|medical|clinical|'
                r'classification|regression|dataset|data set|image|neural network|feature selection|'
                r'hyper-?parameter|timetabling|warehouse|delivery|maintenance)\b'),
]

VARTYPE_RULES = [
    ('mixed', r'\b(mixed[- ]integer|mixed[- ]variable|mixed (binary|discrete)|half binary|binary and (real|continuous))\b'),
    ('permutation', r'\b(permutation\w*|travel+ing salesman|\btsp\b|ordering|sequenc(e|ing) of jobs|job[- ]shop|'
                    r'flow[- ]shop|vehicle routing|\bvrp\b|routing)\b'),
    ('program', r'\b(genetic programming|\bgp\b|symbolic regression|program synthesis|evolv\w* (programs?|trees?)|'
                r'expression trees?)\b'),
    ('binary', r'\b(binary|bit[- ]?strings?|pseudo-?boolean|boolean|onemax|leadingones|0/1|zero-one)\b'),
    ('integer', r'\b(integer|discrete variables?)\b'),
    ('continuous', r'\b(continuous|real[- ]valued|real[- ]parameter|real vectors?|numerical optimi[sz]ation|'
                   r'differential evolution|cma-?es|particle swarm|\bpso\b)\b'),
]


def _first(rules, text):
    for value, pat in rules:
        if re.search(pat, text, re.I):
            return value
    return UNKNOWN


def _objectives(text):
    m = re.search(r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|single|bi|tri)[- ]?(objectives?|'
                  r'conflicting objectives?|criteria)\b', text, re.I)
    if m:
        w = m.group(1).lower()
        n = int(w) if w.isdigit() else WORDNUM.get(w)
        if n:
            return ('single' if n == 1 else 'multi'), n
    if re.search(r'\b(many[- ]objective|multi[- ]?objective|bi-?objective|multi-?criteri\w+|pareto|moea\w*|nsga\w*|'
                 r'hypervolume|\bigd\b)', text, re.I):
        return 'multi', UNKNOWN
    if re.search(r'\bsingle[- ]objective\b', text, re.I):
        return 'single', 1
    return UNKNOWN, UNKNOWN


def _dimensionality(text):
    m = re.search(r'\b(\d{1,6})[- ]?(d\b|dim\w*|variables?|decision variables?|parameters?|genes?)', text, re.I)
    if not m:
        m = re.search(r'\bdimension(?:ality)?\s*(?:of\s*|=\s*)?(\d{1,6})\b', text, re.I)
    if m:
        n = int(m.group(1))
        if n >= 1:
            return n
    if re.search(r'\b(high[- ]dimensional|large[- ]scale)\b', text, re.I):
        return 'high'
    return UNKNOWN


def _constraints(text):
    if re.search(r'\b(unconstrained|bound[- ]constrained|box[- ]constrained|no constraints)\b', text, re.I):
        return 'unconstrained'
    if re.search(r'\b(constrain\w*|feasib\w*|infeasib\w*|(in)?equality constraints?|penalt\w+)\b', text, re.I):
        return 'constrained'
    return UNKNOWN


def _separability(text):
    if re.search(r'\bnon-?separab\w*|\binseparab\w*', text, re.I):
        return 'non-separable'
    if re.search(r'\bseparab\w*', text, re.I):
        return 'separable'
    return UNKNOWN


def _modality(text):
    if re.search(r'\b(multi-?modal|many local optima|lots of local optima|local (optima|minima)|rugged|deceptive|niching)\b',
                 text, re.I):
        return 'multimodal'
    if re.search(r'\buni-?modal\b', text, re.I):
        return 'unimodal'
    return UNKNOWN


LANDSCAPE = {
    'noisy': r'\b(nois\w+|stochastic (fitness|evaluation)s?|uncertain\w*)\b',
    'dynamic': r'\b(dynamic\w*|time[- ]varying|changing (environment|landscape|optim\w*))\b',
    'deceptive': r'\bdecepti\w+\b',
    'plateau': r'\b(plateaus?|neutral\w*|flat (regions?|landscapes?))\b',
    'rugged': r'\b(rugged\w*|epista\w+)\b',
    'expensive': r'\b(expensive|costly evaluations?|minutes? per eval\w*|limited (evaluation )?budget|surrogate\w*)\b',
}


def extract_rules(text):
    text = str(text or '')
    p = empty_profile()
    p['category'] = _first(CATEGORY_RULES, text)
    p['variable_type'] = _first(VARTYPE_RULES, text)
    p['objectives'], p['n_objectives'] = _objectives(text)
    p['dimensionality'] = _dimensionality(text)
    p['separability'] = _separability(text)
    p['modality'] = _modality(text)
    p['landscape'] = sorted(t for t, pat in LANDSCAPE.items() if re.search(pat, text, re.I))
    p['constraints'] = _constraints(text)
    return validate(p)


def extract(text):
    """The extractor used by the module. Rule-based unless SELFLEARN_LLM_EXTRACTOR=1 (not implemented: raises)."""
    if os.environ.get('SELFLEARN_LLM_EXTRACTOR', '') == '1':
        raise NotImplementedError('The optional LLM extractor is not implemented; unset SELFLEARN_LLM_EXTRACTOR.')
    return extract_rules(text)


def has_opt_vocabulary(text):
    return bool(OPT_VOCAB.search(str(text or '')))


def in_scope(text, profile=None):
    """False only when there is no optimisation vocabulary AND no problem category or other feature at all."""
    from .schema import known
    profile = profile or extract(text)
    return has_opt_vocabulary(text) or bool(known(profile))
