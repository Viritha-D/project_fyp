"""
Feature schema of the fallback module. Every feature has a fixed set of allowed values plus "unknown"; anything the
text does not state stays "unknown" and is never guessed. Validation is strict: an unexpected key or value raises.
"""

UNKNOWN = 'unknown'

# name -> allowed values (besides "unknown"). "dimensionality" is a positive integer, "high" or "unknown";
# "landscape" is a sorted list of tags (empty list = nothing stated).
FEATURES = {
    'category': ('pure_math', 'applied'),
    'variable_type': ('continuous', 'binary', 'integer', 'permutation', 'mixed', 'program'),
    'objectives': ('single', 'multi'),
    'n_objectives': None,            # positive integer or "unknown"
    'dimensionality': None,          # positive integer, "high", or "unknown"
    'separability': ('separable', 'non-separable'),
    'modality': ('unimodal', 'multimodal'),
    'landscape': ('noisy', 'dynamic', 'deceptive', 'plateau', 'rugged', 'expensive'),
    'constraints': ('constrained', 'unconstrained'),
}
KEY_FEATURES = ('category', 'variable_type', 'objectives', 'constraints')   # used for "sharing the key features"


def empty_profile():
    return {k: ([] if k == 'landscape' else UNKNOWN) for k in FEATURES}


def validate(profile):
    """Raise ValueError unless the profile follows the schema exactly. Returns the profile."""
    if set(profile) != set(FEATURES):
        raise ValueError(f'profile keys {sorted(profile)} differ from schema {sorted(FEATURES)}')
    for k, allowed in FEATURES.items():
        v = profile[k]
        if k == 'landscape':
            if not isinstance(v, list) or any(t not in allowed for t in v) or v != sorted(set(v)):
                raise ValueError(f'landscape must be a sorted list of {allowed}: {v!r}')
        elif k == 'n_objectives':
            if not (v == UNKNOWN or (isinstance(v, int) and not isinstance(v, bool) and v >= 1)):
                raise ValueError(f'n_objectives must be a positive int or unknown: {v!r}')
        elif k == 'dimensionality':
            if not (v in (UNKNOWN, 'high') or (isinstance(v, int) and not isinstance(v, bool) and v >= 1)):
                raise ValueError(f'dimensionality must be a positive int, "high" or unknown: {v!r}')
        elif v != UNKNOWN and v not in allowed:
            raise ValueError(f'{k} must be one of {allowed} or unknown: {v!r}')
    if profile['n_objectives'] != UNKNOWN:
        want = 'single' if profile['n_objectives'] == 1 else 'multi'
        if profile['objectives'] not in (UNKNOWN, want):
            raise ValueError('objectives and n_objectives disagree')
    return profile


def known(profile):
    """The features with a stated value (landscape counts only when it holds at least one tag)."""
    return {k: v for k, v in profile.items() if (v != UNKNOWN and v != [])}
