# Pre-registration of the final test: amendment 1

This amends `PREREGISTRATION_final.md` (cf15185). It was committed before any scoring of the independent query
sets. Where the two documents differ, this amendment applies. Nothing else in `PREREGISTRATION_final.md` changes.
The frozen system (tag `retrieval-v2.2`, commit 6c81556) is unchanged.

## 1. Delivered sets and status

| set | file | committed alone, unchanged | rows | valid rows | invalid share | status |
|---|---|---|---|---|---|---|
| t1 | `queries_t1.xlsx` (sha256 f6319d7f…a9202) | d6f57a0 | 20 | 20 | 0% | **accepted** |
| t2 | `queries_t2.xlsx` (sha256 45467528…19b45) | d6f57a0 | 20 | 0 | 100% | **rejected** under the validity rule below |
| t3 | - | - | - | - | - | not delivered |

- **t3** counts only if it is committed alone, unchanged, before scoring. It is then validated by the same rule.
- **t2** is kept in the repository, unchanged, with the reason for rejection: every gold id's stored family name
  differs from the name written next to it (`validation_t.md`). It is returned to its writer to redo by hand from
  `families_browse.csv`. The redo is committed as a new file and validated by the same rule.
- Validation details: `validation_t.md`, `validation_t_rows.csv`. Provenance: `PROVENANCE_t.md`.

## 2. Validity rule

- **Valid row.** A row is valid if (a)-(c) all hold for every gold id:
  - (a) the id exists in `families_v5.json` (case-insensitive);
  - (b) it is not an excluded family: F02124 "Not Reported", or F00334, the family of the extraction_artifact_suspect
    entity E00657;
  - (c) the written name equals the stored name for that id after normalisation (NFKC, lower case, whitespace
    collapsed), and the number of names equals the number of ids.
- **Whole query.** A query is valid or invalid as a whole. If any gold id fails (a)-(c), the whole query is
  excluded. The gold list is never trimmed to its valid ids, because that would be repairing it.
- **Excluded rows.** Invalid rows are excluded from every analysis. The count of excluded queries is reported per
  set.
- **Rejected sets.** If more than 25% of a set's rows are invalid, the whole set is rejected, kept in the repo with
  the reason, and returned to its writer to redo by hand from `families_browse.csv`. The redo is committed as a new
  file and validated by the same rule. Nobody else repairs gold.

## 3. Pooled test

The pooled test is the valid rows of all accepted sets. Query ids are prefixed with their set name (`t1:`, `t2:`,
`t3:`).

**Duplicates.** Identical text, or dense cosine (all-mpnet-base-v2) at or above 0.95 between queries, across t1,
t2 and t3, counts as a duplicate.

- Keep the first by file order (t1, then t2, then t3), drop the later one, and report how many were dropped.
- A cosine between 0.8 and 0.95 is flagged and kept.
- Current status (t1 and t2 compared, `validation_t.md`): no identical texts, no pair at or above 0.8, and the
  maximum cross-set cosine is 0.611.

## 4. Primary confirmatory claim

The claim is tested on the **pooled valid rows of the accepted sets**.

- **Statistic:** the paired difference in hit@5, stacked ranker v2.2 (λ = 1.0) minus popularity.
- **Interval:** paired bootstrap 95% interval, 10,000 resamples, seed 42.
- **Outcome:** a lower bound above 0 means the claim is **supported**; otherwise it is **not supported**. The
  result is reported either way.

**MRR stays the metric for the blend decision.** The blend λ = 0.5 replaces the primary only if the 95% interval of
its paired MRR advantage over the primary, on the pooled valid rows, lies entirely above 0. The interval for this
decision uses the same paired bootstrap, 10,000 resamples, seed 42.

## 5. Frozen hashes

`FROZEN_HASHES.txt` must match before scoring:

```
grep -v "^#" retrieval_v2/evaluation/FROZEN_HASHES.txt | sha256sum -c --strict
```

If any line fails, scoring stops.

## 6. Disclosure

This amendment was written after the files were received and after their query text was read. No system output on
them has been seen.

**What prompted the validity rule.** The rule was prompted by finding, in t2, ids that belong to other families in
queries_v2. For example, t2:Q12 lists F00032;F00033, which are ZDT and DTLZ in queries_v2, but names them as
energy-market families. The rule depends only on ids and names, not on any system result.

**When the threshold was set.** The 25% threshold was written after the validation counts were known: t1 0%
invalid, t2 100% invalid. Any threshold strictly between 0% and 100% gives the same outcome.

## 7. Expectation

With about 40 queries, the 95% interval on hit@5 is roughly ±0.15. The test can detect a large advantage over
popularity, but not a small difference between the stacked ranker and the blend. Failing to separate them means the
primary stays.

Current status: with t2 rejected, the pooled test has 20 valid queries (t1) until t3 or a t2 redo is accepted. On the
same reasoning, the interval is about √2 wider, roughly ±0.2.

## 8. Ambiguities in `AUDIT_pre_final.md`, settled

1. **Decision set.** The blend decision and the primary claim use the pooled valid rows of the accepted sets.
   Per-set results are reported descriptively and decide nothing.
2. **full v2 (λ = 0) padding.** Every system is scored exactly as frozen. This includes full v2's popularity padding
   (`v22/blend.py` at λ = 0, padded with hygiene popularity), as written in `PREREGISTRATION_final.md`.
3. **Gold validation.** A query is valid or invalid as a whole (section 2). This replaces "reported and left out,
   with the count stated" and "if a whole file has no valid gold, scoring of that file stops". A set with more than
   25% invalid rows is rejected.
4. **Duplicates across t1-t3.** Handled by section 3: drop at ≥ 0.95 or identical text, keep the first by file
   order, flag 0.8-0.95.
5. **Scoring bug found after scoring.** If a scoring bug is found after scoring (not a model or data change), only
   the scoring code is fixed. The sets are re-scored once, BOTH runs are reported with the reason, and the decision
   rule is re-applied to the corrected run. Nothing else may change.
6. **Computation path and ties.**
   - **One path only:** the batched scoring path used for queries_v2 (`recommend_v21.rank_batch` for all queries of
     the scored set, as in `score_human_queries.py`).
   - **Ties:** ties in the stacked probability are broken by family id, ascending (the frozen sort key is
     (−probability, family_id)). Ties in the blend score and in popularity are also broken by family id, ascending.
   - **Known noise:** the audit found that batched and single-query computation can swap families whose
     probabilities are tied to about 4 decimals (Q32, ranks 17/18). The single batched path removes that ambiguity.
