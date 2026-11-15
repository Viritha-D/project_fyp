# Archive

Superseded code and data, kept for provenance. No live code reads anything here: not the app, not `selflearn/`, and not
the frozen system in `retrieval_v2/`. Files were moved here with `git mv` on 2026-11-15 (`docs/REPO_PLAN.md`), so
`git log --follow <file>` shows their history.

Archived scripts are not maintained. Their paths were not updated after the move, so they may not run from here.

| folder / file | content |
|---|---|
| `legacy_v1/` | v1 code: demo, parts 3 to 9 of the first pipeline, query tests, TSP investigations, v1 evaluation results |
| `legacy_v1/data/` | v1 data layers: entity map, embedding references, unique papers, unmapped queries, entity strategy layers, dedup candidates |
| `family_layers/` | family layers v2 to v4 (families, entity-to-family maps, notes, candidates, review samples), superseded by v5 at the root |
| `labeling/` | blind labelling packs, keys and instructions for the family reviews v3, v4 and v5-delta |
| `ingest_logs/` | logs of the v1 ingest runs |
| `data_review/` | PPSN and PReMI 2023 paper-identity reviews |
| `implementation_slide_revised.tex` | an earlier slide draft |
| `.ignore` | an old copy of `.gitignore`, kept byte-identical |

Some build scripts in `scripts/` still write their outputs into these folders. `scripts/README.md` lists which.
