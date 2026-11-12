# Post-hoc descriptive analysis: product system v2.3 (blend 0.5)

**Post-hoc. Descriptive only. Decides nothing.** The blend became the product system by the pre-registered decision rule after the test was seen, so the blend's independent-test numbers are selection numbers now. Source: `scored_queries_final.csv` (unchanged).

## Blend 0.5 minus stacked ranker (paired bootstrap, 10,000 resamples, seed 42)

| subset | n | d hit@5 | d MRR |
|---|---|---|---|
| pooled | 60 | +0.067 [-0.033, +0.167] | +0.132 [+0.067, +0.202] |
| t1 only | 20 | +0.100 [+0.000, +0.250] | +0.245 [+0.137, +0.363] |
| t3 only | 20 | -0.050 [-0.250, +0.150] | +0.054 [-0.072, +0.193] |
| t4 only | 20 | +0.150 [+0.000, +0.300] | +0.097 [+0.026, +0.185] |
| without t1 | 40 | +0.050 [-0.075, +0.176] | +0.075 [+0.001, +0.156] |
| without t3 | 40 | +0.125 [+0.025, +0.225] | +0.171 [+0.100, +0.246] |
| without t4 | 40 | +0.025 [-0.100, +0.150] | +0.149 [+0.056, +0.244] |

## Blend 0.5 by group (1,000 resamples)

| group | n | hit@5 | MRR |
|---|---|---|---|
| applied / real-world | 21 | 0.714 [0.524, 0.905] | 0.556 [0.390, 0.738] |
| theory / algorithm analysis | 21 | 0.381 [0.190, 0.571] | 0.293 [0.121, 0.471] |
| unusual / niche | 18 | 0.389 [0.167, 0.611] | 0.294 [0.127, 0.461] |

## Blend 0.5 error causes by set (queries with no gold family in the top 5)

| set | n | misses | (a) no gold among candidates | (b) gold among candidates, below rank 5 | (c) every gold family < 2 papers |
|---|---|---|---|---|---|
| t1 | 20 | 3 | 1 | 2 | 1 |
| t3 | 20 | 15 | 7 | 8 | 6 |
| t4 | 20 | 12 | 6 | 6 | 6 |
| all | 60 | 30 | 14 | 16 | 13 |
