# Retrieval v2 evaluation

- `evaluate.py`: five-fold automatic evaluation. Folds by paper (stratified by Category x Conference,
  seed 42); each fold's index is rebuilt from the training rows with
  `python v2_entities_pipeline.py --hold-out <keys> --out-dir <dir>` (cached in `folds_cache/`, not in git).
  One masked query per held-out paper; gold = the paper's v5 families. Outputs: `folds.csv`,
  `queries_auto.csv`, `results_auto.csv`, `report_auto.md`.
- Human-phrased set: teammates fill `human_queries_template.csv` (quotas in its header) using
  `families_browse.csv` to choose gold families **before** seeing any system output, then run
  `score_human_queries.py <file>` (same metrics; writes `results_human.csv`, `report_human.md`).
- v2.1 (Part C): `PREREGISTRATION.md` (committed before the run), `evaluate_v21.py` (hygiene, paper-kNN,
  stacked ranker, seeds 42 and 43) -> `report_v21.md`, `results_v21_seed*.csv`, `candidates_v21_seed*.csv`,
  `folds_seed43.csv`; deployment model `retrieval_v2/v21_model.json`, CLI `retrieval_v2/recommend_v21.py`.
