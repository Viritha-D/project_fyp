# Build scripts

These scripts built the knowledge base. They are kept for provenance, not as part of the live system: the app and the
frozen retrieval code in `retrieval_v2/` do not import them. Their paths were updated when they moved here (2026-11-15,
`docs/REPO_PLAN.md`). That update was checked statically: every file compiles, and every path they named before still
exists. They were **not re-run**.

**Do not re-run a script that writes a frozen file.** Its output would change the bytes that
`retrieval_v2/evaluation/FROZEN_HASHES*.txt` fix, and the frozen system would no longer verify. These are marked
**writes frozen** below.

## `data/`: records, masters and paper embeddings

| script | builds | note |
|---|---|---|
| `ingest.py` | v1 master `archive/legacy_v1/data/papers_master_with_matching_text.csv`, ingest logs in `archive/ingest_logs/` | v1 era |
| `part2_matching_text.py` | matching text for new v1 master rows | v1 era |
| `v2_step1_validate.py` | `papers_master_v2.csv`, `paper_index.csv`, `docs/audit_report.md`, from `master_dataset_clean.csv` | overwrites the root master and paper index |
| `v2_partA_premi2023.py` | `archive/data_review/premi2023_review.csv` | read-only on the master |
| `v2_partB_ppsn.py` | `archive/data_review/ppsn_review.csv` | read-only on the master |
| `v2_partD_premi2023_proceedings.py` | `archive/data_review/premi2023_proceedings_*.csv` | needs `2023-fyp.pdf`, which is in LFS on `main` only |
| `v2_apply_paper_decisions.py` | `paper_index.csv` (reviewer decisions applied) | overwrites the paper index |
| `v2_step2_matching_text.py` | `papers_master_with_matching_text_v2.csv` | **writes frozen** |
| `v2_step3_embed_papers.py` | `paper_embeddings.npy`, `paper_ids_order.txt` | **writes frozen** |

The entity layer (`problem_entities_enriched_v2.json`, `entity_embeddings_v2.npy` and the other entity files) is built
by `v2_entities_pipeline.py`. That script stays at the repository root, because frozen `evaluate.py` runs it from there.

## `families/`: benchmark family layers

| script | builds | note |
|---|---|---|
| `v2_family_diagnostics.py` | `docs/family_diagnostics_v2.md` | report only |
| `v2_families.py` + `family_rules_v2.json` | family layer v2 in `archive/family_layers/` | superseded |
| `v3_families.py` + `family_rules_v3.json` | family layer v3 in `archive/family_layers/` | superseded |
| `make_labeling_pack_v3.py` | blind labelling pack v3 in `archive/labeling/` | |
| `v4_families.py` + `family_rules_v4.json` | family layer v4 in `archive/family_layers/`, pack v4 | superseded |
| `v5_families.py` + `family_rules_v5.json` | `families_v5.json`, `entity_to_family_v5.csv`, `family_notes_v5.json`, delta pack v5 | **writes frozen** (the live family layer) |

## `extraction/`: field extraction from papers

`gecco_pipeline/` holds three modules of the Gemini-based extractor that produced the GECCO and PPSN records. Its other
modules are not in the repository, so it does not run as is. See `extraction/README.md`.
