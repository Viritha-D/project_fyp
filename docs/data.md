# Data

## Git LFS: what is in it and why

**On this branch (`claude/magical-pascal-uxsxvk`), nothing is in Git LFS.** `git lfs ls-files` lists no file. Every
file, including the `.npy` embeddings and the CSV masters, is stored as ordinary git content. The branch's
`.gitattributes` holds no LFS rule. It only pins the files the app reads as plain blobs (see "Files the app reads"
below).

**On `main`, LFS covers `*.pdf`, `*.zip` and `*.csv`.** It holds 12 files:

- `2023-fyp.pdf` (136 MB);
- one reference PDF;
- ten v1-era CSVs, among them `master_dataset_clean.csv`, `papers_master_with_matching_text.csv` and
  `paper_to_entity_map_final.csv`.

The 136 MB PDF exceeds GitHub's 100 MB per-file limit, so it has to be in LFS.

**Why the frozen files stay as plain git.**

- **Exact bytes are needed.** The frozen system is checked by sha256 of the exact file contents
  (`retrieval_v2/evaluation/FROZEN_HASHES*.txt`).
  - A checkout without `git lfs` installed gives pointer files instead of the data, so the check fails.
  - Moving the existing files into LFS needs `git lfs migrate`, which rewrites history. The project rules forbid that.
- **The files are small enough.** The largest tracked file is `paper_embeddings.npy` (34 MB), below GitHub's limit.
  The whole `.git` directory of this branch is about 31 MB packed.

**Rule for new files.** Add any new file above 50 MB through LFS with a new `.gitattributes` rule. Never migrate files
that are already tracked.

## Files the app reads (independent of Git LFS)

**How the list was measured** (2026-11-15). Both modes were run headless in a scratch clone, with every file open
logged twice: by a Python audit hook (`open` events) and by `strace -e openat`. A browser then drove each run:

- **cloud (precomputed) mode:** loaded the page and opened all six gallery examples;
- **live mode:** did the same, then asked three questions: the audit's constrained question (which triggers the
  fallback and writes to the store), a timetabling question and an off-topic question.

Python's bytecode cache was cleared and disabled, so every imported source file was logged. The two loggers agreed on
every file. The result is below; MB = 10^6 bytes.

| mode | data files | size | code files in the repository |
|---|---|---|---|
| cloud (precomputed) | 4 | 0.1 MB | 3, plus the entry point `app.py` |
| live | 20 | 74.7 MB | 17 |

| path | size | cloud | live | frozen | `git lfs ls-files` |
|---|---|---|---|---|---|
| `app/demo_inputs.json` | 2.5 KB | yes | yes |  | not tracked |
| `app/gallery.json` | 81.6 KB | yes | yes |  | not tracked |
| `app/site_data.json` | 8.3 KB | yes | yes |  | not tracked |
| `entity_embeddings_v2.npy` | 9.83 MB |  | yes | yes | not tracked |
| `entity_ids_order_v2.txt` | 22.4 KB |  | yes | yes | not tracked |
| `entity_notes_v2.json` | 5.65 MB |  | yes | yes | not tracked |
| `entity_to_family_v5.csv` | 0.41 MB |  | yes | yes | not tracked |
| `families_v5.json` | 1.60 MB |  | yes | yes | not tracked |
| `family_notes_v5.json` | 4.96 MB |  | yes | yes | not tracked |
| `paper_embeddings.npy` | 34.84 MB |  | yes | yes | not tracked |
| `paper_to_entity_map_v2.csv` | 3.23 MB |  | yes | yes | not tracked |
| `papers_master_with_matching_text_v2.csv` | 10.37 MB |  | yes | yes | not tracked |
| `problem_entities_enriched_v2.json` | 3.64 MB |  | yes | yes | not tracked |
| `retrieval_v2/RESULTS.md` | 43.3 KB |  | yes |  | not tracked |
| `retrieval_v2/config.json` | 1.0 KB |  | yes | yes | not tracked |
| `retrieval_v2/evaluation/FROZEN_HASHES_v23.txt` | 2.1 KB | yes | yes |  | not tracked |
| `retrieval_v2/v21_model.json` | 1.2 KB |  | yes | yes | not tracked |
| `retrieval_v2/v22/v22_selection.json` | 1.4 KB |  | yes | yes | not tracked |
| `selflearn/store/learned.jsonl` | 0.9 KB |  | yes |  | not in git yet (created by the first local suggestion) |
| `selflearn/threshold.json` | 0.9 KB |  | yes |  | not tracked |
| `app/core.py` | 12.7 KB | yes | yes |  | not tracked |
| `app/live.py` | 3.7 KB |  | yes |  | not tracked |
| `app/streamlit_app.py` | 14.2 KB | yes | yes |  | not tracked |
| `retrieval_v2/evaluation/evaluate.py` | 15.2 KB |  | yes | yes | not tracked |
| `retrieval_v2/hybrid.py` | 7.4 KB |  | yes | yes | not tracked |
| `retrieval_v2/recommend_v21.py` | 9.2 KB |  | yes | yes | not tracked |
| `retrieval_v2/recommend_v23.py` | 2.3 KB | yes | yes | yes | not tracked |
| `retrieval_v2/v21.py` | 10.0 KB |  | yes | yes | not tracked |
| `retrieval_v2/v22/blend.py` | 0.8 KB |  | yes | yes | not tracked |
| `selflearn/__init__.py` | 0.5 KB |  | yes |  | not tracked |
| `selflearn/extract.py` | 7.3 KB |  | yes |  | not tracked |
| `selflearn/fallback.py` | 3.6 KB |  | yes |  | not tracked |
| `selflearn/matcher.py` | 5.4 KB |  | yes |  | not tracked |
| `selflearn/profiles.py` | 4.5 KB |  | yes |  | not tracked |
| `selflearn/schema.py` | 2.8 KB |  | yes |  | not tracked |
| `selflearn/store.py` | 5.9 KB |  | yes |  | not tracked |
| `selflearn/trigger.py` | 1.8 KB |  | yes |  | not tracked |

**Read only under a condition** (found by static search, not opened in either run):
`retrieval_v2/evaluation/queries_t*`. The test-query guard in `app/core.py` reads these files only if
`retrieval_v2/RESULTS.md` has no "Independent test" section. It has one, so the guard is inactive.

**No LFS-tracked file is needed, so no copy was made.** None of these files is tracked by Git LFS on this branch, so
nothing was copied to `app/data/`. Frozen files stay where they are.

**`.gitattributes` keeps them plain blobs.**

- Only files that `main`'s LFS patterns (`*.pdf`, `*.zip`, `*.csv`) would match get a rule. Of the files the app
  reads, those are the three frozen CSVs (`entity_to_family_v5.csv`, `paper_to_entity_map_v2.csv` and
  `papers_master_with_matching_text_v2.csv`) and `retrieval_v2/evaluation/queries_t*.csv`. Each rule is
  `-filter !diff !merge`.
- The other 40 paths the app reads (`.py`, `.json`, `.md`, `.npy`, `.txt`, `.jsonl`, `.xlsx`, `.docx`) match no LFS
  pattern, so they need no rule.
- `git check-attr filter` gives `unset` for the 8 matched paths.
- `!diff !merge` leave diff and merge at git's defaults, so `git diff` shows normal text.
- If `.gitattributes` is combined with `main`'s LFS lines, these rules must come **after** those lines: later lines
  win.

**Simulation of `main`'s rules** (scratch clone, not pushed):

1. `main`'s three LFS lines were placed first, and `git add --renormalize .` was run with the LFS filter configured.
2. 85 CSVs that the app does not read became LFS pointers (for example `paper_index.csv` and
   `retrieval_v2/evaluation/folds.csv`).
3. None of the 48 app paths did, and every tracked app file's blob stayed byte-identical to HEAD.
4. A scratch edit showed `git diff` printing normal text, both for `app/core.py` and for `entity_to_family_v5.csv`.

**Merging `main` into this branch** (`git merge --no-commit --no-ff origin/main` in a scratch clone, then aborted):

- **Three add/add conflicts:**
  - `.gitattributes`;
  - `README.md`;
  - `master_dataset_clean.csv`. It is plain here and an LFS pointer on `main`, with the same content hash. The app
    does not read it.
- `main` adds only two PDFs and changes no file the app reads. After the merge, every app file in the index is a plain
  blob, identical to this branch.
- **Resolve `.gitattributes` with `main`'s lines first.** Kept in conflict-marker order (this branch's lines first),
  `main`'s `*.csv filter=lfs` wins, and staging the 8 app CSVs turns all 8 into LFS pointers. With `main`'s lines
  first, it turns 0 of 8 into pointers.

**Clean-clone test** (`app/tools/lfs_proof/`):

1. `GIT_LFS_SKIP_SMUDGE=1 git clone` of origin, then a checkout of this branch.
2. A fresh Python 3.13.18 virtualenv, with `pip install -r requirements.txt` (streamlit, pandas, numpy; no torch).
3. The app was run headless in cloud mode with `streamlit run app.py`. The page loaded, and all six gallery examples
   were opened.
4. Result: the app opened 1,434 regular files, 9 of them inside the clone. **None starts with
   `version https://git-lfs.github.com/spec`.** As a negative control, the checker fails when it is given a real
   LFS pointer from `main`.

## Frozen data files (repository root)

They are fixed by `retrieval_v2/evaluation/FROZEN_HASHES.txt` and `FROZEN_HASHES_v23.txt`. Do not edit, move or
reformat them: frozen code reads them from the root.

| file | size | content |
|---|---|---|
| `papers_master_with_matching_text_v2.csv` | 9.9 MB | 11,342 benchmark records (1,488 papers) with structured fields and matching text |
| `paper_embeddings.npy` | 34 MB | all-mpnet-base-v2 vectors of the records' matching text |
| `problem_entities_enriched_v2.json` | 3.5 MB | 3,199 problem entities |
| `entity_embeddings_v2.npy` | 9.4 MB | entity vectors |
| `entity_ids_order_v2.txt` | small | row order of `entity_embeddings_v2.npy` |
| `entity_notes_v2.json` | 5.4 MB | per-entity notes |
| `paper_to_entity_map_v2.csv` | 3.1 MB | record → entity |
| `families_v5.json` | 1.6 MB | 2,173 benchmark families (v5) |
| `entity_to_family_v5.csv` | 399 KB | entity → family |
| `family_notes_v5.json` | 4.8 MB | per-family notes |

The frozen code and evaluation files in `retrieval_v2/` are listed in the same hash files.

**Other result files stay unedited too:**

- `retrieval_v2/evaluation/scored_queries_final.csv`;
- `report_final.md`;
- `results_final.json`;
- `FROZEN_ENV.txt`.

## Other data at the root (not frozen)

| file | why it is at the root |
|---|---|
| `papers_master_v2.csv`, `master_dataset_clean.csv` (7.7 MB each) | the source master and its byte-identical copy (`docs/data_notes.md`). The data-build scripts in `scripts/data/` read them, and they stay at the root by decision (`docs/REPO_PLAN.md`). |
| `paper_index.csv` | one row per paper (1,488). Frozen `retrieval_v2/config.json` names it at the root, and `v2_entities_pipeline.py` reads it. |
| `backup_v1/`, `backup_v2/` | inputs that `v2_entities_pipeline.py` reads when frozen `evaluate.py` rebuilds the fold indexes |

## Evaluation data (`retrieval_v2/evaluation/`)

| file | role |
|---|---|
| `folds.csv`, `folds_seed43.csv` | the five-fold paper splits |
| `queries_auto.csv` | the automatic masked queries |
| `queries_v2.csv` / `.xlsx` | 55 written development queries (a selection set) |
| `queries_t1.csv`, `queries_t3.csv`, `queries_t4.csv` (+ `.xlsx`, `t3_resolved`, `t4_original.docx`) | the independent test sets, scored once |
| `queries_t2.csv` | rejected at intake (amendment 1) |
| `families_for_writers.*`, `families_browse.csv` | the family list given to the query writers |
| `PROVENANCE.md`, `PROVENANCE_t.md` | where the query sets came from; self-reported, not verified |

## Fallback module data (`selflearn/`)

| file | role |
|---|---|
| `threshold.json` | the low-confidence threshold and how it was chosen |
| `holdout_check.csv`, `review_pack.csv`, `review_pack_key.csv` | descriptive hold-out output and the blind review pack |
| `store/learned.jsonl` | the learned store; tracked in git, not LFS; created on the first live suggestion, empty so far |

## Archived data (`archive/`)

The v1 and intermediate data layers (family layers v2 to v4, v1 entity maps, ingest logs, review files) are in
`archive/`. No live code reads them. See `archive/README.md`.

## Provenance of the papers

The records were extracted from conference papers (GECCO 6,450 records, CEC 3,675, PReMI 658, FOGA 467, PPSN 92; the Conference column).

- Part of the extraction code (three modules of the Gemini-based GECCO/PPSN extractor) is in `scripts/extraction/`.
- The validation steps are in `scripts/data/` and `docs/data_notes.md`.
- No paper has a DOI or URL in the data (`docs/limitations.md`).
