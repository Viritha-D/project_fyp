# Audit before the final independent test

Date: 2026-11-09. Audited HEAD: 52cf7ef on `claude/magical-pascal-uxsxvk`. This file adds no model, data, rule or
result changes. Re-runs were done read-only in scratch git worktrees of the tags `retrieval-v2.1-frozen` (c0f8802)
and `retrieval-v2.2` (6c81556), outside the repository.

## Summary

| item | check | result |
|---|---|---|
| 1a | only .md changed since 6c81556 | **PASS** (with an explanation for one .py) |
| 1b | no test query files added or present | **PASS** |
| 1c | PREREGISTRATION_final.md has every required item | **PASS** (ambiguities quoted below) |
| 1d | branch pushed; tags | **PASS** |
| 2 | RESULTS.md Blend / Known weaknesses numbers = report_v22.md; naming; selection statement | **PASS** |
| 3(i) | queries_v2 re-score: stacked .491/.336, full v2 .564/.423 | **PASS** |
| 3(ii) | top-20 lists identical, v2.2 (λ = 1.0) vs v2.1, 55 queries, hashed | **PASS** (caveat below) |
| 3(iii) | seed-42 automatic re-run (281 s): stacked .376, popularity .328 | **PASS** |
| 4 | FROZEN_HASHES.txt written and committed | **PASS** |
| 5 | headline-number mismatches | **PASS** (none in current numbers; historical differences listed) |
| 6 | leakage ledger | **PASS** (only the λ selection used queries_v2; section added to RESULTS.md) |

## 1a. Changes since 6c81556

```
cf15185 2026-11-03 08:33:22 +0000 Pre-register the final independent test (before any test query file exists)
3b1950f 2026-11-03 08:33:03 +0000 RESULTS.md: stacked ranker (v2.1/v2.2), blend experiment, known weaknesses (documentation only)
6c81556 2026-11-03 08:23:17 +0000 recommend_v21: --lambda (default = v2.2 selection, 1.0); default output unchanged
907b6c1 2026-11-03 08:20:55 +0000 Retrieval v2.2 results: diagnostics, lambda curves, selection (lambda = 1.0)
2937453 2026-11-03 08:18:44 +0000 Retrieval v2.2: queries_v2 blend results (run in progress)
f7c6aab 2026-11-03 08:14:43 +0000 Retrieval v2.2: blend and experiment code (diagnostics, lambda curves, fixed selection rule)
71e6287 2026-11-03 08:13:22 +0000 Retrieval v2.2: pre-registration (before any v2.2 run)

git show --stat 3b1950f:  retrieval_v2/RESULTS.md | 96 ++++-  ;  retrieval_v2/evaluation/build_results_md.py | 53 +++-
git show --stat cf15185:  retrieval_v2/evaluation/PREREGISTRATION_final.md | 73 +++
```

Files changed between 6c81556 and the audit start (cf15185): `retrieval_v2/RESULTS.md`,
`retrieval_v2/evaluation/PREREGISTRATION_final.md`, `retrieval_v2/evaluation/build_results_md.py`.

**Explanation for the one .py.** `build_results_md.py` is the generator for RESULTS.md. Its diff only adds RESULTS
text (the naming, the Blend experiment and Known weaknesses sections, and a text replace of `| stacked |`). It reads
`report_v22.md` and `v22_selection.json` and writes only `RESULTS.md`. It imports no ranking code and changes no
model, ranking or result file. One dead statement remains after its `return` (harmless).

The audit itself added 52cf7ef (`FROZEN_HASHES.txt`, one RESULTS.md section) and this file. No .json, .csv, .npy
or config file changed.

## 1b. Test query files

`git log --all --diff-filter=A -- 'retrieval_v2/**/queries_t*' '**/user_queries*'` printed nothing.
`git status --porcelain --untracked-files=all` printed nothing, and no `queries_t*` or `user_queries*` file exists
on disk. The uploaded `queries.xlsx` from 2026-11-03 was byte-identical to queries_v2.xlsx (sha256 b43d2c54…bfd02)
and was not committed as test data.

## 1c. PREREGISTRATION_final.md

| required item | where | ok |
|---|---|---|
| t1/t2/t3 + pooled; each committed alone, unchanged, before scoring | lines 9–16 | yes |
| PRIMARY = stacked ranker v2.2 (λ = 1.0) | line 33 | yes |
| SECONDARY = full v2 (λ = 0), blend 0.5, popularity | lines 35–39 | yes |
| hit@5 and MRR primary; hit@1/hit@3/recall@5 secondary; 95% bootstrap over queries | lines 43–46 | yes |
| paired comparisons (primary − popularity / full v2 / blend 0.5) | lines 52–57 | yes |
| blend replaces primary only if its paired MRR advantage has a 95% interval entirely above 0 | lines 63–65 | yes |
| choice made after seeing the test; nothing else changes after scoring | lines 67–68 | yes |

Ambiguities, quoted:

1. *"The decision is made on the **pooled** set."* (line 61). The user's prompt did not name the set. Pooled was
   chosen when the file was written.
2. *"full v2 (λ = 0): the blend of `v22/blend.py` at λ = 0, which is the full v2 family ranking padded with hygiene
   popularity."* (lines 36–37). This is not byte-identical to Part B full v2 when full v2 lists fewer than 10
   families. On queries_v2: hit@5 .564 for both, MRR .428 vs .423.
3. *"A query whose gold has no valid id is reported and left out ... If a whole file has no valid gold, scoring of
   that file stops."* (lines 25–26). This is looser than the queries_v2 rule ("Stop if any query would have no valid
   gold"), although the file says *"as for queries_v2"* (line 20).
4. *"pooled, which is the three sets concatenated"* (lines 9–10). Duplicate queries across t1–t3 are not addressed.
5. *"no ... re-scoring"* (line 68). There is no provision for a scoring-code bug found after scoring.
6. Not stated: which computation path is used. See the 3(ii) caveat. The scorer uses the batched path
   (`rank_batch`), as for queries_v2.

## 1d. Pushed state and tags

```
## claude/magical-pascal-uxsxvk...origin/claude/magical-pascal-uxsxvk
cf1518583846f412c440024de8796936fd8e69bb  refs/heads/claude/magical-pascal-uxsxvk   (= local HEAD at audit start)
local  retrieval-v2.1-frozen  988690011d1acd836d364015d8f013870aa9fd44 -> commit c0f8802181b5066b85b331e9818eb0a3ce4fdc6d
local  retrieval-v2.2         4e3d4916ece3bbfe8a1105ebbcb0bae5510a9b75 -> commit 6c81556c35d4b679a8f75dfc9ac1df945c47bcdd
remote retrieval-v2.1-frozen  7a02d9d1… -> c0f8802181b5…   (pushed by the user; same commit)
remote retrieval-v2.2         b80e3709… -> 6c81556c35d4…   (pushed by the user; same commit)
```

The tag objects differ between local and remote because they were created separately, but both pairs point to
the same commits.

## 2. RESULTS.md against report_v22.md

The B1 curve table and the B2 selection table are verbatim copies (string containment checked). Prose numbers:

| item | RESULTS.md | report_v22.md |
|---|---|---|
| popularity auto hit@5, seed 42 / 43 | .328 / .310 | 0.328 / 0.310 |
| λ = 1 auto hit@5, seed 42 / 43 | .376 / .352 | 0.376 / 0.352 |
| λ < 1 auto hit@5 | about .19 / .21 | 0.186–0.194 / 0.208–0.212 |
| queries_v2 MRR, λ 0.5 / 0.75 vs 1.0 | .468 vs .336 | 0.468 / 0.468 vs 0.336 |
| chosen λ | 1.0 | 1.0 |
| mean top-5 size on 21 cause-(b) queries, stacked vs full v2 | 25.8 vs 5.7 | 25.8 vs 5.7 |
| same, all 55 queries | 24.8 vs 4.8 | 24.8 vs 4.8 |
| cause-(b) queries with a full v2 gold family in its top 5 | 7 | 7 |
| full v2 rank of linear ordering / Symbolic Regression | 1 / 1 | 1 / 1 |
| OneMax: stacked / BM25 / full v2 | 7 / not a candidate / not a candidate | same |
| LeadingOnes: stacked / BM25 / full v2 | 30 (padding) / not a candidate / not a candidate | same |
| DE query: full v2 rank 1; includes Indoor localization | Stackelberg duopoly; yes | same |
| TSP: Gymnasium + Test-Assignment in full v2; DTLZ in stacked | yes; yes | same |
| defect query: sphere, rastrigin, mnist in stacked | yes | same |

Other checks:

- "stacked ranker (v2.1/v2.2)" appears 18 times, and no `| stacked |` table cell is left.
- The verbatim B1 table keeps report_v22's row label "stacked v2.1 (reference)".
- RESULTS.md says "lambda was selected on queries_v2" and "selection numbers, not test numbers".

## 3. Reproducibility (read-only)

**(i)** Running `score_human_queries.py` from the `retrieval-v2.2` worktree on a scratch copy of queries_v2.csv:

| system | recorded hit@5 / MRR | re-run hit@5 / MRR | per-query top-5 identical |
|---|---|---|---|
| stacked | .491 / .336 | .491 / .336 | 55/55 |
| full v2 | .564 / .423 | .564 / .423 | 55/55 |

**(ii)** Top-20 family lists for the 55 queries:

- The v2.1-tag code (`recommend_v21(q, k=20)`, single query) and the v2.2-tag code (`recommend_v21(q, k=20,
  lam=1.0)`, single query) are **identical for 55/55 queries**. The sha256 of both list sets is
  `01848ba28478ba6dbd4c4c1272e495199443ad2b3d305f0ca24ee1571f5c586b`.
- **Caveat.** The v2.2 batched path (`rank_batch` of all 55 + `blend(…, λ = 1.0)`, sha256 d6c3d127…0aa5) differs
  from the single-query path in one place: Q32 swaps F00878 and F00877 at ranks 17/18. Both have stacked
  probability 0.0048, so this is floating-point noise from batched cross-encoder inference. It is not a
  v2.1/v2.2 difference, and the batched v2.2 path disagrees with the single-query v2.2 path in exactly the same
  way. Top-5 lists are unaffected (55/55).
- The final scoring should use one fixed path. The scorer uses the batched path, as for queries_v2.

**(iii)** `evaluate_v21.py --seeds 42` was re-run in the v2.2 worktree (281 s, under the 15-minute cap):

| system | recorded hit@5 / MRR | re-run hit@5 / MRR | top-5 identical |
|---|---|---|---|
| stacked | .376 / .255 | .376 / .255 | 558/558 |
| popularity | .328 / .164 | .328 / .164 | 558/558 |
| full v2 | .186 / .116 | .186 / .116 | 558/558 |
| paper-kNN | .242 / .142 | .242 / .142 | 558/558 |

- The candidate rows are the same 14,611 (paper, family) pairs, with a maximum probability difference of 0.0.
- The re-fitted deployment model is byte-identical to the frozen `v21_model.json` (same sha256).

## 4. Freeze

`FROZEN_HASHES.txt` (committed in 52cf7ef) holds the sha256 of every requested file and the other files the
ranking reads:

- requested: `recommend_v21.py`, `config.json`, `families_v5.json`, `entity_to_family_v5.csv`,
  `family_notes_v5.json`, `entity_embeddings_v2.npy`, `paper_embeddings.npy`, `v21_model.json` (ranker weights
  and tier thresholds), `families_browse.csv`;
- also frozen: `v21.py`, `hybrid.py`, `blend.py`, `v22_selection.json`, `evaluate.py`, `score_human_queries.py`, the
  entity descriptions, order and notes, the record map and the master.

It also records canonical-JSON hashes of the stacker weights and of the tier thresholds inside `v21_model.json`.
All entries verify OK at HEAD and at tag `retrieval-v2.2`. Final scoring must first run:

```
grep -v "^#" retrieval_v2/evaluation/FROZEN_HASHES.txt | sha256sum -c --strict
```

## 5. Headline numbers

Recomputed from the data files: 11,342 records; 1,488 papers (paper_key in the map = paper_index.csv rows); 3,199
entities; 2,173 families; 42.0% of records in families with ≥ 2 papers.

| number | where it appears | status |
|---|---|---|
| 11,342 rows | RESULTS.md, data_notes.md, audit_report.md, family_diagnostics_v2.md | consistent |
| 1,488 papers | RESULTS.md, report_auto.md, report_v21.md ("1488"), PREREGISTRATION.md, data_notes.md | consistent |
| 1,494 papers | audit_report.md, data_notes.md lines 11 and 55 | historical, before the 6 approved merges; data_notes.md explains 1,494 → 1,488 |
| 3,199 entities | RESULTS.md, data_notes.md, family_diagnostics_v2.md | consistent |
| 2,173 families | RESULTS.md, data_notes.md | consistent |
| 42.0% | data_notes.md (v5 section) | consistent with the recomputed value |
| old entity count | data_notes.md and part4_rules.json: 1,038 (original Part 4 map; `part4_answer_key_map.csv` has 1,038 distinct ids); part4_methodology.md: "Output: 1,035 candidate problem entities"; old problem_entities.json on main: 1,035; v2_entities_pipeline.py: "1,038 from Part 4; 1,035 after the old repairs" | two stages, not a contradiction, but data_notes.md mentions only 1,038 |

- **1,036 does not appear anywhere** in the tracked docs on this branch or on main. The old figures are 1,038 and
  1,035.
- `index.html` does not exist on this branch or on main, so it was not checked.
- The retrieval_v2 and extraction READMEs and the v22 README contain none of these numbers.

## 6. Leakage ledger

- The model files were last changed before queries_v2 was committed (c0f8802, 06:27 UTC):
  - `v21_model.json` at c7a0e04 (05:57);
  - `v21.py` and `evaluate_v21.py` at 6b0e1fc;
  - `hybrid.py` and `config.json` at 31b4d55;
  - families at 014be24;
  - entity and paper embeddings on 2026-10-28.
- Code reading queries_v2: `score_human_queries.py` (via its argument), `report_query_sets.py`,
  `build_results_md.py` and `v22/run_v22.py`. A `git grep` hit in `recommend.py` is only its
  `unmapped_queries_v2.csv` log name.
- The single use of queries_v2 for tuning is the v2.2 λ selection (it chose 1.0).

The full list of decisions taken after seeing queries_v2 is in RESULTS.md, "Decisions made after seeing
queries_v2". It was added directly to RESULTS.md, so re-running `build_results_md.py` would drop it. The
generator was not edited, because the audit allowed only RESULTS.md, this file and FROZEN_HASHES.txt.
