# Pre-registration: scoring the written query sets

Written and committed **before** any of these query sets is scored. Models are frozen at tag
`retrieval-v2.1-frozen` (commit c0f8802): `retrieval_v2/v21_model.json`, `hybrid.py`, `v21.py`, the published v2
entity files and v5 families. Nothing that affects rankings is changed after this point. The refactor of
`recommend_v21.py` into `rank_batch()` leaves rankings unchanged (checked on a test query before this commit).

## Query sets

- **Primary:** `queries_v2.csv`, a cell-for-cell conversion of `queries_v2.xlsx` (committed alone and unchanged
  in c0f8802, before any scoring). 55 queries. Provenance: `PROVENANCE.md` (user's statement, unedited).
- **Secondary:** `ai_queries_v1.csv` and `queries_reworded_v1.csv` (the same 55 query ids and gold as each other;
  their gold was chosen by Claude according to the header of the original file). **At the time of writing neither
  file is in the repository, on any branch, or among the uploaded files.** They are scored with the same script,
  unchanged, if and when they are supplied; until then they are reported as not run.

## Gold validation (done before this commit)

Every id in `gold_families` exists in `families_v5.json` and is not a family made only of hygiene-excluded
entities (F02124 "Not Reported", F00334 "Evolutionary Algorithm"); every entry of `gold_family_names` equals the
family name of its id. Result for `queries_v2.csv`: 126 gold ids, 0 unknown, 0 excluded, 0 name mismatches,
0 queries without valid gold.

## Systems

On the published index (all papers): `popularity`, `bm25_only`, `dense_only`, `full_v2` (Part B), and the v2.1
deployment model: `paper_knn` (K = 100) and `stacked` (padded with hygiene popularity), via
`score_human_queries.py`.

## Metrics

- **Primary metrics:** hit@5 and MRR.
- Also reported: hit@1, hit@3, recall@5.
- All values are means over queries with 95% bootstrap intervals (1,000 resamples, seed 42).

## Primary comparisons

Paired bootstrap of the per-query difference for hit@5 and for MRR:

- stacked − popularity
- stacked − full_v2

Each difference is reported with its interval, whichever way it goes. No pass/fail threshold is set. Results on
the secondary sets are reported separately and never pooled with the primary set.

## Groups

The group is the text of `notes` before the first `;`, with any parenthetical qualifier removed, for example
`multi-objective (dynamic)` → `multi-objective`. For `queries_v2` this gives 6 groups:

| group | queries |
|---|---|
| continuous single-objective | 15 |
| multi-objective | 10 |
| combinatorial | 10 |
| machine learning | 10 |
| control / RL | 5 |
| vague | 5 |

Group sizes are reported with every group table.

## Confidence

Stacked top-1 probability tiers use the frozen cut-offs in `v21_model.json` (0.0723 / 0.1372). hit@1 is reported
per tier.

## Error analysis (primary set only)

This covers every query where the stacked ranker has no gold family in its top 5.

Cause, mutually exclusive:

- **(a)** no gold family among the stacked ranker's candidate families. Candidates are the shortlist families plus
  the top-20 kNN families; the popularity padding does not count.
- **(b)** a gold family is among the candidates but ranked below 5.

Flag, reported alongside (a)/(b):

- **(c)** every gold family has fewer than 2 papers in the index. The number of misses where at least one gold
  family has fewer than 2 papers is also given.

The first 15 such queries in query_id order are shown with the query, the gold family names and the stacked
top-5 names. Nothing is tuned on any of this.
