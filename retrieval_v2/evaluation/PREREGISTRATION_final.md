# Pre-registration: final independent test

This file was written and committed **before any test query file exists in the repository**. No model, rule
or earlier result changes. The system under test is frozen at tag `retrieval-v2.2` (commit 6c81556), which
ranks identically to v2.1 (λ = 1.0).

## Test data

The test sets are `queries_t1`, `queries_t2` and `queries_t3`, plus **pooled**, which is the three sets
concatenated.

- **Format.** Each file uses the queries_v2 layout: `query_id`, `query_text`, `gold_families`,
  `gold_family_names`, `notes`.
- **Commit order.** Each file is committed **alone and unchanged** (byte-identical to what is supplied), in
  its own commit, before any scoring. A cell-for-cell CSV conversion, if needed, comes in a later commit and is
  checked to round-trip.
- **No edits.** Queries and gold are never edited. No query is added or removed.
- **Pooled ids.** In the pooled set, query ids are prefixed with their set name (`t1:`, `t2:`, `t3:`) so they
  stay unique. Pooled intervals resample over all pooled queries.
- **Gold validation.** Run before scoring, as for queries_v2:
  - every gold id must exist in `families_v5.json`;
  - no gold id may be a hygiene-excluded family (F02124, F00334);
  - every `gold_family_names` entry is compared with the family name, and every mismatch is reported without
    being corrected.
  - A query whose gold has no valid id is reported and left out, with the count stated. If a whole file has no
    valid gold, scoring of that file stops.
- **Provenance.** Any provenance statement supplied with a file is copied unedited.

## Systems

All systems run on the published index, with no retraining:

- **PRIMARY:** stacked ranker v2.2 (λ = 1.0), i.e. `recommend_v21.py` defaults and the stacked ranking padded
  with hygiene popularity.
- **SECONDARY (exploratory):**
  - **full v2 (λ = 0):** the blend of `v22/blend.py` at λ = 0, which is the full v2 family ranking padded with
    hygiene popularity.
  - **blend λ = 0.5:** `v22/blend.py`.
  - **popularity:** the Part B popularity ranking of the published index.

## Metrics

- **Primary:** hit@5 and MRR. MRR counts the first gold family within the top 10.
- **Secondary:** hit@1, hit@3 and recall@5. recall@5 is computed over each query's gold families.
- All metrics are means over queries with 95% bootstrap intervals (1,000 resamples, seed 42). Each is reported
  for t1, t2, t3 and pooled.
- The stacked ranker's confidence tiers (frozen cut-offs 0.0723 / 0.1372) with hit@1 per tier are also reported,
  as a secondary result.

## Comparisons

All comparisons are paired: a bootstrap of the per-query difference over the same resampled queries, for hit@5
and for MRR, on each set and on pooled.

- primary − popularity
- primary − full v2 (λ = 0)
- primary − blend λ = 0.5

## Decision rule (product system)

The decision is made on the **pooled** set.

- The blend λ = 0.5 replaces the primary as the product system **only if** the 95% interval of its paired MRR
  advantage over the primary (blend 0.5 − primary) lies **entirely above 0**.
- Otherwise the primary stays.

Either way, all systems are reported, and the report states that this choice was made **after seeing the test**.
No other change of any kind is made after scoring: no new λ, features, rules, gold, queries or re-scoring.

## Code

The scoring script for these files is committed after this pre-registration and **before** any test file is
scored. It may only implement what is written here.
