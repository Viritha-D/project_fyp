# Pre-registration of the final test: amendment 3

This amends `PREREGISTRATION_final.md` (cf15185), amendment 1 (1b3a188) and amendment 2 (d180627). All their rules
stand except where this amendment says otherwise. In particular:

- the whole-query validity rule and the 25% set rule (amendment 1);
- the primary claim, its paired bootstrap with 10,000 resamples and seed 42, and the MRR blend decision on the pooled
  valid rows (amendment 1);
- `FROZEN_HASHES.txt` must match before scoring (amendment 1);
- the duplicate rule (amendment 1);
- names-only resolution with `resolve_gold_names.py` (amendment 2);
- the single scoring event (amendment 2);
- honest reporting below 40 queries (amendment 2);
- error causes for every system (amendment 2).

It was committed before `queries_t3.xlsx` and `queries_t4_original.docx` were added to the repository, and before any
scoring. The frozen system (tag `retrieval-v2.2`, commit 6c81556) and every model, data file and result are unchanged.

## 1. Sets

| set | file | form | status |
|---|---|---|---|
| t1 | `queries_t1.xlsx` | ids + names | accepted (amendment 1) |
| t2 | `queries_t2.xlsx` | ids + names | rejected, 100% invalid (amendment 1). Excluded from every analysis. |
| t2b | `queries_t2b.xlsx` | names-only | reserved for the t2 writer's hand redo. Counts only if committed alone before scoring. |
| t3 | `queries_t3.xlsx` | names-only, from `submission_template.xlsx` | to be committed alone, then validated |
| t4 | `queries_t4_original.docx` (submitted as `queries_benchmarks.docx`) by Sanjesh Nandha K | ids + names, Word table | to be committed alone in its original form, then converted (section 2) |
| t5 | any later set | - | counts only if committed alone before the scoring date |

**Why t3 and t4.** Two writers were both told to save their file as `queries_t3.xlsx`. The names t3 and t4 were
assigned to tell the two files apart.

## 2. Conversion of t4

`convert_t4_docx.py` writes `queries_t4.xlsx` and `queries_t4.csv` from the docx table.

- **Text copied verbatim.** It copies every cell's text verbatim.
- **The one change.** Names that are separated by newlines inside a `gold_family_names` cell become `;`-separated.
  No other cell content is changed.
- **Extra column `group_norm`.** It is added next to the untouched original `notes`:
  - `Theory` → `theory / algorithm analysis`
  - `applied` → `applied / real-world`
  - `unusual / niche` → unchanged
- **Round-trip check.** It must show that every original cell is unchanged, apart from the newline rule in
  `gold_family_names`. If the check fails, the conversion is not used.

## 3. Validation

- **t3:** validated by amendment 2. Names-only; ids are resolved by `resolve_gold_names.py`.
- **t4:** validated by amendment 1, because it has ids and names (rule (a)-(c)).
  - `resolve_gold_names.py` is also run on t4's names, as an information-only cross-check. It does not decide
    validity.
- **Both:** the whole-query rule and the 25% set rule apply exactly as written. Nothing is repaired.

## 4. Provenance and AI use

Each set needs the writer's own statement on two points:

1. Did any AI tool write or suggest queries, ids or family names?
2. Which tools were used?

The statements are recorded verbatim in `PROVENANCE_t.md`.

- **AI use for content.** A set whose writer reports AI use for the queries, or for choosing families, is excluded
  from the PRIMARY pooled analysis. It is reported separately, as a sensitivity analysis.
- **AI use for the file only.** AI used only to format or create the file container, with no content choices, is
  recorded. It does not exclude the set.
- **No statement.** A set without a statement by the scoring date stays in the primary analysis, flagged
  **"provenance not stated"**. The report then adds a sensitivity analysis that drops every set with no statement or
  with reported AI use.

## 5. Corpus-closeness diagnostic

This is descriptive only and excludes nothing.

- **Measure.** For each set, including queries_v2 and t1: the maximum dense cosine (all-mpnet-base-v2) between each
  query and the `matching_text` of all papers. It is reported as a distribution per set.
- **Reason.** The t4 writer says the queries were drafted from research papers, so they may track papers in the
  corpus.

## 6. Scoring date

Unchanged from amendment 2: **not yet fixed**. The request for this amendment contained the unfilled placeholder
"[KEEP the date in amendment 2 / NEW DATE, TIME IST]". Amendment 2 had no date, so keeping it means the date is still
unset.

- It will be fixed in a further amendment, committed before any scoring.
- No scoring takes place before that amendment exists.
- Everything else in amendment 2 stands.

## 7. Disclosure

This amendment was written after both files were received and after their query text was read. No system output has
been seen on them.

**Why the AI-use rule was added.** t4 reports Copilot use for the Word document, and t3 has no provenance yet. The
rule depends on statements, not on any result.

**Factual note on authorship.** The session that wrote this file did not have the two files: the attachments did not
reach it. Its author (Claude) had therefore not read their query text. The user had.

## 8. Expectation

With t1, t3 and t4 accepted, the pooled n is up to 60 and the hit@5 interval is about ±0.12. The report states the
actual n. Amendment 2's reporting rule for fewer than 40 valid queries still applies.
