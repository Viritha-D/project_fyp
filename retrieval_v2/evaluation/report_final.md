# Final independent test

Scoring run started 2026-11-12 15:21:09 IST (cut-off 12 November 2026, 10:00 IST, amendment 6). Single scoring run on t1, t3, t4. Frozen system tag retrieval-v2.2; environment FROZEN_ENV.txt; batched path; ties by family id ascending.

## Pooled set

Pooled valid queries: **n = 60**. Duplicates dropped (>= 0.95 or identical): 0; flagged (0.8-0.95): 0; maximum cross-set cosine 0.688.

| set | queries | writer | provenance (amendments 3, 5) |
|---|---|---|---|
| t1 | 20 | Sanjesh Nandha | provenance not stated |
| t3 | 20 | Adarsh Prakash | provenance not stated |
| t4 | 20 | Sanjesh Nandha K | statement relayed by the user (formatting-only AI use; does not exclude) |

| group | queries |
|---|---|
| theory / algorithm analysis | 21 |
| applied / real-world | 21 |
| unusual / niche | 18 |

## Results (pooled)

Means over queries, 95% bootstrap intervals (1,000 resamples, seed 42).

| system | role | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| stacked | PRIMARY | 60 | 0.117 [0.050, 0.200] | 0.350 [0.233, 0.467] | 0.433 [0.317, 0.567] | 0.264 [0.181, 0.361] | 0.253 [0.177, 0.341] |
| popularity | secondary | 60 | 0.000 [0.000, 0.000] | 0.050 [0.000, 0.117] | 0.083 [0.017, 0.167] | 0.058 [0.017, 0.125] | 0.034 [0.011, 0.066] |
| full_v2_lambda0 | secondary | 60 | 0.300 [0.183, 0.417] | 0.483 [0.367, 0.617] | 0.517 [0.400, 0.650] | 0.353 [0.253, 0.461] | 0.397 [0.295, 0.513] |
| blend_0.5 | secondary | 60 | 0.283 [0.183, 0.400] | 0.450 [0.333, 0.583] | 0.500 [0.383, 0.633] | 0.336 [0.242, 0.444] | 0.385 [0.285, 0.500] |
| bm25_only | exploratory | 60 | 0.267 [0.150, 0.383] | 0.317 [0.200, 0.433] | 0.350 [0.233, 0.467] | 0.217 [0.131, 0.311] | 0.310 [0.205, 0.426] |
| dense_only | exploratory | 60 | 0.250 [0.150, 0.367] | 0.367 [0.250, 0.483] | 0.417 [0.300, 0.550] | 0.319 [0.219, 0.436] | 0.327 [0.224, 0.440] |
| paper_knn | exploratory | 60 | 0.083 [0.017, 0.167] | 0.100 [0.033, 0.183] | 0.183 [0.083, 0.283] | 0.100 [0.044, 0.169] | 0.130 [0.061, 0.211] |

## Paired comparisons (stacked minus other; paired bootstrap, 10,000 resamples, seed 42)

| comparison | d hit@5 | d MRR |
|---|---|---|
| stacked - popularity | +0.350 [+0.217, +0.483] | +0.219 [+0.140, +0.303] |
| stacked - full_v2_lambda0 | -0.083 [-0.183, +0.017] | -0.144 [-0.223, -0.069] |
| stacked - blend_0.5 | -0.067 [-0.167, +0.033] | -0.132 [-0.202, -0.067] |

## Primary confirmatory claim

Paired difference in hit@5, stacked ranker v2.2 minus popularity, pooled valid queries: **+0.350 [+0.217, +0.483]**, n = 60, interval width 0.267 (paired bootstrap, 10,000 resamples, seed 42). Lower bound above 0: **SUPPORTED**. The cluster bootstrap over 38 groups of queries sharing a gold family (sensitivity (c)) gives +0.350 [+0.176, +0.530], which agrees with this conclusion.

## Blend decision (MRR)

Paired MRR advantage of blend 0.5 over the primary: +0.132 [+0.067, +0.202] (10,000 resamples, seed 42). The interval is entirely above 0: **blend 0.5 replaces the primary**. This choice was made after seeing the test.

## Error causes for every system (queries with no gold family in the top 5)

| system | misses | (a) no gold among candidates | (b) gold among candidates, below rank 5 | (c) every gold family < 2 papers | at least one gold family < 2 papers |
|---|---|---|---|---|---|
| stacked | 34 | 14 | 20 | 18 | 29 |
| popularity | 55 | 0 | 55 | 30 | 46 |
| full_v2_lambda0 | 29 | 26 | 3 | 13 | 22 |
| blend_0.5 | 30 | 14 | 16 | 13 | 23 |
| bm25_only | 39 | 24 | 15 | 18 | 30 |
| dense_only | 35 | 18 | 17 | 14 | 24 |
| paper_knn | 49 | 4 | 45 | 30 | 42 |

For popularity the candidates are all families, so (a) cannot occur.

## By group (hit@5 and MRR, 1,000 resamples)

| group | n | stacked hit@5 | popularity hit@5 | full_v2_lambda0 hit@5 | blend_0.5 hit@5 | stacked MRR |
|---|---|---|---|---|---|---|
| applied / real-world | 21 | 0.619 [0.429, 0.810] | 0.000 [0.000, 0.000] | 0.714 [0.524, 0.905] | 0.714 [0.524, 0.905] | 0.337 [0.212, 0.487] |
| theory / algorithm analysis | 21 | 0.429 [0.238, 0.619] | 0.238 [0.048, 0.429] | 0.381 [0.190, 0.571] | 0.381 [0.190, 0.571] | 0.246 [0.129, 0.374] |
| unusual / niche | 18 | 0.222 [0.056, 0.444] | 0.000 [0.000, 0.000] | 0.444 [0.222, 0.667] | 0.389 [0.167, 0.611] | 0.164 [0.043, 0.336] |

## Stacked confidence tiers (frozen cut-offs 0.0723 / 0.1372)

| tier | n | mean top-1 probability | hit@1 |
|---|---|---|---|
| low | 27 | 0.053 | 0.111 [0.000, 0.259] |
| medium | 17 | 0.094 | 0.059 [0.000, 0.176] |
| high | 16 | 0.225 | 0.188 [0.000, 0.375] |

## Sensitivity analyses (amendment 4; descriptive, not decisive; paired bootstrap, 10,000 resamples)

| analysis | n | vs popularity d hit@5 | d MRR | vs full v2 d hit@5 | d MRR | vs blend 0.5 d hit@5 | d MRR |
|---|---|---|---|---|---|---|---|
| primary (pooled) | 60 | +0.350 [+0.217, +0.483] | +0.219 [+0.140, +0.303] | -0.083 [-0.183, +0.017] | -0.144 [-0.223, -0.069] | -0.067 [-0.167, +0.033] | -0.132 [-0.202, -0.067] |
| (a) t1 only | 20 | +0.700 [+0.450, +0.900] | +0.402 [+0.262, +0.551] | -0.100 [-0.250, +0.000] | -0.228 [-0.374, -0.086] | -0.100 [-0.250, +0.000] | -0.245 [-0.363, -0.137] |
| (a) t3 only | 20 | +0.150 [-0.050, +0.350] | +0.111 [-0.003, +0.240] | +0.050 [-0.150, +0.250] | -0.056 [-0.196, +0.070] | +0.050 [-0.150, +0.250] | -0.054 [-0.193, +0.072] |
| (a) t4 only | 20 | +0.200 [+0.050, +0.400] | +0.144 [+0.041, +0.269] | -0.200 [-0.400, -0.050] | -0.147 [-0.258, -0.050] | -0.150 [-0.300, +0.000] | -0.097 [-0.185, -0.026] |
| (b) without t1 | 40 | +0.175 [+0.050, +0.325] | +0.128 [+0.048, +0.216] | -0.075 [-0.225, +0.075] | -0.101 [-0.189, -0.018] | -0.050 [-0.176, +0.075] | -0.075 [-0.156, -0.001] |
| (b) without t3 | 40 | +0.450 [+0.275, +0.625] | +0.273 [+0.177, +0.377] | -0.150 [-0.275, -0.050] | -0.188 [-0.280, -0.099] | -0.125 [-0.225, -0.025] | -0.171 [-0.246, -0.100] |
| (b) without t4 | 40 | +0.425 [+0.250, +0.600] | +0.257 [+0.156, +0.366] | -0.025 [-0.150, +0.100] | -0.142 [-0.246, -0.041] | -0.025 [-0.150, +0.100] | -0.149 [-0.244, -0.056] |
| (c) cluster bootstrap, 38 components | 60 | +0.350 [+0.176, +0.530] | +0.219 [+0.134, +0.310] | -0.083 [-0.186, +0.031] | -0.144 [-0.221, -0.066] | -0.067 [-0.170, +0.040] | -0.132 [-0.209, -0.056] |
| (d) only sets with a qualifying statement (t4) | 20 | +0.200 [+0.050, +0.400] | +0.144 [+0.041, +0.269] | -0.200 [-0.400, -0.050] | -0.147 [-0.258, -0.050] | -0.150 [-0.300, +0.000] | -0.097 [-0.185, -0.026] |
| leave out writer Sanjesh Nandha (t1, t4) (amendment 5) | 20 | +0.150 [-0.050, +0.350] | +0.111 [-0.003, +0.240] | +0.050 [-0.150, +0.250] | -0.056 [-0.196, +0.070] | +0.050 [-0.150, +0.250] | -0.054 [-0.193, +0.072] |
| leave out writer Adarsh Prakash (t3) (amendment 5) | 40 | +0.450 [+0.275, +0.625] | +0.273 [+0.177, +0.377] | -0.150 [-0.275, -0.050] | -0.188 [-0.280, -0.099] | -0.125 [-0.225, -0.025] | -0.171 [-0.246, -0.100] |

Components for (c): 38; largest sizes [6, 5, 4, 3, 3]; singletons 29.

## Gold families

Distinct gold families in the pooled set: 104; with fewer than 2 papers in the index: 73 (70%). Gold families shared between sets: {'t1&t3': 9, 't1&t4': 5, 't3&t4': 11}.

