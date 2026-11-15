# Pre-registration of the final test: amendment 5

This amends `PREREGISTRATION_final.md` (cf15185) and amendments 1 to 4 (1b3a188, d180627, 81384f4, 155ca81). Every rule
of amendments 1 to 4 stands, except that this amendment fixes the scoring date and says how a relayed provenance
statement counts. It was committed before any scoring. No system has been scored on t1, t3 or t4.

## 1. Scoring date

**13 November 2026, IST**, as given by the user ("13/11/26").

- **No time given.** The user gave no time of day. The cut-off is therefore the start of the scoring run on
  13 November 2026 (IST). The report records that start time.
- **What counts.** Sets accepted by the cut-off, and provenance statements received by it, are the test. Nothing
  arriving later is added.
- **Order of steps on the day.**
  1. Verify `FROZEN_HASHES.txt` and the `FROZEN_ENV.txt` versions; stop if either fails.
  2. Score all accepted sets together, once.
  3. Apply amendments 1 to 4.

## 2. Provenance at the time of writing

| set | writer | AI-use statement | effect under amendment 3 |
|---|---|---|---|
| t1 | "Sanjesh Nandha" (given by the user) | none | primary analysis, flagged "provenance not stated" |
| t3 | "Adarsh Prakash" (given by the user) | none | primary analysis, flagged "provenance not stated" |
| t4 | Sanjesh Nandha K | relayed by the user: "sanjesh todl that copilot was only used for formatting the content and it dod not modify or edit anything" | see section 3 |

## 3. How a relayed statement counts

- **It counts as a statement.** A statement passed on by the user, rather than written by the writer, counts as a
  statement. It is recorded verbatim and marked "relayed".
- **t4's statement means formatting-only use.** It says AI (Copilot) was used only to format, and changed no content.
  So t4 stays in the primary analysis, and it qualifies for sensitivity analysis (d) of amendment 4.
- **Its limits are reported.** The report notes that t4's statement is relayed. It also notes that the statement
  speaks only about Copilot, and does not say whether any other AI tool wrote or suggested queries, ids or family
  names.
- **A later statement replaces it.** If the writer's own statement arrives before the cut-off and differs, the
  writer's own statement is used instead. The amendment 3 rules are then applied to it.

## 4. Disclosure

**Same writer for t1 and t4.** Per the user, Sanjesh Nandha wrote both t1 and t4. The two sets share 5 gold families
(`validation_t34.md`). No rule is changed for this. The amendment 4 leave-one-set-out analysis (b) and the cluster
bootstrap (c) over shared gold families already show how much the result depends on them. The report also gives
leave-one-writer-out, descriptively: once without t1 + t4, and once without t3.

**When this was written.** This amendment was written after the sets were validated and their query text read. No
system output on t1, t3 or t4 has been seen.
