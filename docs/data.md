# Data

## Git LFS: what is in it and why

**On this branch (`claude/magical-pascal-uxsxvk`), nothing is in Git LFS.** There is no `.gitattributes`, and every
file, including the `.npy` embeddings and the CSV masters, is stored as ordinary git content.

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

- The extraction prompts and scripts are in `scripts/extraction/`.
- The validation steps are in `scripts/data/` and `docs/data_notes.md`.
- No paper has a DOI or URL in the data (`docs/limitations.md`).
