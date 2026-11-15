# Repository reorganisation plan (proposal; nothing moved yet)

Date: 2026-11-15. Branch `claude/magical-pascal-uxsxvk`. This is a plan only. **Nothing is moved, renamed or deleted
until it is approved.** Frozen files keep their paths. Everything else either stays, moves with `git mv` (history
kept), or goes to `archive/`. Nothing is deleted.

## 1. Inventory (measured on this branch)

**Size.**

- 277 tracked files; 117 entries at the top level.
- Top-level folders and file counts: `app/` 18, `backup_v1/` 7 (15 MB), `backup_v2/` 14 (14 MB), `data/` 5 (408 KB),
  `docs/` 2, `extraction/` 4, `labeling/` 10 (120 KB), `retrieval_v2/` 87, `selflearn/` 22. The other 108 entries are
  files at the root.
- The full depth-3 listing is in Appendix A.

**Files over 5 MB (tracked).**

| size | file | frozen |
|---|---|---|
| 33.2 MB | paper_embeddings.npy | yes |
| 10.6 MB | papers_master_with_embeddings_ref.csv | no |
| 9.9 MB | papers_master_with_matching_text_v2.csv | yes |
| 9.4 MB | entity_embeddings_v2.npy | yes |
| 7.6 MB | papers_master_v2.csv | no |
| 7.6 MB | master_dataset_clean.csv | no |
| 5.4 MB | entity_notes_v2.json | yes |
| 5.2 MB | family_notes_v4.json | no |

**Git LFS.**

- `git lfs ls-files` on this branch lists **nothing**, and there is no `.gitattributes`. Every file here is plain git.
- On `main`, `.gitattributes` puts `*.pdf`, `*.zip` and `*.csv` under LFS. 12 files are LFS there: 2023-fyp.pdf, "ELA
  Integration Plan Inputs, Reference Library and Mapping.pdf", entity_dedup_candidates.csv, entity_strategy_layer.csv,
  entity_strategy_layer_v2.csv, master_dataset_clean.csv, paper_to_entity_map.csv, paper_to_entity_map_final.csv,
  papers_master_with_embeddings_ref.csv, papers_master_with_matching_text.csv, unique_papers.csv, unmapped_queries.csv.
- The LFS setup is a later step and is not changed by this plan.

**Frozen files.** These are every path in any `FROZEN_HASHES*.txt`, plus the files frozen by rule.

- At the root: entity_embeddings_v2.npy, entity_ids_order_v2.txt, entity_notes_v2.json, entity_to_family_v5.csv,
  families_v5.json, family_notes_v5.json, paper_embeddings.npy, paper_to_entity_map_v2.csv,
  papers_master_with_matching_text_v2.csv, problem_entities_enriched_v2.json.
- In `retrieval_v2/`: config.json, hybrid.py, recommend_v21.py, recommend_v23.py, v21.py, v21_model.json,
  v22/blend.py, v22/v22_selection.json, evaluation/evaluate.py, evaluation/families_browse.csv,
  evaluation/score_human_queries.py.
- By rule: evaluation/scored_queries_final.csv, report_final.md, results_final.json, FROZEN_ENV.txt.

## 2. Why some non-frozen files must also stay

Frozen code reads some non-frozen files at fixed paths, so moving them would break it.

- `retrieval_v2/evaluation/evaluate.py` (frozen) runs `ROOT/v2_entities_pipeline.py` to rebuild the training-only
  indexes.
- That script imports `part4_entities` and `part5_entities` from its own folder, runs `entity_dedup_audit.py` and
  `find_true_duplicates.py`, and reads or writes about 15 files at the root.
- It also reads three files inside the backup folders: `backup_v1/master_before_ingest.csv` (via part4_entities),
  `backup_v2/problem_entities.json` and `backup_v2/paper_to_entity_map_final.csv`.
- `retrieval_v2/config.json` (frozen) names `paper_index.csv` at the root.

These files are marked "(stays)" with the dependency as the reason. Moving them would mean editing frozen code, which is
not allowed.

**Consequence.** About 32 entries stay at the root even after the clean-up (10 frozen data files, 16 pinned files, and
the frozen or pinned folders). A fully tidy root is not possible without changing frozen code.

## 3. Proposed mapping (every top-level entry)

- **frozen = yes:** the path is in a FROZEN_HASHES file (or is `retrieval_v2/`).
- **"(stays)":** the path does not change.
- **`<name>`:** the file keeps its name in the new folder.

| current path | new path | reason | frozen |
|---|---|---|---|
| `app/` | (stays) | already in the target layout (their tests move, see tests/ rows) | no |
| `backup_v1/` | (stays) | part4_entities.py reads backup_v1/master_before_ingest.csv (fidelity gate) | no |
| `backup_v2/` | (stays) | v2_entities_pipeline.py reads backup_v2/problem_entities.json and paper_to_entity_map_final.csv | no |
| `digit_merge_report.csv` | (stays) | read or written by part4_entities.py at ROOT/<name> | no |
| `digit_merge_report_fidelity_old_master.csv` | (stays) | read or written by part4_entities.py at ROOT/<name> | no |
| `docs/` | (stays) | target docs folder | no |
| `entity_dedup_audit.py` | (stays) | run by v2_entities_pipeline.py as ROOT/<name> (subprocess) | no |
| `entity_dedup_candidates_v2.csv` | (stays) | output path fixed in v2_entities_pipeline.py | no |
| `entity_embeddings_v2.npy` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `entity_id_map_old_to_v2.csv` | (stays) | output path fixed in v2_entities_pipeline.py | no |
| `entity_ids_order_v2.txt` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `entity_notes_v2.json` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `entity_to_family_v5.csv` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `entity_true_duplicates_v2.txt` | (stays) | output path fixed in v2_entities_pipeline.py | no |
| `families_v5.json` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `family_notes_v5.json` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `find_true_duplicates.py` | (stays) | run by v2_entities_pipeline.py as ROOT/<name> (subprocess) | no |
| `gold_standard_labels_remapped.csv` | (stays) | read by v2_entities_pipeline.py at ROOT/<name> | no |
| `paper_embeddings.npy` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `paper_ids_order.txt` | (stays) | read by v2_entities_pipeline.py at ROOT/<name> | no |
| `paper_index.csv` | (stays) | named in frozen retrieval_v2/config.json; read by v2_entities_pipeline.py | no |
| `paper_to_entity_map_v2.csv` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `papers_master_with_matching_text_v2.csv` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `part4_answer_key_map.csv` | (stays) | read or written by part4_entities.py at ROOT/<name> | no |
| `part4_entities.py` | (stays) | imported by v2_entities_pipeline.py from its own folder | no |
| `part4_rules.json` | (stays) | read or written by part4_entities.py at ROOT/<name> | no |
| `part5_entities.py` | (stays) | imported by v2_entities_pipeline.py from its own folder | no |
| `problem_entities_enriched_v2.json` | (stays) | frozen (FROZEN_HASHES*.txt); read by the frozen system and the app | yes |
| `problem_entities_v2.json` | (stays) | output path fixed in v2_entities_pipeline.py | no |
| `retrieval_v2/` | (stays) | frozen system and evaluation; every frozen path inside keeps its place | yes |
| `selflearn/` | (stays) | already in the target layout (their tests move, see tests/ rows) | no |
| `v2_entities_pipeline.py` | (stays) | frozen evaluate.py and evaluate_v21.py call ROOT/v2_entities_pipeline.py by a fixed path | no |
| `data/` | (stays) data/incoming/ | raw PReMI input CSVs, 408 KB, small; provenance of the master | no |
| `.gitignore` | (stays, updated) | extend with venvs, caches and local store temp files | no |
| `master_dataset_clean.csv` | DECISION NEEDED: data/ or stay at root | 7.6 MB each; the source master and its byte-identical frozen copy (data_notes.md); not read by code; on main these are LFS | no |
| `papers_master_v2.csv` | DECISION NEEDED: data/ or stay at root | 7.6 MB each; the source master and its byte-identical frozen copy (data_notes.md); not read by code; on main these are LFS | no |
| `.ignore` | archive/.ignore | uncertain: byte-identical duplicate of .gitignore | no |
| `ppsn_review.csv` | archive/data_review/ppsn_review.csv | data-review outputs cited in data_notes.md; provenance only | no |
| `premi2023_proceedings_check.csv` | archive/data_review/premi2023_proceedings_check.csv | data-review outputs cited in data_notes.md; provenance only | no |
| `premi2023_proceedings_toc.csv` | archive/data_review/premi2023_proceedings_toc.csv | data-review outputs cited in data_notes.md; provenance only | no |
| `premi2023_review.csv` | archive/data_review/premi2023_review.csv | data-review outputs cited in data_notes.md; provenance only | no |
| `entity_to_family_v2.csv` | archive/family_layers/entity_to_family_v2.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `entity_to_family_v3.csv` | archive/family_layers/entity_to_family_v3.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `entity_to_family_v4.csv` | archive/family_layers/entity_to_family_v4.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `families_v2.json` | archive/family_layers/families_v2.json | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `families_v3.json` | archive/family_layers/families_v3.json | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `families_v4.json` | archive/family_layers/families_v4.json | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_candidates_v2.csv` | archive/family_layers/family_candidates_v2.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_candidates_v3.csv` | archive/family_layers/family_candidates_v3.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_notes_v2.json` | archive/family_layers/family_notes_v2.json | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_notes_v3.json` | archive/family_layers/family_notes_v3.json | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_notes_v4.json` | archive/family_layers/family_notes_v4.json | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_review_sample.csv` | archive/family_layers/family_review_sample.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `family_review_sample_v3.csv` | archive/family_layers/family_review_sample_v3.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `possible_duplicate_entities_v2.csv` | archive/family_layers/possible_duplicate_entities_v2.csv | superseded family layers v2-v4 and their review samples; v5 is the frozen layer | no |
| `implementation_slide_revised.tex` | archive/implementation_slide_revised.tex | uncertain: presentation source; not referenced anywhere | no |
| `ingest_log.csv` | archive/ingest_logs/ingest_log.csv | logs of the PReMI ingest runs; provenance only | no |
| `ingest_log_v1.csv` | archive/ingest_logs/ingest_log_v1.csv | logs of the PReMI ingest runs; provenance only | no |
| `ingest_skipped.csv` | archive/ingest_logs/ingest_skipped.csv | logs of the PReMI ingest runs; provenance only | no |
| `ingest_skipped_v1.csv` | archive/ingest_logs/ingest_skipped_v1.csv | logs of the PReMI ingest runs; provenance only | no |
| `labeling/` | archive/labeling/ | family-layer labelling packs v3-v5 (blind packs, keys, labels); not read by code | no |
| `demo.py` | archive/legacy_v1/demo.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `fix_underspecified_entities.py` | archive/legacy_v1/fix_underspecified_entities.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `merge_tsp_duplicates.py` | archive/legacy_v1/merge_tsp_duplicates.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part3_embed_papers.py` | archive/legacy_v1/part3_embed_papers.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part4a_dedup_papers.py` | archive/legacy_v1/part4a_dedup_papers.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part5_build_entities.py` | archive/legacy_v1/part5_build_entities.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part6_fix_strategy_layer.py` | archive/legacy_v1/part6_fix_strategy_layer.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part7_apply_enrichment.py` | archive/legacy_v1/part7_apply_enrichment.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part7_diagnose_run.py` | archive/legacy_v1/part7_diagnose_run.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part7_hybrid_retrieval.py` | archive/legacy_v1/part7_hybrid_retrieval.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part7_live_pipeline.py` | archive/legacy_v1/part7_live_pipeline.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part7_live_pipeline_v2.py` | archive/legacy_v1/part7_live_pipeline_v2.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part8_final_output.py` | archive/legacy_v1/part8_final_output.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part9_eval_results.json` | archive/legacy_v1/part9_eval_results.json | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part9_evaluate.py` | archive/legacy_v1/part9_evaluate.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `part9_test_queries.py` | archive/legacy_v1/part9_test_queries.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `qtest.py` | archive/legacy_v1/qtest.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `qtest2.py` | archive/legacy_v1/qtest2.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `query_candidates_test.py` | archive/legacy_v1/query_candidates_test.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `test_queries.json` | archive/legacy_v1/test_queries.json | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `tsp_investigate.py` | archive/legacy_v1/tsp_investigate.py | original v1 pipeline (Parts 3-9) and its CLI demo; superseded by retrieval_v2/ and app/; kept for provenance | no |
| `embedding_metadata.json` | archive/legacy_v1/data/embedding_metadata.json | v1 data products (4,256-row master era); not read by live code | no |
| `entity_dedup_candidates.csv` | archive/legacy_v1/data/entity_dedup_candidates.csv | v1 data products (4,256-row master era); not read by live code | no |
| `entity_strategy_layer.csv` | archive/legacy_v1/data/entity_strategy_layer.csv | v1 data products (4,256-row master era); not read by live code | no |
| `entity_strategy_layer_v2.csv` | archive/legacy_v1/data/entity_strategy_layer_v2.csv | v1 data products (4,256-row master era); not read by live code | no |
| `paper_to_entity_map.csv` | archive/legacy_v1/data/paper_to_entity_map.csv | v1 data products (4,256-row master era); not read by live code | no |
| `paper_to_entity_map_final.csv` | archive/legacy_v1/data/paper_to_entity_map_final.csv | v1 data products (4,256-row master era); not read by live code | no |
| `papers_master_with_embeddings_ref.csv` | archive/legacy_v1/data/papers_master_with_embeddings_ref.csv | v1 data products (4,256-row master era); not read by live code | no |
| `papers_master_with_matching_text.csv` | archive/legacy_v1/data/papers_master_with_matching_text.csv | v1 data products (4,256-row master era); not read by live code | no |
| `problem_entities.json` | archive/legacy_v1/data/problem_entities.json | v1 data products (4,256-row master era); not read by live code | no |
| `unique_papers.csv` | archive/legacy_v1/data/unique_papers.csv | v1 data products (4,256-row master era); not read by live code | no |
| `unmapped_queries.csv` | archive/legacy_v1/data/unmapped_queries.csv | v1 data products (4,256-row master era); not read by live code | no |
| `audit_report.md` | docs/audit_report.md | documentation; not read by code (part4_entities.py only names part4_methodology.md in a docstring) | no |
| `data_notes.md` | docs/data_notes.md | documentation; not read by code (part4_entities.py only names part4_methodology.md in a docstring) | no |
| `family_diagnostics_v2.md` | docs/family_diagnostics_v2.md | documentation; not read by code (part4_entities.py only names part4_methodology.md in a docstring) | no |
| `part4_methodology.md` | docs/part4_methodology.md | documentation; not read by code (part4_entities.py only names part4_methodology.md in a docstring) | no |
| `ingest.py` | scripts/data/ingest.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `part2_matching_text.py` | scripts/data/part2_matching_text.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_apply_paper_decisions.py` | scripts/data/v2_apply_paper_decisions.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_partA_premi2023.py` | scripts/data/v2_partA_premi2023.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_partB_ppsn.py` | scripts/data/v2_partB_ppsn.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_partD_premi2023_proceedings.py` | scripts/data/v2_partD_premi2023_proceedings.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_step1_validate.py` | scripts/data/v2_step1_validate.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_step2_matching_text.py` | scripts/data/v2_step2_matching_text.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `v2_step3_embed_papers.py` | scripts/data/v2_step3_embed_papers.py | data-build scripts (master v2, matching text, embeddings, PReMI/PPSN, paper decisions); need ROOT = parents[2] | no |
| `extraction/` | scripts/extraction/ | Gemini extraction pipeline that produced the PPSN rows; provenance, not read by code | no |
| `family_rules_v2.json` | scripts/families/family_rules_v2.json | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `family_rules_v3.json` | scripts/families/family_rules_v3.json | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `family_rules_v4.json` | scripts/families/family_rules_v4.json | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `family_rules_v5.json` | scripts/families/family_rules_v5.json | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `make_labeling_pack_v3.py` | scripts/families/make_labeling_pack_v3.py | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `v2_families.py` | scripts/families/v2_families.py | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `v2_family_diagnostics.py` | scripts/families/v2_family_diagnostics.py | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `v3_families.py` | scripts/families/v3_families.py | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `v4_families.py` | scripts/families/v4_families.py | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |
| `v5_families.py` | scripts/families/v5_families.py | family-layer builders and their rule files; v5 built families_v5.json; need ROOT edits; never re-run writers of frozen outputs | no |

Additional rows below the top level:

| current path | new path | reason | frozen |
|---|---|---|---|
| `app/tests/` | tests/app/ | target layout has a top-level tests/; needs conftest.py path updates (sys.path to app/) | no |
| `selflearn/tests/` | tests/selflearn/ | same; the tests import the `selflearn` package from the repository root | no |
| everything inside `retrieval_v2/` | (stays) | frozen system; non-frozen files inside (intake scripts, query sets, reports) also stay so that paths in RESULTS.md and the pre-registrations remain valid | partly |

**Notes for the move step.**

- **Moved scripts need path edits.** 17 of the scripts proposed for `scripts/` find the repository through
  `Path(__file__)`, so each needs a one-line ROOT edit (`parents[2]`). Scripts that import each other move together:
  v2_step2 with part2 and ingest; v3/v4/v5 with v2_families.
- **No re-runs.** The move step verifies scripts by importing them, never by running them. `v5_families.py` writes
  `families_v5.json`, which is frozen, so it must not be re-run.
- **Archived scripts won't run where they land.** The v1 pipeline is moved as one folder, so its imports still resolve,
  but its relative data paths will not. That is acceptable for an archive, and its README will say so.
- **Docs need path updates.** `data_notes.md` and the reports cite some moved paths (labeling/, extraction/, review CSVs).
  The move step updates those references in non-frozen docs only.

## 4. Decisions needed from you

1. **LICENSE: which licence?** I have not chosen one. Common options:
   - MIT or Apache-2.0 for the code;
   - CC-BY-4.0 for the derived data;
   - "all rights reserved" (no open licence).
   - **Caution:** `main` holds 2023-fyp.pdf, the PReMI 2023 proceedings (Springer LNCS 14301). It is a third-party
     copyrighted volume, and an open licence for the repository cannot cover it.
2. **CITATION.cff: who are the authors, in which order?** I have not guessed. The commit authors on `main` are
   "Darshan R", "Darshan07", "Sanjesh", "Viritha" and "Viritha Daggubati". I also need the title and the year.
3. **`master_dataset_clean.csv` and `papers_master_v2.csv`: move to `data/` or stay at the root?** They are 7.6 MB each:
   the source master and its byte-identical frozen copy. They are not read by code, and on `main` they are LFS.
4. **`selflearn/store/learned.jsonl`: track it in git or ignore it?** Tracking keeps verified records; ignoring keeps
   local experiments out.

## 5. Files to add

| file | content |
|---|---|
| `README.md` | what the project is, how to run the app (hosted precomputed / local live), the layout, the frozen-files policy, where the results are (retrieval_v2/RESULTS.md) |
| `LICENSE` | **ask first**; see decision 1 |
| `CITATION.cff` | CFF 1.2.0 with the title, authors (decision 2), year, repository URL and a version tag (retrieval-v2.3-blend) |
| `requirements.txt` | pinned runtime environment: the pins of `retrieval_v2/evaluation/FROZEN_ENV.txt` (Python 3.13, torch 2.15.0+cpu from the PyTorch CPU index, sentence-transformers 6.2.0, transformers 5.22.2, numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, scipy 1.18.1, rank-bm25 0.2.2, langdetect 1.0.9, openpyxl 3.1.5, …) plus streamlit==1.67.0 for the app |
| `requirements-dev.txt` | `-r requirements.txt` plus pytest==9.2.0 (with pluggy 1.7.0, iniconfig 2.3.1, as installed in the app test environment) |
| `.gitignore` | add `__pycache__/`, `.pytest_cache/`, `.venv*/`, `venv*/`, `*.pyc`, `selflearn/store/*.tmp`, `retrieval_v2/evaluation/folds_cache/` (already ignored there), and decision 4 |
| `docs/data.md` | every large data file with its size, sha256 (frozen ones from FROZEN_HASHES), origin and the script that built it; the current LFS state (none on this branch; csv/pdf/zip on `main`); what the later LFS step will change |
| `docs/REPO_PLAN.md` | this plan |
| `archive/README.md` | one line per archived group, saying what it was and why it was archived; that nothing in it is read by live code; that archived scripts may not run from there |
| `scripts/README.md` | what each script builds, and the warning never to re-run writers of frozen outputs |

## 6. How the move would be verified (after approval)

The move step will be checked with:

- `git mv` only (history kept) and small commits, one group per commit;
- `sha256sum -c` on every FROZEN_HASHES*.txt before and after each commit;
- all tests (app and selflearn, at their new paths) plus `check_demo_inputs.py`;
- acceptance (a) from the selflearn step (blend 0.5 top 5 on the 60 test queries equal to `scored_queries_final.csv`;
  queries_v2 hit@5 .600, MRR .468);
- the seed-42 automatic run reproduced (stacked hit@5 .376, popularity .328), which exercises `v2_entities_pipeline.py`
  and its pinned files;
- `python -c "import ..."` for every moved script;
- a grep that no live code references a moved path.

## Appendix A: tracked files to depth 3

Paths deeper than three levels are counted per folder.

```
.gitignore
.ignore
app/.gitignore
app/README.md
app/core.py
app/demo_inputs.json
app/gallery.json
app/live.py
app/requirements-live.txt
app/requirements.txt
app/run_demo.sh
app/site_data.json
app/streamlit_app.py
app/tests/conftest.py
app/tests/test_app_render.py
app/tests/test_core.py
app/tests/test_gallery_e2e.py
app/tools/build_gallery.py
app/tools/check_demo_inputs.py
app/tools/site_stats.py
audit_report.md
backup_v1/embedding_metadata.json
backup_v1/entity_strategy_layer_v2.csv
backup_v1/master_after_ingest_v1.csv
backup_v1/master_before_ingest.csv
backup_v1/paper_to_entity_map_final.csv
backup_v1/papers_master_with_matching_text.csv
backup_v1/problem_entities.json
backup_v2/embedding_metadata.json
backup_v2/entity_dedup_candidates.csv
backup_v2/entity_strategy_layer.csv
backup_v2/entity_strategy_layer_v2.csv
backup_v2/ingest_log.csv
backup_v2/ingest_skipped.csv
backup_v2/paper_to_entity_map.csv
backup_v2/paper_to_entity_map_final.csv
backup_v2/papers_master_with_embeddings_ref.csv
backup_v2/papers_master_with_matching_text.csv
backup_v2/part9_eval_results.json
backup_v2/problem_entities.json
backup_v2/unique_papers.csv
backup_v2/unmapped_queries.csv
data/incoming/PReMI_darshan/ (5 files deeper)
data_notes.md
demo.py
digit_merge_report.csv
digit_merge_report_fidelity_old_master.csv
docs/audit_demo.md
docs/limitations.md
embedding_metadata.json
entity_dedup_audit.py
entity_dedup_candidates.csv
entity_dedup_candidates_v2.csv
entity_embeddings_v2.npy
entity_id_map_old_to_v2.csv
entity_ids_order_v2.txt
entity_notes_v2.json
entity_strategy_layer.csv
entity_strategy_layer_v2.csv
entity_to_family_v2.csv
entity_to_family_v3.csv
entity_to_family_v4.csv
entity_to_family_v5.csv
entity_true_duplicates_v2.txt
extraction/README.md
extraction/gecco_pipeline/config.py
extraction/gecco_pipeline/extractor.py
extraction/gecco_pipeline/processor.py
families_v2.json
families_v3.json
families_v4.json
families_v5.json
family_candidates_v2.csv
family_candidates_v3.csv
family_diagnostics_v2.md
family_notes_v2.json
family_notes_v3.json
family_notes_v4.json
family_notes_v5.json
family_review_sample.csv
family_review_sample_v3.csv
family_rules_v2.json
family_rules_v3.json
family_rules_v4.json
family_rules_v5.json
find_true_duplicates.py
fix_underspecified_entities.py
gold_standard_labels_remapped.csv
implementation_slide_revised.tex
ingest.py
ingest_log.csv
ingest_log_v1.csv
ingest_skipped.csv
ingest_skipped_v1.csv
labeling/family_review_key_v3.csv
labeling/family_review_key_v4.csv
labeling/family_review_key_v5_delta.csv
labeling/family_review_labels_v3.csv
labeling/family_review_sample_v3_blind.csv
labeling/family_review_sample_v4_blind.csv
labeling/family_review_sample_v5_delta_blind.csv
labeling/labeling_instructions.md
labeling/labeling_instructions_v4.md
labeling/labeling_instructions_v5_delta.md
make_labeling_pack_v3.py
master_dataset_clean.csv
merge_tsp_duplicates.py
paper_embeddings.npy
paper_ids_order.txt
paper_index.csv
paper_to_entity_map.csv
paper_to_entity_map_final.csv
paper_to_entity_map_v2.csv
papers_master_v2.csv
papers_master_with_embeddings_ref.csv
papers_master_with_matching_text.csv
papers_master_with_matching_text_v2.csv
part2_matching_text.py
part3_embed_papers.py
part4_answer_key_map.csv
part4_entities.py
part4_methodology.md
part4_rules.json
part4a_dedup_papers.py
part5_build_entities.py
part5_entities.py
part6_fix_strategy_layer.py
part7_apply_enrichment.py
part7_diagnose_run.py
part7_hybrid_retrieval.py
part7_live_pipeline.py
part7_live_pipeline_v2.py
part8_final_output.py
part9_eval_results.json
part9_evaluate.py
part9_test_queries.py
possible_duplicate_entities_v2.csv
ppsn_review.csv
premi2023_proceedings_check.csv
premi2023_proceedings_toc.csv
premi2023_review.csv
problem_entities.json
problem_entities_enriched_v2.json
problem_entities_v2.json
qtest.py
qtest2.py
query_candidates_test.py
retrieval_v2/README.md
retrieval_v2/RESULTS.md
retrieval_v2/config.json
retrieval_v2/demo_outputs.md
retrieval_v2/evaluation/.gitignore
retrieval_v2/evaluation/AUDIT_pre_final.md
retrieval_v2/evaluation/FROZEN_ENV.txt
retrieval_v2/evaluation/FROZEN_HASHES.txt
retrieval_v2/evaluation/FROZEN_HASHES_v23.txt
retrieval_v2/evaluation/PREREGISTRATION.md
retrieval_v2/evaluation/PREREGISTRATION_final.md
retrieval_v2/evaluation/PREREGISTRATION_final_amendment1.md
retrieval_v2/evaluation/PREREGISTRATION_final_amendment2.md
retrieval_v2/evaluation/PREREGISTRATION_final_amendment3.md
retrieval_v2/evaluation/PREREGISTRATION_final_amendment4.md
retrieval_v2/evaluation/PREREGISTRATION_final_amendment5.md
retrieval_v2/evaluation/PREREGISTRATION_final_amendment6.md
retrieval_v2/evaluation/PREREGISTRATION_queries.md
retrieval_v2/evaluation/PROVENANCE.md
retrieval_v2/evaluation/PROVENANCE_t.md
retrieval_v2/evaluation/README.md
retrieval_v2/evaluation/build_results_md.py
retrieval_v2/evaluation/candidates_v21_seed42.csv
retrieval_v2/evaluation/candidates_v21_seed43.csv
retrieval_v2/evaluation/convert_t4_docx.py
retrieval_v2/evaluation/evaluate.py
retrieval_v2/evaluation/evaluate_v21.py
retrieval_v2/evaluation/families_browse.csv
retrieval_v2/evaluation/families_for_writers.csv
retrieval_v2/evaluation/families_for_writers.xlsx
retrieval_v2/evaluation/folds.csv
retrieval_v2/evaluation/folds_seed43.csv
retrieval_v2/evaluation/human_queries_template.csv
retrieval_v2/evaluation/intake_validate_t.py
retrieval_v2/evaluation/intake_validate_t34.py
retrieval_v2/evaluation/posthoc_v23.py
retrieval_v2/evaluation/queries_auto.csv
retrieval_v2/evaluation/queries_t1.csv
retrieval_v2/evaluation/queries_t1.xlsx
retrieval_v2/evaluation/queries_t2.csv
retrieval_v2/evaluation/queries_t2.xlsx
retrieval_v2/evaluation/queries_t3.csv
retrieval_v2/evaluation/queries_t3.xlsx
retrieval_v2/evaluation/queries_t3_resolved.csv
retrieval_v2/evaluation/queries_t4.csv
retrieval_v2/evaluation/queries_t4.xlsx
retrieval_v2/evaluation/queries_t4_original.docx
retrieval_v2/evaluation/queries_v2.csv
retrieval_v2/evaluation/queries_v2.xlsx
retrieval_v2/evaluation/report_auto.md
retrieval_v2/evaluation/report_final.md
retrieval_v2/evaluation/report_posthoc_v23.md
retrieval_v2/evaluation/report_queries_v2.md
retrieval_v2/evaluation/report_query_sets.md
retrieval_v2/evaluation/report_query_sets.py
retrieval_v2/evaluation/report_v21.md
retrieval_v2/evaluation/resolve_gold_names.py
retrieval_v2/evaluation/results_auto.csv
retrieval_v2/evaluation/results_final.json
retrieval_v2/evaluation/results_queries_v2.csv
retrieval_v2/evaluation/results_v21_seed42.csv
retrieval_v2/evaluation/results_v21_seed43.csv
retrieval_v2/evaluation/score_final.py
retrieval_v2/evaluation/score_human_queries.py
retrieval_v2/evaluation/scored_queries_final.csv
retrieval_v2/evaluation/similarity_t.csv
retrieval_v2/evaluation/similarity_t34.csv
retrieval_v2/evaluation/submission_template.xlsx
retrieval_v2/evaluation/validation_t.md
retrieval_v2/evaluation/validation_t34.md
retrieval_v2/evaluation/validation_t34_rows.csv
retrieval_v2/evaluation/validation_t_rows.csv
retrieval_v2/hybrid.py
retrieval_v2/recommend.py
retrieval_v2/recommend_v21.py
retrieval_v2/recommend_v23.py
retrieval_v2/v21.py
retrieval_v2/v21_model.json
retrieval_v2/v22/PREREGISTRATION_v22.md
retrieval_v2/v22/README.md
retrieval_v2/v22/blend.py
retrieval_v2/v22/report_v22.md
retrieval_v2/v22/results_v22_queries_v2.csv
retrieval_v2/v22/results_v22_seed42.csv
retrieval_v2/v22/results_v22_seed43.csv
retrieval_v2/v22/run_v22.py
retrieval_v2/v22/v22_selection.json
selflearn/.gitignore
selflearn/__init__.py
selflearn/extract.py
selflearn/fallback.py
selflearn/holdout_check.csv
selflearn/matcher.py
selflearn/profiles.py
selflearn/review_pack.csv
selflearn/review_pack_key.csv
selflearn/schema.py
selflearn/store.py
selflearn/store/README.md
selflearn/tests/__init__.py
selflearn/tests/test_extract.py
selflearn/tests/test_matcher.py
selflearn/tests/test_store.py
selflearn/threshold.json
selflearn/tools/__init__.py
selflearn/tools/choose_threshold.py
selflearn/tools/holdout_check.py
selflearn/trigger.py
selflearn/verify.py
test_queries.json
tsp_investigate.py
unique_papers.csv
unmapped_queries.csv
v2_apply_paper_decisions.py
v2_entities_pipeline.py
v2_families.py
v2_family_diagnostics.py
v2_partA_premi2023.py
v2_partB_ppsn.py
v2_partD_premi2023_proceedings.py
v2_step1_validate.py
v2_step2_matching_text.py
v2_step3_embed_papers.py
v3_families.py
v4_families.py
v5_families.py
```
