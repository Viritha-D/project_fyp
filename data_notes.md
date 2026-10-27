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
- Across files, 3 title pairs where one title extends the other were found; 1 is proposed
  as "same paper, title variants" (`353_paper.pdf` / `359_paper.pdf`, "Fast Convergence to
  Near Optimal Solution for Job Shop Scheduling ...", same authors and Problem_Context),
  2 are "unclear". Note that this pair's Problem_Context (DC-DC buck converter design)
  does not match its title.
- Nothing is merged yet. Decisions go in the `my_decision` column of
  `premi2023_review.csv`. If the one proposed merge is accepted the count becomes 1,493.

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
  90 of the 92 v2 rows match them, PPSN_2018 grew from 13 to 15 rows). No raw PPSN PDF or
  CSV, extraction script or notebook exists in any branch or commit of this repository.
- No titles are invented and no file is split.

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
