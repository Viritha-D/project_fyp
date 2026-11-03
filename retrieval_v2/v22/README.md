# Retrieval v2.2 experiment

- `PREREGISTRATION_v22.md`: committed before any run (71e6287).
- `blend.py`: weighted reciprocal-rank blend of the full v2 and stacked v2.1 family rankings.
- `run_v22.py` writes `report_v22.md` (diagnostics A1/A2, lambda curves, selection), `results_v22_*.csv` and
  `v22_selection.json`.
- Selected lambda = 1.0, i.e. the stacked v2.1 ranking unchanged. It is the CLI default:
  `python retrieval_v2/recommend_v21.py "<query>" [--lambda 1.0]`.
- `queries_v2` was used to select lambda, so it is no longer a test set. A fresh independent query set will be
  scored once with the frozen v2.2 (tag `retrieval-v2.2`).
