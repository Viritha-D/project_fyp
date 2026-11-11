# Pre-registration of the final test: amendment 6

This amends `PREREGISTRATION_final.md` (cf15185) and amendments 1 to 5 (1b3a188, d180627, 81384f4, 155ca81, b09e672).
Every rule of amendments 1 to 5 stands. This amendment changes only the scoring date and time. It was committed before
any scoring.

## 1. Scoring date and time

**12 November 2026 at 10:00 IST.**

- This replaces the date in amendment 5 (13 November 2026, at the start of the scoring run).
- Provenance statements for t1, t3 and t4 are due by this time.
- The test is whatever is accepted by then. Nothing arriving later is added.
- The procedure on the day is unchanged from amendment 5:
  1. verify `FROZEN_HASHES.txt` and the `FROZEN_ENV.txt` versions, stopping if either fails;
  2. score all accepted sets together, once;
  3. apply amendments 1 to 5.

## 2. Disclosure

- **The move.** The date was moved one day earlier, from 13 to 12 November, on project schedule.
- **No results seen.** At the time of this amendment, no system output or score on t1, t3, t4 or any other test set has
  been seen. This was checked before writing: there is no `scored_queries_final.csv` in any commit, no "Independent
  test" section in any version of `RESULTS.md`, and no results file for any t-set on any branch.
- **No dependence on results.** The change does not depend on any result.
- **Less time for statements.** The writers have one day less to send statements. Sets without a statement are handled
  by amendment 3, unchanged.

## 3. Everything else

Everything else stays as written, including:

- the frozen files (`FROZEN_HASHES.txt`, `FROZEN_ENV.txt`);
- the validity, duplicate and AI-use rules;
- the handling of relayed statements (amendment 5);
- the primary analysis and its decision rules;
- the sensitivity analyses (amendment 4) and the leave-one-writer-out descriptive analysis (amendment 5).
