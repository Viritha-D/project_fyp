# Pre-registration of the final test: amendment 2

This amends `PREREGISTRATION_final.md` (cf15185) and `PREREGISTRATION_final_amendment1.md` (1b3a188). It was
committed before `queries_t2b.xlsx` or `queries_t3.xlsx` existed in the repository, and before any scoring. Where it
differs from the earlier documents, this amendment applies; everything else in them stands. The frozen system (tag
`retrieval-v2.2`, commit 6c81556) and every model, data file and result are unchanged.

## 1. File names

- `queries_t2b.xlsx` is the hand redo of t2. `queries_t3.xlsx` is the third set.
- Each is committed alone and unchanged (byte-identical to what is supplied), in its own commit, before validation.

## 2. Names-only submissions

**Format.** t2b and t3 are names-only. They use `submission_template.xlsx` (commit a4aab5d, sha256 e36cf516…f995):
columns `query_id`, `query_text`, `gold_family_names`, `notes`, with no id column and rows Q01-Q20.

**Resolving names to ids.** Ids are resolved by `resolve_gold_names.py` (commit a4aab5d, sha256 f4693738…fdd8).

- Each written name is matched exactly, after casefold and whitespace collapsing, against the family names in
  `families_v5.json`.
- The result goes to a separate CSV. The submitted file is never modified.

**Validity rule.** It is the same as in amendment 1.

- (c) holds by construction: each resolved id carries the name as written.
- (a) and (b) are checked by the resolver: the name must resolve to exactly one family, and that family must not be
  F02124 or F00334.
- A name that matches no family, or more than one, makes the whole query invalid. The name and the candidates are
  reported. Nothing is guessed.
- A query with no names is invalid.
- The amendment 1 set rule applies unchanged: more than 25% invalid rows means the set is rejected and returned to
  its writer.

**Ambiguous names (known in advance).** 13 family names in `families_v5.json` are shared by more than one family
(26 families in total), for example "mnist", "Evolution Gym", "cartpole", "madelon" and "BipedalWalker-v3". A
names-only query that uses one of them is invalid under this rule. Writers should be told this before they start.

**Submissions with ids.** A submission that contains ids is validated by amendment 1 instead. The resolver refuses
such a file.

## 3. Single scoring event

All accepted sets are scored together, once.

- **Date and time:** not yet fixed. The user left it unset on 2026-11-09. It will be fixed in a further amendment,
  committed before any scoring. No scoring takes place before that amendment exists.
- What is accepted by that date and time is the test. Nothing arriving later is added.
- Scoring goes ahead on that date even if t1 alone is accepted.

## 4. Honest reporting

If the pooled set has fewer than 40 valid queries:

- the report states the actual n and the width of the 95% interval;
- a "not supported" result is described as **inconclusive at that size**, not as evidence against the system.

## 5. t2 (original)

t2 is reported as **"rejected, 100% invalid"**, with the reason: every gold id's stored family name differs from the
name written next to it (`validation_t.md`). It is excluded from every analysis. t2b is a new submission and does
not inherit anything from t2.

## 6. Error causes for every system

For every scored system (primary and secondary) and every query that system misses (no gold family in its top 5), the
report gives the cause:

- **(a)** no gold family among the system's candidates. Candidates are the families the system ranks before any
  popularity padding:
  - stacked: its candidate families;
  - full v2: its shortlist roll-up;
  - blend 0.5: the union of those two lists;
  - popularity: all families, so (a) cannot occur for it.
- **(b)** a gold family is among the candidates but ranked below 5.
- **(c)** every gold family has fewer than 2 papers in the index. This is reported as a flag alongside (a)/(b), with
  the count of misses where at least one gold family has fewer than 2 papers.
