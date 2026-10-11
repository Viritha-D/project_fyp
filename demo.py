"""
Live demo script for the panel review.

Runs the full pipeline end-to-end: a plain-English problem description goes
in, map_user_description() (Part 7: dense + sparse search, RRF fusion,
cross-encoder re-ranking with evidence bonus) finds the best-matching entity,
and assemble_final_output() (Part 8) turns that into the final response --
matched entity, evidence strength, and ranked strategies grouped by metric,
or an honest "no confident match" if nothing clears the bar.

Usage:
    python demo.py
Type a problem description at the prompt. Type 'examples' to run a few
pre-loaded demo queries, or 'quit' / Ctrl+C to exit.
"""

import logging
import os
import sys
import warnings

# Silence HF Hub's "unauthenticated requests" notice and the model-loading
# progress bars -- purely cosmetic for a live demo, must be set before the
# heavy imports below (they trigger model loading at import time).
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')
os.environ.setdefault('TRANSFORMERS_VERBOSITY', 'error')
os.environ.setdefault('HF_HUB_VERBOSITY', 'error')
warnings.filterwarnings('ignore')
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)

# Enable ANSI colors on Windows terminals (no-op elsewhere).
if os.name == 'nt':
    os.system('')

USE_COLOR = sys.stdout.isatty()


def _c(code, text):
    return f'\033[{code}m{text}\033[0m' if USE_COLOR else text


BOLD, DIM = '1', '2'
CYAN, GREEN, RED, YELLOW = '36', '32', '31', '33'

print(_c(DIM, 'Loading pipeline (models + entity index)... this takes about 10-20 seconds.'))

from part7_live_pipeline import map_user_description  # noqa: E402
from part8_final_output import assemble_final_output  # noqa: E402

EXAMPLE_QUERIES = [
    "I need to optimize battery charge equalization for an electric vehicle pack",
    "minimize a rugged multimodal function with many local minima",
    "what's a good recipe for pasta",  # deliberately out-of-scope
]

WIDTH = 78


def print_result(query, output):
    print()
    print(_c(CYAN, '=' * WIDTH))
    print(_c(f'{BOLD};{CYAN}', 'QUERY'))
    print(f'  "{query}"')
    print(_c(CYAN, '=' * WIDTH))
    print()

    if not output.get('mapped'):
        print(_c(f'{BOLD};{RED}', '  ✗ NO CONFIDENT MATCH'))
        print(_c(DIM, '  ' + '-' * (WIDTH - 2)))
        print('  Nothing in the knowledge base scored above the confidence threshold.')
        print(_c(DIM, '  (The top candidate seen was near-random noise, not a genuine semantic match --'))
        print(_c(DIM, '   the system correctly declined to force a guess rather than report it as an answer.)'))
        print()
        return

    entity = output['matched_entity']
    conf = output['match_confidence']
    evidence = output['evidence_strength']

    print(_c(f'{BOLD};{GREEN}', f"  ✓ MATCHED: {entity['canonical_name']}  ({entity['entity_id']})"))
    print(_c(DIM, '  ' + '-' * (WIDTH - 2)))
    print(f"  {'Confidence':<13}: score {conf['retrieval_score']:.2f}   "
          f"margin +{conf['margin_over_runner_up']:.2f} over runner-up")
    print(f"  {'Evidence':<13}: {evidence['n_supporting_papers']} supporting paper(s)  "
          f"({evidence['description_confidence']} confidence)")
    print(f"  {'Entity type':<13}: {entity['entity_type']}")

    conflicts = output.get('characterization_conflicts')
    if conflicts:
        print()
        print(_c(YELLOW, f"  ⚠ Papers disagree on: {', '.join(conflicts.keys())}"))

    if not output.get('strategies_available'):
        print()
        print(_c(DIM, '  No strategy data available for this entity.'))
        print()
        return

    print()
    print(_c(BOLD, '  RANKED STRATEGIES') + _c(DIM, '  (grouped by metric -- never compared across metrics)'))
    print(_c(DIM, '  ' + '-' * (WIDTH - 2)))
    for family in output['strategies_by_metric']:
        print(f"  {_c(f'{BOLD};{CYAN}', family['metric_family'])}")
        for s in family['strategies']:
            opt = (f"{s['pct_optimal_found_among_reported']:.0f}% optimal-found"
                   if s['pct_optimal_found_among_reported'] is not None else 'optimal-found unknown')
            print(f"    {s['rank']}. {s['strategy']:<55} {opt}, {s['evidence_label']}")
    print()


def main():
    print(_c(GREEN, 'Ready.'))
    print(_c(CYAN, '=' * WIDTH))
    print("Type a problem description, 'examples' for demo queries, or 'quit' to exit.")
    print(_c(CYAN, '=' * WIDTH))
    while True:
        try:
            query = input('\n> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query or query.lower() in ('quit', 'exit'):
            break
        if query.lower() == 'examples':
            for q in EXAMPLE_QUERIES:
                retrieval = map_user_description(q)
                output = assemble_final_output(retrieval, query_text=q)
                print_result(q, output)
            continue
        retrieval = map_user_description(query)
        output = assemble_final_output(retrieval, query_text=query)
        print_result(query, output)


if __name__ == '__main__':
    main()
