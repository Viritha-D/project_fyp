# Pre-registration of the final test: amendment 4

This amends `PREREGISTRATION_final.md` (cf15185) and amendments 1 (1b3a188), 2 (d180627) and 3 (81384f4). Every rule
of amendments 1 to 3 stands, except where this amendment adds to it. Those rules include:

- the whole-query validity rule and the 25% set rule;
- the duplicate rule;
- names-only resolution;
- the frozen hashes;
- the MRR blend decision on the pooled valid rows;
- honest reporting below 40 queries;
- error causes for every system;
- the AI-use rule.

It was committed before any scoring. No system has been scored on t1, t3 or t4. The frozen system (tag
`retrieval-v2.2`, commit 6c81556) and every model, data file and result are unchanged.

## 1. Scoring date and time

**Not yet fixed.** The request for this amendment contained the unfilled placeholder "[DATE, TIME IST]", so amendments
2 and 3 still stand on this point. The date and time will be fixed in a further amendment, committed before any
scoring. No scoring takes place before that amendment exists.

Once fixed:

- provenance statements are due by that date and time;
- the test is whatever sets are accepted by then;
- a later set is not added.

Status at the time of writing:

- accepted: t1, t3 and t4 (20 valid queries each);
- rejected: t2;
- reserved: t2b;
- no provenance statement on AI use yet for t1, t3 or t4.

## 2. Scoring environment

The scoring environment is the one recorded in `FROZEN_ENV.txt` (commit 5733bda):

- Python 3.13.18, CPU;
- the listed library versions;
- `all-mpnet-base-v2` @ e8c3b32e…, `ms-marco-MiniLM-L-6-v2` @ 233902d2….

The versions used for the earlier recorded runs are unknown; the current ones are kept.

**Gate condition.** Scoring runs only if the reproduction gate passed in that environment. It did, on 2026-11-11:

- (i) queries_v2: stacked .491 / .336, full v2 .564 / .423, with top-5 lists identical for 55/55 queries;
- (ii) the v2.1-tag and v2.2-tag top-20 hashes are both 01848ba2…586b;
- (iii) automatic seed 42: stacked .376, popularity .328, with 558/558 top-5 lists identical.

**Before scoring.** `FROZEN_HASHES.txt` must verify, and the installed versions must equal `FROZEN_ENV.txt`. If either
check fails, scoring stops.

## 3. Primary analysis

Unchanged from amendments 1 to 3:

- **Data:** the pooled valid queries of the accepted sets, with the amendment 3 AI-use rule.
- **Claim:** the paired difference in hit@5, stacked ranker v2.2 (λ = 1.0) minus popularity.
- **Interval:** a query-level paired bootstrap, 10,000 resamples, seed 42.
- **Outcome:** a lower bound above 0 means supported, otherwise not supported. Below 40 queries, "not supported" is
  described as inconclusive at that size.
- **Blend decision:** made on paired MRR (blend 0.5 − primary), with the interval entirely above 0, on the same pooled
  rows.

## 4. Sensitivity analyses

These are descriptive and not decisive. Each reports the same paired differences, hit@5 and MRR (primary − popularity,
primary − full v2, primary − blend 0.5), with 95% intervals: 10,000 resamples, seed 42.

- **(a) Per set.** Each accepted set on its own.
- **(b) Leave one set out.** The pooled analysis repeated once without each accepted set.
- **(c) Cluster bootstrap.**
  - Clusters are the connected components of the pooled queries, where two queries are linked if they share at least
    one gold family (after validation and id resolution).
  - Each resample draws whole components with replacement (as many as there are components), and computes the mean
    paired difference over all queries in the drawn components.
- **(d) Provenance.** The pooled analysis without every set that has no AI-use statement, or that reports AI use for
  queries or for choosing families. If no set remains, (d) is reported as "not computable: no set has a qualifying
  statement".

**If (c) disagrees with the primary.** That is, if (c) puts the lower bound on the other side of 0. The report must
say so in the same paragraph as the primary result.

## 5. Output

The per-query top-5 families of every scored system (stacked, popularity, full v2, blend 0.5) are saved to
`scored_queries_final.csv`, with one row per query and system, and set, query_id, gold, top-5 and the per-query
metrics. The file is committed with the results.
