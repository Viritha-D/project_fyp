# Known limitations of the benchmark recommender demo

These are the limits found in the demo audit (`docs/audit_demo.md`, 2026-11-14). The product system is v2.3
(blend 0.5). Numbers from the independent test are cited from `retrieval_v2/RESULTS.md`; the blend's test numbers there
are selection numbers, because the blend was chosen after seeing the test.

## What the recommender can get wrong

- **Applied problems often return families backed by a single paper.** Many real-world problems have no standard,
  named benchmark, so the closest matches are problems that a single published paper studied. In the audit, 5 of 5
  families for an electricity-grid crew-scheduling question and 4 of 5 for an irrigation question had a single paper.
  The app marks these with "Single paper only". On the independent test, 70% of the gold families (73 of 104) had fewer
  than 2 papers.
- **A constrained problem may not return the constrained suites.** For a differential-evolution question about
  problems with many equality and inequality constraints and a small feasible region, the top family was "Stackelberg
  duopoly" (1 paper). None of the constrained suites in the data (CEC 2006 suite, DASCMOP, MW) was in the top 5.
- **An unrelated question is still answered.** Until the planned fallback step is built, the app returns five families
  for any text. In the audit, a cookie-recipe question got five unrelated families; the only signal was the lowest
  score band.
- **The score band is not a quality guarantee.**
  - The band (1 = top) comes from the stacked ranker's confidence. It is experimental and was not validated for v2.3.
  - On the independent test, hit@1 did not rise from the lowest band to the top band (low .111, medium .059, high
    .188, with wide intervals).
  - In the audit, the constrained question above got the top band.

## Sources without links

**No source paper has a link.** The knowledge base has no DOI or URL for any paper. The checks were:

- every column of `papers_master_with_matching_text_v2.csv` (11,342 records);
- every column of `paper_index.csv` (1,488 papers).

So every source paper the app shows, all 1,488 papers, is listed by title, conference and year only, without a link. No
link is invented.

**`Source_Platform` URLs are not paper links.** That column holds 338 URLs, such as benchmark or dataset download pages
(for example www.math.uwaterloo.ca, yann.lecun.com and github.com). They describe where a dataset comes from, not the
paper, so the app does not show them as source links.

## Running the demo

- **Live mode is local only.** It runs on your own computer: peak memory 1.4 to 1.5 GB at the first answer, an install
  of about 1.8 GB, and 7 to 16 seconds to the first answer. A fresh start downloads about 0.5 GB of model weights.
- **The hosted app shows precomputed examples.** It does not run retrieval, because the free hosting tier does not
  guarantee the memory and CPU that live mode needs.
