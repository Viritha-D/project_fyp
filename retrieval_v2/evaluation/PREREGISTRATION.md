# Retrieval v2.1 (Part C): pre-registration

Written and committed **before** any v2.1 system is run or any v2.1 metric is computed. The only results
seen so far are the Part B results (`report_auto.md`). No rule below is changed after test metrics are seen.
Anything that has to be changed after that point is reported as a deviation, with the reason, in the report.

Code: `retrieval_v2/v21.py` (components) and `retrieval_v2/evaluation/evaluate_v21.py` (evaluation).
Part B files (`hybrid.py`, `recommend.py`, `evaluate.py`, `report_auto.md`, `results_auto.csv`, `folds.csv`)
are not modified.

## 0. Fixed from Part B

- Papers, the query template, masking and gold definition are those of `evaluate.py`. One query per
  paper; gold = the v5 families of the paper's records; "seen" gold = gold families that are in the fold's
  training index (Part B definition, i.e. before hygiene); a paper without seen gold is "unseen" and not scored.
- Primary folds: seed 42, exactly `folds.csv` (5 folds, stratified Category x Conference, rare strata
  pooled). The scored set is the Part B set (n = 558). Hold-out builds are the cached Part B builds.
- Replication: seed 43, same procedure (new `StratifiedKFold(5, shuffle=True, random_state=43)`,
  new hold-out builds in `folds_cache/seed43/`). Its scored set is whatever that split gives; its n is reported.
- Metrics: hit@1, hit@3, hit@5, recall@5 (over seen gold), MRR (first gold in the top 10), means over
  papers with 95% bootstrap intervals (1,000 resamples, bootstrap seed 42). Breakdowns: Category,
  Conference, gold evidence (some seen gold family has >= 2 training papers, or not).
- Gold is not changed by the hygiene step: a hygiene-excluded family that is gold stays gold (it simply
  cannot be returned by the v2.1 systems). The number of scored queries affected is reported.

## 1. Index hygiene

- Excluded entities: canonical name (published `entity_notes_v2.json`), lowercased with every
  non-alphanumeric character removed, equal to `notreported`, `na` or `unknown`; plus every entity whose
  `flags` in `problem_entities_enriched_v2.json` contain `extraction_artifact_suspect`. The list is
  computed once from the published v2 files by entity_id and applied to every fold index.
  (Inspection of the data before writing this: E03148 "Not Reported" and E00657 "Evolutionary Algorithm";
  2 records.)
- Excluded entities stay in all data files. They are removed from the v2.1 retrieval index (BM25 is rebuilt
  on the remaining descriptions, dense search ignores them), from family roll-up, from family n_papers
  (training papers counted over non-excluded records), from kNN votes and from popularity.
- Hygiene applies to: paper-kNN, stacked, the two-slate output, and an extra row `popularity_clean`.
  The rows `popularity`, `bm25_only`, `dense_only` and `full_v2` are the **unchanged Part B systems**
  (they must reproduce Part B on seed 42; this is checked, not tuned).

## 2. Paper-kNN voting

- Query vector: all-mpnet-base-v2, L2-normalised (same as Part B).
- Cosine with `paper_embeddings.npy` rows of TRAINING papers only (rows are aligned to the master; the
  alignment is asserted). Paper similarity = maximum over its training rows.
- Top K papers; each paper votes its similarity for each of its families (set of families of its
  non-excluded records, once per family per paper). Family score = sum of votes. Ties broken by family_id.
- K in {10, 25, 50, 100}, chosen per outer fold by inner cross-validation on that fold's training papers
  only: 4 inner folds, `StratifiedKFold(4, shuffle=True, random_state=<outer seed>)` on the same
  Category x Conference strata (strata < 4 pooled). Inner gold = paper's families seen in the inner
  training papers (after hygiene); inner queries without seen gold are skipped. Criterion: mean inner
  hit@5; ties -> smaller K. The chosen K per fold is reported.

## 3. Stacked ranker

- Candidates per query: the families of the v2.1 full-pipeline shortlist (BM25 top 20 + dense top 20 ->
  RRF k = 60 -> 10 entities, on the hygiene index) UNION the top 20 kNN families (chosen K).
- Best member of a candidate family: if any of its members is in the shortlist, the shortlisted member with
  the highest cross-encoder (CE) score; otherwise the non-excluded member with the highest dense cosine,
  which is then scored by the CE.
- Features (8): (1) best-member CE score; (2) best-member BM25 score divided by the query's maximum BM25
  score over the index (0 if that maximum is 0); (3) best-member dense cosine; (4) kNN vote score (0 if no
  vote); (5) log1p(family training n_papers); (6-8) family kind one-hot: suite_or_series (`suite_series`,
  `numbered_series`), `stem_group`, `template_grid` (base: `single`).
- Model: `StandardScaler` + `LogisticRegression(C=1.0, max_iter=2000)` (sklearn defaults otherwise),
  label = candidate is a seen gold family.
- Cross-fitting: for outer fold i the model is trained on the candidate rows of the scored queries of the
  other four folds, whose features were computed with their own fold's index (out-of-fold for those
  queries). **This is stacking, not strict nesting**: the other folds' indexes contain fold i's papers as
  training data, so fold i's papers have influenced the features the fold-i model is trained on (never their
  labels and never fold i's own features).
- Ranking: candidates by predicted probability (ties family_id), padded to 10 with `popularity_clean` order.

## 4. Confidence

- The margin gate and the "not mapped" output are dropped for v2.1. Confidence = the stacked model's
  probability for the top-1 family.
- Tiers: for outer fold i, cut-offs are the 1/3 and 2/3 quantiles of the top-1 probabilities of the
  training-fold scored queries under the fold-i model. low < c1 <= medium < c2 <= high.
- Output label: tier "low" is shown as **low evidence**; medium and high are shown as such.
- Reliability table: per tier, n, hit@1 with 95% bootstrap interval, mean predicted probability.

## 5. Systems in the table

`popularity`, `bm25_only`, `dense_only`, `full_v2` (unchanged Part B), `popularity_clean`, `paper_knn`,
`stacked`; seed 42 and seed 43, with all breakdowns.

## 6. Success criterion (pre-registered)

Paired bootstrap over papers (1,000 resamples, seed 42) of d = hit@5(stacked) - hit@5(popularity), on the
scored queries of the group:

- (a) overall: upper bound of the 95% interval of d >= 0 (stacked not worse beyond the interval);
- (b) Pure Math: upper bound of the 95% interval of d >= 0;
- (c) Applied: lower bound of the 95% interval of d > 0 (an Applied advantage is kept).

"popularity" is the Part B baseline; the same test is also reported against `popularity_clean`.
The criterion is **met only if (a), (b) and (c) hold on seed 42 and on seed 43**. Point estimates of d are
reported too. If the criterion is not met, that is reported and nothing is changed.

## 7. Unseen analysis (seed 42)

The 930 unseen papers broken down by Category, Conference and number of distinct entities (1, 2, 3-5, >= 6),
plus the number whose every gold family has only one paper in the whole data. Oracle hit@5 = share of all
1,488 papers with at least one seen gold family (overall and per group), next to each system's hit@5 over
all papers (unseen counted as misses).

## 8. Two-slate output (optional, only after 1-7)

Slate = 3 "standard choices" (highest kNN vote among `suite_series` / `numbered_series` families; filled from
the stacked order if fewer than 3) + 2 "specific matches" (highest stacked probability excluding those).
Order: standard 1-3, specific 4-5. Compared at k = 5 (hit@5, recall@5) with the plain ranker that has the
highest overall hit@5 on the same seed, with paired bootstrap intervals of the difference.

## 9. Deployment model (`recommend_v21.py`)

Fitted by the same rules on all papers: K by the inner-CV rule on all papers (5 folds, seed 42); the
logistic model on the out-of-fold candidate rows of all seed-42 scored queries; tier cut-offs = the 1/3 and
2/3 quantiles of its top-1 probabilities on those queries.
