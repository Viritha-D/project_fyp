"""
Part 8 - Confidence scoring and final output assembly.

This wraps Part 7's retrieval result into the actual end-user-facing response:
entity match + evidence strength + ranked strategies per metric family.

`assemble_final_output` takes the dict returned by `map_user_description()`
(part7_live_pipeline.py) and turns it into the final response, or logs an
unmapped query and returns a clear "no confident match" response instead of
forcing one. The __main__ block below wires the two together end-to-end
against real queries.
"""

import json
import os
import pandas as pd
from datetime import datetime, timezone

with open('problem_entities.json', encoding='utf-8') as f:
    ENTITIES = {e['entity_id']: e for e in json.load(f)}

STRATEGY_LAYER = pd.read_csv('entity_strategy_layer_v2.csv')

UNMAPPED_LOG_PATH = 'unmapped_queries.csv'


def get_strategies_for_entity(entity_id, max_families=3, max_strategies_per_family=5):
    """Pull this entity's ranked strategies, grouped by metric family -- never
    flattened into one list, since strategies under different metrics can't be
    compared (the rule established back in Part 6)."""
    rows = STRATEGY_LAYER[STRATEGY_LAYER['entity_id'] == entity_id]
    if len(rows) == 0:
        return []

    # If multiple metric families exist, prioritize the ones with more total
    # evidence (more papers reporting), so the most-supported metric surfaces first.
    family_evidence = rows.groupby('metric_family')['n_papers_reporting'].sum().sort_values(ascending=False)
    families = []
    for metric_family in family_evidence.index[:max_families]:
        fam_rows = rows[rows['metric_family'] == metric_family].sort_values('rank_within_metric')
        strategies = []
        for _, r in fam_rows.head(max_strategies_per_family).iterrows():
            strategies.append({
                'strategy': r['strategy'],
                'rank': int(r['rank_within_metric']),
                'n_papers_reporting': int(r['n_papers_reporting']),
                'pct_optimal_found_among_reported': (
                    None if pd.isna(r['pct_optimal_found_among_reported'])
                    else float(r['pct_optimal_found_among_reported'])
                ),
                # Honest evidence label rather than a fake precision number --
                # most metric families here are backed by very few papers.
                'evidence_label': (
                    'single report only' if r['n_papers_reporting'] <= 1
                    else f'reported by {int(r["n_papers_reporting"])} papers'
                ),
            })
        families.append({'metric_family': metric_family, 'strategies': strategies})
    return families


def assemble_final_output(retrieval_result, query_text=None):
    """retrieval_result: the dict returned by map_user_description() in
    part7_live_pipeline.py -- {mapped, top_confidence, margin, results: [...]}.

    Returns the actual end-user-facing response, OR logs an unmapped query
    and returns a clear 'no confident match' response instead of forcing one.
    """
    if not retrieval_result.get('mapped', False):
        _log_unmapped_query(query_text, retrieval_result)
        return {
            'mapped': False,
            'message': "No confident match found for this description.",
            'top_candidate_seen': (
                retrieval_result['results'][0]['canonical_name']
                if retrieval_result.get('results') else None
            ),
        }

    top = retrieval_result['results'][0]
    entity = ENTITIES.get(top['entity_id'])
    if entity is None:
        return {'mapped': False, 'message': f"Entity {top['entity_id']} not found in knowledge base."}

    strategy_families = get_strategies_for_entity(top['entity_id'])

    return {
        'mapped': True,
        'matched_entity': {
            'entity_id': entity['entity_id'],
            'canonical_name': entity['canonical_name'],
            'entity_type': entity['entity_type'],
        },
        # Two SEPARATE numbers, deliberately not blended into one fake precision
        # score -- how well the description matched vs. how much literature
        # backs this entity are different kinds of uncertainty.
        'match_confidence': {
            'retrieval_score': top['confidence'],
            'margin_over_runner_up': retrieval_result.get('margin'),
        },
        'evidence_strength': {
            'n_supporting_papers': entity['n_supporting_papers'],
            'description_confidence': entity['description_confidence'],
        },
        'characterization_conflicts': entity.get('characterization_conflicts') or None,
        'strategies_by_metric': strategy_families,
        'strategies_available': len(strategy_families) > 0,
    }


def _log_unmapped_query(query_text, retrieval_result):
    """Kept structurally separate from the literature-derived knowledge base,
    per the original schema design -- these are unverified, system-flagged
    queries for later review, never blurred with verified paper-derived entities."""
    row = pd.DataFrame([{
        'query_text': query_text,
        'top_score_seen': retrieval_result.get('top_confidence'),
        'margin_seen': retrieval_result.get('margin'),
        'logged_at': datetime.now(timezone.utc).isoformat(),
    }])
    if os.path.exists(UNMAPPED_LOG_PATH):
        row.to_csv(UNMAPPED_LOG_PATH, mode='a', header=False, index=False)
    else:
        row.to_csv(UNMAPPED_LOG_PATH, index=False)


if __name__ == '__main__':
    # ---- Live end-to-end test: Part 7's real query -> match -> Part 8's assembly ----
    from part7_live_pipeline import map_user_description

    test_queries = [
        "I need to optimize battery charge equalization for an electric vehicle pack",
        "minimize a rugged multimodal function with many local minima",
        "what's a good recipe for pasta",  # deliberately out-of-domain
    ]

    for q in test_queries:
        print(f'\n{"=" * 70}')
        print(f'Query: "{q}"')
        print("=" * 70)
        retrieval_result = map_user_description(q)
        final_output = assemble_final_output(retrieval_result, query_text=q)
        print(json.dumps(final_output, indent=2, ensure_ascii=False))

    if os.path.exists(UNMAPPED_LOG_PATH):
        print(f'\n{"=" * 70}')
        print('Contents of unmapped_queries.csv:')
        print("=" * 70)
        print(pd.read_csv(UNMAPPED_LOG_PATH).to_string(index=False))