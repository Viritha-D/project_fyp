"""
Fix two bugs found in the team's entity_strategy_layer.csv (Part 6 output):

1. The "Other / Paper-Specific Metric" catch-all bucket lumps together rows
   whose *raw* Performance_Metric text is genuinely different (e.g. one
   entity mixing "RPD of Assignment Cost" with "Order Dispatched Rate"),
   so strategies get ranked against each other despite never being evaluated
   on the same metric -- the exact thing the brief said not to do.
   Fix: for any row whose metric_family isn't one of the already-validated
   known families, use its own raw Performance_Metric text as the
   metric_family instead of a shared "Other" bucket.

2. rank_within_metric doesn't actually sort by the optimal-found signal --
   e.g. entity E00027 has two strategies tied at pct_optimal_found=100.0
   sitting at rank 1 and rank 6, with 0%-strategies in between. It looks
   like the original rank preserved row-encounter order rather than being
   computed from the aggregate columns.
   Fix: recompute rank_within_metric within each (entity_id, metric_family)
   group as: has any optimal-found evidence (desc), pct_optimal_found_among_reported
   (desc), n_papers_reporting (desc, the frequency-count fallback the brief
   specifies when no numeric comparison is possible), strategy name (asc,
   final tie-break for determinism).

Known-family labels for everything NOT in the old "Other" bucket are kept
exactly as the team produced them (trusted, already validated) via a lookup
on (entity_id, strategy, Performance_Metric).
"""

import pandas as pd
import numpy as np

MASTER_CSV = 'papers_master_with_embeddings_ref.csv'
ENTITY_MAP_CSV = 'paper_to_entity_map_final.csv'
OLD_STRATEGY_CSV = r'C:/Users/daggu/Downloads/entity_strategy_layer.csv'
OUTPUT_CSV = 'entity_strategy_layer_fixed.csv'

OTHER_LABEL = 'Other / Paper-Specific Metric'


def main():
    master = pd.read_csv(MASTER_CSV)
    emap = pd.read_csv(ENTITY_MAP_CSV)
    old = pd.read_csv(OLD_STRATEGY_CSV)

    merged = emap.merge(
        master[['paper_id', 'Algorithm_Name', 'Performance_Metric', 'Is_Optimal_Found']],
        on='paper_id', how='left',
    )
    merged = merged[merged['Algorithm_Name'] != 'Not Reported'].copy()

    # trusted (entity_id, strategy, raw metric text) -> known family, from
    # every row the team did NOT put in the Other bucket
    known = old[old['metric_family'] != OTHER_LABEL]
    lookup_rows = merged.merge(
        known[['entity_id', 'strategy', 'metric_family']],
        left_on=['entity_id', 'Algorithm_Name'], right_on=['entity_id', 'strategy'],
        how='inner',
    )
    lookup = {
        (r.entity_id, r.Algorithm_Name, r.Performance_Metric): r.metric_family
        for r in lookup_rows.itertuples()
    }

    def resolve_family(row):
        key = (row['entity_id'], row['Algorithm_Name'], row['Performance_Metric'])
        return lookup.get(key, row['Performance_Metric'])

    merged['metric_family'] = merged.apply(resolve_family, axis=1)

    # ---- Aggregate ----
    def agg(g):
        n_reporting = len(g)
        has_status = g['Is_Optimal_Found'].isin(['True', 'False'])
        n_status = int(has_status.sum())
        pct = (100.0 * (g['Is_Optimal_Found'] == 'True').sum() / n_status) if n_status > 0 else np.nan
        return pd.Series({
            'n_papers_reporting': n_reporting,
            'pct_optimal_found_among_reported': pct,
            'n_papers_reporting_optimal_status': n_status,
        })

    grouped = (
        merged.groupby(['entity_id', 'metric_family', 'Algorithm_Name'], sort=False)
        .apply(agg, include_groups=False)
        .reset_index()
        .rename(columns={'Algorithm_Name': 'strategy'})
    )

    grouped['has_evidence'] = grouped['n_papers_reporting_optimal_status'] > 0
    grouped['pct_sort'] = grouped['pct_optimal_found_among_reported'].fillna(-1)
    grouped = grouped.sort_values(
        by=['entity_id', 'metric_family', 'has_evidence', 'pct_sort', 'n_papers_reporting', 'strategy'],
        ascending=[True, True, False, False, False, True],
    )
    grouped['rank_within_metric'] = (
        grouped.groupby(['entity_id', 'metric_family']).cumcount() + 1
    )
    grouped = grouped.drop(columns=['has_evidence', 'pct_sort'])
    grouped = grouped[['entity_id', 'metric_family', 'strategy', 'n_papers_reporting',
                        'pct_optimal_found_among_reported', 'n_papers_reporting_optimal_status',
                        'rank_within_metric']]

    grouped.to_csv(OUTPUT_CSV, index=False)

    # ---- Validation ----
    print(f'Old file: {len(old)} rows, {old["entity_id"].nunique()} entities, '
          f'{old["metric_family"].nunique()} metric families')
    print(f'New file: {len(grouped)} rows, {grouped["entity_id"].nunique()} entities, '
          f'{grouped["metric_family"].nunique()} metric families')

    bad = 0
    for _, g in grouped.groupby(['entity_id', 'metric_family']):
        g2 = g.sort_values('rank_within_metric')
        pct = g2['pct_optimal_found_among_reported'].fillna(-1).to_numpy()
        if any(pct[i] < pct[i + 1] for i in range(len(pct) - 1)):
            bad += 1
    print(f'Groups where rank order still violates descending pct: {bad}')

    print()
    print('--- E00027 after fix ---')
    print(grouped[grouped['entity_id'] == 'E00027'].to_string(index=False))


if __name__ == '__main__':
    main()
