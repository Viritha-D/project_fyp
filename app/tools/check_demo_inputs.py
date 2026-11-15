"""
Fail if any demo input text (gallery query or example/placeholder text in app/demo_inputs.json) matches a held-out
test query exactly (after NFKC, casefold, whitespace collapsing) or has dense cosine (all-mpnet-base-v2) >= 0.8 with
any query in queries_t1 .. t5 / t2b. Run before every commit.

Usage: python app/tools/check_demo_inputs.py      (exit 0 = pass, 1 = fail)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'app'))
import core  # noqa: E402


def main():
    d = json.loads((ROOT / 'app/demo_inputs.json').read_text(encoding='utf-8'))
    inputs = [(f"gallery {g['query_id']}", g['query_text']) for g in d['gallery']] + [('placeholder', d['placeholder'])]
    tests = core.test_query_texts()
    sets = sorted({s for s, _, _ in tests})
    print(f'demo inputs: {len(inputs)}; held-out test queries: {len(tests)} from {sets}')
    exact = {core.norm_text(t): (s, q) for s, q, t in tests}
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    enc = lambda xs: m.encode(list(xs), normalize_embeddings=True, show_progress_bar=False)
    C = enc([t for _, t in inputs]) @ enc([t for _, _, t in tests]).T
    fail = False
    for i, (name, text) in enumerate(inputs):
        j = int(C[i].argmax())
        hit = exact.get(core.norm_text(text))
        bad = hit is not None or C[i, j] >= core.SIM_LIMIT
        fail |= bad
        print(f"{'FAIL' if bad else 'ok  '} {name}: max cosine {C[i, j]:.3f} with {tests[j][0]}:{tests[j][1]}"
              + (f'; EXACT match with {hit[0]}:{hit[1]}' if hit else ''))
    print('RESULT:', 'FAIL' if fail else 'PASS')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
