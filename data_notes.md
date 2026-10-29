# Data notes: master v2

Source: `master_dataset_clean.csv` (11,342 rows x 29 columns), frozen unchanged as
`papers_master_v2.csv`. Derived data lives in `paper_index.csv`,
`papers_master_with_matching_text_v2.csv` (29 columns + 4 Part 2 columns) and the review
files; no original master value is ever edited.

## Paper identity

- A paper is `paper_key = Conference|Year|normalised title` (title lowercased, only
  letters and digits kept). There are **1,494 papers** (`paper_index.csv`).
- An untitled paper (title "Not Reported") is keyed `Conference|Year|Source_File|untitled`,
  so untitled papers are never merged with each other. 101 untitled rows form 38 papers,
  all PReMI; each key holds exactly one Paper_ID root (asserted in `v2_step1_validate.py`).
- `Paper_ID` is the unique row identifier (`P<Year>_<Conference>_<NNN>_Ext_<NN>`).
- `Original_Paper_ID` is a per-file extraction counter that restarts for every source
  (`Paper_001`, `Paper_002`, ...). It is **never a key**: 246 of its 388 roots occur under
  more than one Conference or Year (245 across conferences).
- `Source_File` alone is never a key: generic names such as `018_paper.pdf` carry
  several papers.

## PReMI 2023 caveat

- 267 rows, 67 Source_Files, 107 real titles plus 17 untitled papers (50 rows).
- 59 papers are flagged `source_file_has_multiple_titles`, all in two files:
  - `018_paper.pdf`: 57 titles, each with different authors and its own contiguous Paper_ID
    block. Classified "multi-paper, contiguous": one file name was reused for 57 papers;
    one paper_key per title is kept.
  - `289_paper.pdf`: 2 different titles by the same author ("M. Das") with different
    Problem_Contexts. Classified "unclear".
- Across files, 3 title pairs where one title extends the other were found. 2 are
  proposed as "same paper, title variants": `353_paper.pdf` / `359_paper.pdf` ("Fast
  Convergence to Near Optimal Solution for Job Shop Scheduling ...", same authors and
  Problem_Context, though that context, DC-DC buck converter design, does not match the
  title, and neither copy is in the 2023 proceedings), and the Document Similarity pair
  below. The EEG pair (different authors and contexts) stays "unclear".
- **Checked against the real proceedings.** `2023-fyp.pdf` (Git LFS, on `main`) is the
  PReMI 2023 proceedings, Springer LNCS 14301, 892 pages, 91 papers
  (`premi2023_proceedings_toc.csv`, built by `v2_partD_premi2023_proceedings.py` from the
  PDF bookmarks, first-page author lines and running heads). Of the 107 titled
  "PReMI 2023" papers in the master only **22** are in it: 12 by exact title and 10 by the
  paper's running head (the short title printed on its pages). The other **85** titles do
  not occur anywhere in the volume's text. 56 of the 57 titles in `018_paper.pdf` are not
  2023 papers. So most rows labelled PReMI 2023 come from other PReMI volumes, and their
  Year is not reliable. Per-paper results: `premi2023_proceedings_check.csv`.
- 7 PReMI papers labelled 2020, 2021 or 2022 are in the 2023 proceedings with a shared
  author; 3 of them are short-title copies of a 2023 paper_key ("Identifying a Person in
  Mask", "Elephant Swarm Water Search Algorithm (LESWSA)", "A GE Based Automated
  Configuration of an Ensemble DE Algorithm").
- One proceedings paper appears twice in 2023 under its full title and its running head:
  `679_paper.pdf` / `687_paper.pdf` ("Front Generation Using Pivots", Mandal and Dutta).
- The "Document Similarity" pair (`018_paper.pdf` / `023_paper.pdf`) is one paper: both
  titles match the same proceedings paper (pp. 37-45, Dey, Jenamani, De).
- Proposed merges (none applied): Fast Convergence pair, Document Similarity pair, Front
  Generation pair and the 3 other-year copies above, i.e. 6 merges: 1,494 papers would
  become **1,488**. **Approved and applied** (2026-10-28) to `paper_index.csv` only, by
  `v2_apply_paper_decisions.py`: 1,488 papers; absorbed keys are listed in `merged_keys`.
- `paper_index.csv` flags `year_unverified` on the 84 paper_keys (85 titles, one absorbed
  by a merge) of titled PReMI 2023 papers not found in the proceedings; no Year is changed.
- The PReMI extraction scripts (said to be in a zip) are not in any branch or commit.

## PPSN caveat

- 92 rows in 5 Source_Files, one per year (2016, 2018, 2020, 2022, 2024); each file has
  one title, one author list and one Original_Paper_ID root, so each is one paper_key now.
- `PPSN_2020-compressed.pdf` and `PPSN_24.pdf` carry the proceedings name as their title
  ("Parallel Problem Solving from Nature – PPSN XVI" / "XVIII") and editor-style author
  lists: flagged `whole_proceedings_suspect` in `paper_index.csv`.
- The other three files mix several Problem_Contexts: flagged `mixed_context`.
- ESTIMATE (distinct Problem_Context per file, a heuristic only): 22 underlying papers in
  the 5 files (5 + 7 + 4 + 3 + 3). See `ppsn_review.csv`.
- Origin: the same 5 files were already in the first commit of the old master (90 rows;
  90 of the 92 v2 rows match them, PPSN_2018 grew from 13 to 15 rows). They were
  extracted with the Gemini pipeline now in `extraction/gecco_pipeline/`. It returns one
  `metadata` block (title, authors, year) per PDF and, for PDFs over 200 pages, merges
  the extractions of all 200-page parts under the first part's metadata. So the title and
  authors on every PPSN row describe the whole PDF, not the paper the row came from. The
  PPSN PDFs are not in the repository, so the paper behind each row cannot be checked.
- No titles are invented and no file is split. Each PPSN file counts as one paper and is
  flagged `ppsn_partial` in `paper_index.csv`.

## Repeated rows

835 rows repeat the title + Benchmark_Name + Algorithm_Name + Evaluation_Dataset of an
earlier row (464 groups, 1,299 rows including the first of each). None is an exact
duplicate: every group differs in at least one other column, mostly Environment (373
groups), Dimensionality (365), Max_Evaluations_or_Generations (175) or Performance_Metric
(112). They are legitimate runs at different dimensions, budgets or metrics, so **all are
kept**.

## Matching text (Part 2)

- Recipe (`part2_matching_text.py`, unchanged): Applied rows use
  "Problem_Context. Paper_Title"; Pure Math rows use
  "Benchmark_Name. Target_Landscape. Landscape_Characteristics"; "Not Reported" parts are
  dropped.
- **119 title_suspect rows** (101 untitled, 18 with titles under 3 words) never use the
  title; for Applied rows (71 of the 119) the text is Problem_Context only.
- 5 rows (2 CEC 2023 papers, Portuguese) are translated; the English text is reused from
  the old master, `matching_text_original` keeps the Portuguese, `language` = `pt`.
- Every row has matching_text with at least 3 alphanumeric characters (asserted).

## Gold labels

`gold_standard_labels_remapped.csv` (40 rows, supplied by the user): every `new_Paper_ID`
is unique and exists in `papers_master_v2.csv`, and title, Benchmark_Name, Category and
Problem_Context are identical to the master on all 40 rows. The original
`gold_standard_labels.csv` is not in this repository.

## Problem entities (v2)

- Built by `python v2_entities_pipeline.py --stage all` (fidelity -> A -> B -> C); rules in
  `part4_rules.json`, reconstructed from `part4_methodology.md`. Name-key blocking does all
  the grouping; embeddings only pick each entity's medoid.
- Fidelity on the old 4,256-row master: name_key 100%, ARI/NMI 1.0 against the original
  Part 4 map (1,038 entities); Part 5 + enrichment + repairs reproduce the old
  `problem_entities.json` except 3 medoid tie-breaks.
- v2: 3,199 entities (3,187 single_function, 8 named_subset, 4 suite; Applied 1,765,
  Pure Math 1,434); 2,946 are supported by a single paper. Gold (38 labelled rows):
  ARI 1.0, NMI 1.0. `--series-split` splits CEC 2006 into a suite + 7 G functions; digit
  guard reports 0 cases.
- `entity_notes_v2.json`: one data-only note per entity (fixed template, no LLM text),
  with caveats single_paper (2,946), sparse_metadata (1,138), premi_year_unverified (94),
  ppsn_partial (47). E00657 "Evolutionary Algorithm" is kept but flagged
  extraction_artifact_suspect.

## Families (v2)

- `python v2_families.py`, rules in `family_rules_v2.json`: entities in one Category are
  grouped by equal name stem, equal library cue (rows' Dataset_Name / Source_Platform) or
  template names (>= 5 tokens, <= 2 token edits). Embedding similarity never merges
  (`family_candidates_v2.csv` lists pairs for review). Entities are unchanged.
- 2,136 families for 3,199 entities; records in families with >= 2 papers: 46.0% (26.3%
  at entity level). Known issues, reported not fixed: library cues chain unrelated
  functions (Sphere + Rastrigin via CEC 2013) and build very large families (UCI: 162
  entities); the template rule joins different CEC years; the software-bug HPO grid splits
  into 4 families; "Sharp Ridge (BBOB F13)" / "BBOB F13 (Sharp Ridge)" are not grouped.

## Families v3

- `python v3_families.py`, rules in `family_rules_v3.json`: one family key per entity
  (standard suite > stem > template > library cue > single), no union across rules. Suite
  and stem families may mix Categories; template keys require digit tokens to match.
- 2,027 families; records in families with >= 2 papers 46.7% (v2 46.0%). Suite families
  (ZDT, WFG, DTLZ, BBOB, CEC <year> ...) replace the chained v2 families; library cues are
  kept per entity as suite_memberships. `family_review_sample_v3.csv` is the sample to label
  (blind); the v2 sample is superseded.
