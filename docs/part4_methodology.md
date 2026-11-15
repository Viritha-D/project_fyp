# Part 4 Output — Entity Resolution & Clustering
### Canonical file: `paper_to_entity_map_final.csv`

**Status: pipeline complete, logic validated on known test cases, NOT yet validated against a real independent gold-standard sample.** This document explains exactly what was done and how, so your team can check the reasoning itself rather than trusting the output blindly.

---

## Result summary

- **Input:** 4,256 papers (`papers_main_master.csv`, Categories: Pure Math 2,777 / Applied 1,479)
- **Output:** 1,035 candidate problem entities
  - 865 base entities (from name-key blocking)
  - 170 additional entities created by splitting 2 mixed suite/sub-function groups
- **Zero missing entity_id values.** Every paper is assigned.

---

## Method: deterministic name-based blocking (not embedding clustering)

**Why not pure embedding clustering (the original plan):** it was tried first and failed a real test — CEC 2017 fragmented into ~26 separate entities because different papers described the suite with different companion text (different function subsets tested), even though they're the same suite. Embeddings correctly saw the text as different; a human wouldn't. See "Known limitation" below for the one case where this fallback still matters.

**What was used instead:**
1. Normalize `Benchmark_Name` (lowercase, strip filler words like "suite"/"benchmark"/"the")
2. **Special-cased CEC-suite detection:** any `"CEC <year>"` phrasing (in either word order, any suffix wording) collapses to a single canonical key `cec_<year>`. Different years stay distinct (`cec_2014` ≠ `cec_2017`).
3. Papers sharing `(Category, normalized_name)` become one entity — regardless of any text differences elsewhere in their description.
4. Embedding-based clustering was kept as a fallback for rows with no usable `Benchmark_Name` — in practice this never triggered, since every row in this dataset had one.

## Suite / single-function hierarchy split

After step 3, some entities mixed suite-level papers (e.g. `"CEC 2017 Suite"`) with per-function papers (e.g. `"CEC2017 F1 (Bent Cigar Function)"`) under the same name key. These were split: the suite-level papers keep the original entity as `entity_type = "suite"`; each distinct function number gets its own new child entity with `entity_type = "single_function"` and `parent_benchmark_id` pointing back to the suite.

**A bug was found and fixed during this step:** the first version used the regex `\bF\d+\b` to detect function numbers, which incorrectly matched range notation like `"F1-F10"` (a suite-level description of a range) as if it were describing single function "F1". This falsely split ~47 rows across the dataset. Fixed by explicitly excluding range patterns (`F\d+-F\d+`, `F1, F3-F30`, etc.) before applying single-function detection. Verified against all 6 affected suite entities (CEC 2013, 2014, 2017, 2020, 2021, 2022), not just the original CEC 2017 case.

---

## Known limitation — not fixed, deliberately deferred

**Problem-family variants are not merged.** Cases where papers describe the same real-world problem but with a different parameter baked into the name itself (e.g. `"...3 Underwater Vehicles"` vs `"...10 Underwater Vehicles"`) remain as separate entities, since name-blocking treats different names as different entities.

Quantified scope: **187 papers (17 groups)** are genuine small parameter-variant families that should likely be merged in Part 5. A further 325 papers (`MSTSP1-25`, `RWMOP1-35`) look superficially similar but are actually large structured series — the same pattern as CEC's F1-F30 — and should get the suite/child treatment above, not simple family-merging. Do not casually merge these two patterns the same way; they need different handling in Part 5.

---

## How to actually validate this (the step still pending)

1. **Fill in `gold_standard_template.csv`** (already generated, 40 papers, stratified across both categories with 16 deliberately hand-picked near-miss/edge cases — see the file for exactly which papers and why). Your team assigns real `entity_id` values by reading each paper's context and judging which ones describe the same problem. Mark genuinely unclear cases as `uncertain` rather than guessing.
2. **Run `validate_clustering.py`** — already written and pointed at `paper_to_entity_map_final.csv` and `gold_standard_labels.csv` (your team's real file, once produced). It outputs Adjusted Rand Index and Normalized Mutual Information, plus an automatic example of any group the algorithm split apart, for your report's error-analysis section.
3. **Do NOT reuse `gold_standard_labels_PLACEHOLDER.csv`** for this — it's AI-generated, explicitly marked as illustrative, and was only ever meant to demo the pipeline mechanism to your professor before real labeling starts.
4. If ARI/NMI comes back weak, the most likely places to look first, based on everything found so far: (a) whether other suite-like series beyond CEC exist that need the same special-casing, (b) whether the 17 small-family groups are being incorrectly treated as separate when your team's judgment says they shouldn't be.

Once validated, this file is the direct input to Part 5 (entity record building) — no changes to Part 4's logic should be needed unless validation reveals a real problem.
