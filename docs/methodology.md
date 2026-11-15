# Methodology

The authoritative numbers are in `retrieval_v2/RESULTS.md`. This page explains how they were obtained. All intervals
are 95% bootstrap intervals.

## Task

Given a free-text description of an optimisation problem, return the five benchmark families that published papers
used for similar problems. The system recommends benchmarks, not algorithms.

## Knowledge base

- **Records.** 1,488 papers give 11,342 benchmark records with structured fields (Category, Problem_Context, landscape,
  dimensionality and others). The fields were extracted from the papers (`scripts/extraction/`) and validated
  (`scripts/data/`).
- **Entities and families.** Records are grouped into 3,199 problem entities (`v2_entities_pipeline.py`). The entities
  are grouped into 2,173 benchmark families by rules (`scripts/families/v5_families.py`, `family_rules_v5.json`).
- **Historical notes.** These are in `docs/part4_methodology.md`, `docs/data_notes.md` and
  `docs/family_diagnostics_v2.md`.

## Systems

| system | description |
|---|---|
| popularity | families ranked by the number of training papers |
| full v2 | BM25 and dense (all-mpnet-base-v2) over entities, reciprocal-rank fusion (k = 60), cross-encoder re-rank, family roll-up with an evidence bonus |
| paper-kNN | votes from the 100 nearest training papers |
| stacked ranker (v2.1/v2.2) | logistic regression over 8 features of the candidates from full v2 and paper-kNN, cross-fitted; **the primary claim** |
| blend 0.5 (v2.3) | weighted reciprocal-rank blend of full v2 and the stacked ranking at λ = 0.5; **the product**, chosen after seeing the test |

## Stage 1: automatic evaluation

**Design.**

- **Folds.** Five folds by paper, stratified by Category × Conference, with two seeds (42 primary, 43 replication).
- **Indexes.** Each fold's index is rebuilt from the training papers only.
- **Queries.** Each held-out paper gives one query from its own fields, with every benchmark name token masked. The gold
  is the paper's families that exist in the training index.
- **Pre-registration.** The criterion is in `retrieval_v2/evaluation/PREREGISTRATION.md`. It compares hit@5 of the
  stacked ranker with popularity. On both seeds it requires the overall upper bound ≥ 0, the Pure Math upper bound ≥ 0
  and the Applied lower bound > 0.

**Result: criterion met on both seeds.**

| seed | stacked hit@5 | popularity hit@5 | overall difference |
|---|---|---|---|
| 42 (n = 558) | .376 [.337, .421] | .328 [.290, .371] | +.048 [+.016, +.082] |
| 43 (n = 548) | .352 [.314, .392] | .310 [.268, .349] | +.042 [+.011, +.078] |

## Stage 2: written development queries (`queries_v2`)

There are 55 written queries with gold families, pre-registered in `PREREGISTRATION_queries.md`.

**This set was used for selection.**

- The v2.2 blend weight was chosen on it (`retrieval_v2/v22/`).
- The fallback threshold was chosen on it.
- The demo gallery comes from it.

So its numbers are selection numbers.

| system | hit@5 | MRR |
|---|---|---|
| stacked | .491 [.363, .618] | .336 [.239, .433] |
| full v2 | .564 [.436, .691] | .423 [.311, .536] |
| blend 0.5 | .600 [.473, .727] | .468 [.349, .585] |

The v2.2 rule selected λ = 1.0, which is the stacked ranking unchanged. So v2.2 ranks identically to v2.1.

## Stage 3: independent test

**Pre-registration.** The test is pre-registered in `PREREGISTRATION_final.md` and amendments 1 to 6, with a cut-off of
12 November 2026, 10:00 IST.

**Sets.** Writers who did not see the system wrote the sets, choosing gold families from a family list.

- t1, t3 and t4 (20 queries each, n = 60) were accepted.
- t2 was rejected at intake (amendment 1), because every gold id's stored name differed from the name written next to
  it.
- Provenance statements are in `PROVENANCE_t.md`. They are self-reported and not verified.

**Scoring.** A single run on 12 November 2026 with `score_final.py` against the frozen system (tag `retrieval-v2.2`,
environment `FROZEN_ENV.txt`). Every system's per-query top 5 is in `scored_queries_final.csv`, and the report is
`report_final.md`.

| quantity | value |
|---|---|
| **primary claim**: stacked minus popularity, hit@5 | **+0.350 [+0.217, +0.483]**, n = 60, width 0.267 (paired bootstrap, 10,000 resamples): SUPPORTED |
| cluster bootstrap over 38 groups sharing a gold family | +0.350 [+0.176, +0.530] |
| stacked hit@5 / MRR | 0.433 [0.317, 0.567] / 0.253 [0.177, 0.341] |
| popularity hit@5 | 0.083 [0.017, 0.167] |
| full v2 hit@5 | 0.517 [0.400, 0.650] |
| blend 0.5 hit@5 / MRR (selection numbers) | 0.500 [0.383, 0.633] / 0.385 [0.285, 0.500] |
| blend decision: blend minus stacked, MRR | +0.132 [+0.067, +0.202]: the blend replaces the primary |

**Product decision.** The blend decision rule was pre-registered but applied after the results were seen. So v2.3
(blend 0.5) is the product, and its test numbers are selection numbers.

## Caveats on the numbers

- **Small test.** n = 60.
- **Overlapping topics.** Topics overlap across sets, and t1 and t4 share a writer.
- **One set drives the advantage.** On t3 alone, the hit@5 interval against popularity includes 0.
- **Rare gold families.** 70% of the test's gold families (73 of 104) have fewer than 2 papers.
- **The evaluations disagree on the blend.**
  - On the automatic evaluation (seed 42), the blend's hit@5 is .190 [.158, .222], below popularity's .328.
  - On the written test, it is above popularity.
  - The query distributions differ (`retrieval_v2/RESULTS.md`, "Product decision").
- **Score bands are not validated.** The bands did not rise in order on the test.

The full list is in `docs/limitations.md` and the "Limitations" sections of `retrieval_v2/RESULTS.md`.
