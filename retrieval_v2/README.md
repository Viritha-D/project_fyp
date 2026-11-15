# Retrieval v2: benchmark families for a problem description

`python retrieval_v2/recommend.py "<query>" [--k 5]` returns benchmark **families** (v5 by default) with
their notes. No algorithm or strategy recommendation is produced.

Pipeline (`hybrid.py`, settings and file names in `config.json`): BM25 top 20 + dense top 20
(all-mpnet-base-v2) -> reciprocal rank fusion (k = 60) -> shortlist of 10 entities -> cross-encoder
(ms-marco-MiniLM-L-6-v2) -> roll-up to families: family score = best member cross-encoder score +
0.5 * log1p(family n_papers). Margin gate on the top-2 family scores (threshold 1.0, not tuned); a query
that fails it is returned as "not mapped" and appended to `unmapped_queries_v2.csv`.

Each family result keeps **match confidence** (member cross-encoder scores, the top-2 margin) separate
from **evidence strength** (papers, venues, reuse signals, member caveats).

To switch to another family layer, edit only the `families` block of `config.json`.
Evaluation lives in `evaluation/` (see its README).
