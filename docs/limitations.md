# Known limitations of the benchmark recommender

This page lists the limits found in the demo audit (`docs/audit_demo.md`, 2026-11-14) and in building the fallback
module (`docs/selflearning.md`). The product system is v2.3 (blend 0.5). Numbers from the independent test come from
`retrieval_v2/RESULTS.md`. The blend's test numbers there are selection numbers, because the blend was chosen after
seeing the test.

## What the recommender can get wrong

- **Applied problems often return families backed by a single paper.**
  - Many real-world problems have no standard, named benchmark, so the closest matches are problems that one published
    paper studied.
  - In the audit, 5 of 5 families for an electricity-grid crew-scheduling question and 4 of 5 for an irrigation question
    had a single paper. The app marks these "Single paper only".
  - On the independent test, 70% of the gold families (73 of 104) had fewer than 2 papers.
- **A constrained problem may not return the classic constrained suite.**
  - For a differential-evolution question about many equality and inequality constraints and a small feasible region,
    the v2.3 top family was "Stackelberg duopoly" (1 paper).
  - In live mode this question now triggers the fallback, because every one of the top five conflicts with
    "constrained".
  - The fallback shortlist is CEC 2010 suite, Obstacle-Aware Maximum Coverage Deployment, CEC 2024 suite, Berth and
    Quay Crane Assignment and bar truss. It **misses the CEC 2006 suite**, because that suite's records in the data are
    mostly tagged unconstrained (19 records versus 5).
  - DASCMOP and MW profile as constrained but rank below 5.
  - **This depends on the wording.** The audit's exact question (`docs/audit_demo.md`) triggers the fallback. Two
    shorter versions tested on 2026-11-15 ("Differential evolution for real-valued problems with many equality and
    inequality constraints and a small feasible region", and the same with "a very small feasible region.") did not.
    Their top five included CEC 2011 suite and MOPTA 2008, so the conflict rule did not fire, and p1 (0.0496 and
    0.0548) was above the threshold.
- **The confidence trigger is weak.**
  - The low-confidence threshold (p1 < 0.0134, the probability of the blend's rank-1 family) has Youden's J = 0.197 on
    the 55 development queries.
  - 6 development queries fall below it, of which 5 are misses; 17 misses stay above it.
- **The score band is not a quality guarantee.**
  - The band (1 = top) comes from the stacked ranker's confidence. It is experimental and was not validated for v2.3.
  - On the independent test, hit@1 did not rise from the lowest band to the top band (low .111, medium .059, high .188,
    with wide intervals).

## The fallback module (selflearn)

- **Unrelated questions are rejected in live mode.** A question with no optimisation vocabulary and no stated problem
  feature gets "this does not look like an optimisation problem". It gets no shortlist and nothing is stored. Outside
  the app (for example, calling `recommend_v23` directly), every text still gets five families.
- **The hold-out check is descriptive, not an accuracy.** It was run on the development queries only. 87 of 126
  removed-family/query pairs had a shortlist family in the same group or sharing the key features. 11 of 35 had a
  same-group family, where such a group existed. The "shares key features" measure is weak, because common feature
  combinations are shared by many families.
- **The optional LLM extractor is not implemented.** Setting `SELFLEARN_LLM_EXTRACTOR=1` raises an error. Only the
  rule-based extractor exists.
- **The learned store is empty.** It is read-only on the hosted app, because that file system is not durable.
  Suggestions are stored, as unverified, only when the app runs locally, and they need human verification
  (`python -m selflearn.verify`).

## Sources without links

**No source paper has a link.** The knowledge base has no DOI or URL for any paper. The checks were:

- every column of `papers_master_with_matching_text_v2.csv` (11,342 records);
- every column of `paper_index.csv` (1,488 papers).

So every source paper the app shows, all 1,488 papers, is listed by title, conference and year only, without a link. No
link is invented.

**`Source_Platform` URLs are not paper links.** That column holds 338 URLs, such as benchmark or dataset download pages
(for example www.math.uwaterloo.ca, yann.lecun.com and github.com). They describe where a dataset comes from, not the
paper, so they are not shown as source links.

## Running the demo

- **Live mode is local only.** It needs about 1.8 GB installed and peaks at 1.4 to 1.5 GB of memory at the first answer.
  The first answer takes 7 to 16 seconds, and a fresh start downloads about 0.5 GB of model weights.
- **The hosted app shows precomputed examples.** It does not run retrieval, because the free hosting tier does not
  guarantee the memory and CPU that live mode needs.
