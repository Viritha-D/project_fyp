# Retrieval v2.2 experiment: pre-registration

Written and committed **before** any v2.2 code is run. The frozen v2.1 model is not changed: `v21_model.json`,
`v21.py`, `hybrid.py` and the entity, family and paper files stay as they are at tag `retrieval-v2.1-frozen`.
New code goes in `retrieval_v2/v22/`. `queries_v2.csv` and its gold are not edited, and no queries are added.

**Caveat, stated up front.** λ is chosen by MRR on `queries_v2`, so after this experiment `queries_v2` is a
**selection set**, not a test set. The v2.2 numbers on `queries_v2` will be optimistic for the chosen λ. The
honest test of v2.2 is the fresh independent query set, which will be scored once, later, with the frozen v2.2.

## A. Diagnostics (report only; nothing is selected or tuned on them)

**A1. The 7 demo queries** (`retrieval_v2/demo_outputs.md`), on the published index, for the systems
popularity, bm25_only, dense_only, full_v2, paper_knn and stacked.

- **"(1+1) EA runtime" query:** the rank of F00445 OneMax and F00455 LeadingOnes in each system.
- **Neuroevolution query:** the rank of:
  - every family whose name contains "gym" (case-insensitive): F00431, F00924, F01314, F01404, F01522, F01839;
  - every family whose lowercased alphanumeric name starts with "walker2d": F01054, F01298, F01600, F01601.
- Ranks are 1-based positions in each system's own ranked family list:
  - bm25_only and dense_only: the roll-up of their top 50 entities;
  - full_v2: its shortlist roll-up;
  - paper_knn: all voted families;
  - stacked: its candidates by probability, then the popularity padding.
  - A family absent from a system's list is "not a candidate". For stacked, a family that is reached only
    through the popularity padding is marked "(padding)".
- **The other five demo queries:** the top-5 family names of full_v2 and of stacked, side by side.

**A2. The 21 cause-(b) misses in `queries_v2`** (error analysis in `report_query_sets.md`).

- For each gold family: its rank under full_v2 and under stacked (as defined in A1), and its n_papers in the
  published index after hygiene.
- Also reported: the mean n_papers of the top-5 families under stacked and under full_v2, for these 21 queries
  and for all 55.

## B. One-parameter blend

**Lists.**

- R_full is the full v2 family ranking: the Part B pipeline, its shortlist roll-up in order, with no padding.
- R_stacked is the stacked v2.1 family ranking: the candidate families by cross-fitted (automatic) or
  deployment (`queries_v2`) probability, with no padding.

**Score.** score(f) = (1 − λ) / (60 + rank_full(f)) + λ / (60 + rank_stacked(f)), where ranks are 1-based. A
family absent from one list gets no contribution from that term.

**Ranking.** Sort the union of the two lists by score (descending, ties by family_id). Then pad to 10 with the
fold's hygiene popularity order (`popularity_clean`), excluding families already listed. λ ∈ {0, 0.25, 0.5, 0.75, 1}.

**What λ = 0 and λ = 1 reproduce.**

- λ = 1 reproduces v2.1 `stacked` exactly.
- λ = 0 is full_v2 plus popularity padding. It differs from Part B `full_v2` only when full_v2 lists fewer
  than 10 families.
- Both reproductions are checked and reported. The reference rows popularity, full_v2 (unpadded) and stacked
  are shown next to the curves.

**Data.**

- (i) `queries_v2` (55 queries, published index, deployment model).
- (ii) The five-fold automatic evaluation, seeds 42 and 43, with the same folds, queries, scored sets (558 / 548)
  and cross-fitted stacked probabilities (`candidates_v21_seed*.csv`) as v2.1. Full v2 is recomputed per fold from
  the cached training-only builds and checked against `results_v21_seed*.csv`.

**Metrics.** hit@1, hit@3, hit@5, recall@5 and MRR (first gold within the top 10), with 95% bootstrap intervals
(1,000 resamples, seed 42), over papers or queries. Everything is shown in one table of full curves.

**Selection rule (fixed here).**

1. A λ is eligible if its automatic-evaluation hit@5 point estimate is ≥ popularity's hit@5 point estimate on
   seed 42 (.328) **and** on seed 43 (.310).
2. Among the eligible λ, choose the one with the highest MRR point estimate on `queries_v2`. Ties go to the
   smaller λ.
3. If no λ is eligible, report that, and keep λ = 1 (unchanged v2.1) as the default.

No other selection is made, and nothing else is tuned.

**Confidence tier under the blend.** The tier stays the frozen v2.1 one: the stacked top-1 probability with
cut-offs 0.0723 / 0.1372. For the chosen λ, the hit@1 of the **blended** top-1 family per tier is measured on the
automatic evaluation (both seeds pooled). The CLI wording uses it as "about 1 in N", with N = round(1 / pooled hit@1).
For λ = 1 the v2.1 wording is kept.

**CLI.** `recommend_v21.py` gets `--lambda`, defaulting to the chosen value. With `--lambda 1` its output ranking
is that of v2.1. The commit is tagged `retrieval-v2.2` locally only, and the push command is printed, not run.
