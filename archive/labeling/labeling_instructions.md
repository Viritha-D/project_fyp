# Labelling instructions: same benchmark family?

You will label 80 pairs of benchmark problems in `family_review_sample_v3_blind.csv`.
Work alone and do not discuss pairs with anyone until you are done.

## What you see

Each row is one pair, **a** and **b**. For each side:

- `name_*`: the benchmark name used in the papers
- `aliases_*`: up to 5 other names papers used for the same benchmark (separated by `|`)
- `category_*`: Pure Math (synthetic / mathematical benchmark) or Applied (real-world problem)
- `venues_*`: conferences where it appears, with the number of papers
- `sample_problem_contexts_*`: up to 2 task descriptions taken from the papers (separated by `|`)

Rows are in random order. Nothing in the file tells you how the pair was chosen.

## The question

Label y if a researcher choosing benchmarks would treat the two as members of the same benchmark series, suite, repository or experimental grid, so recommending one makes the other a plausible alternative from the same set. Label n if they are different benchmarks that only share a topic or a word. Two datasets from the same repository are y only if their task type is also similar (both classification, both feature selection); different task types are n. Use unsure when you cannot tell from the shown fields. Do not look anything up.

## How to fill it in

- Write exactly one of `y`, `n` or `unsure` in `same_family (y/n/unsure)` for every row.
- Use `notes` for a short reason when the call was hard, or when you chose `unsure`.
- Judge only from the fields shown. Do not search online, open papers or ask anyone.
- Do not change any other column, and do not sort, add or delete rows.
- When finished, save the file as CSV (UTF-8) under the same name and return it.

## Examples of the distinction (not taken from the file)

- DTLZ1 and DTLZ3: **y** (same suite).
- Two UCI classification datasets: **y**; a UCI classification dataset and a UCI regression
  dataset: **n** (same repository, different task type).
- "Vehicle routing with drones" and "Vehicle routing with time windows" from unrelated papers:
  usually **n** unless the fields show they come from one benchmark set or grid.
