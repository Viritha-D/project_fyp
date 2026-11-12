# Retrieval v2.1 / v2.2: results

**v2.2 ranks identically to v2.1.** The v2.2 blend experiment selected lambda = 1.0, which is the stacked v2.1 ranking unchanged (checked: identical top-5 on all 55 / 558 / 548 queries, and identical CLI output on the 7 demo queries). The product system is therefore called the **stacked ranker (v2.1/v2.2)** below; tables label it `stacked ranker (v2.1/v2.2)`. Tags: `retrieval-v2.1-frozen`, `retrieval-v2.2`.

Benchmark-family recommendation from a problem description. Models frozen at tag `retrieval-v2.1-frozen`. Details: `evaluation/report_auto.md` (v2), `evaluation/report_v21.md` (v2.1), `evaluation/report_query_sets.md` (written queries); pre-registrations `evaluation/PREREGISTRATION.md`, `evaluation/PREREGISTRATION_queries.md`, `v22/PREREGISTRATION_v22.md`; blend experiment `v22/report_v22.md`.

## Setup

- 1,488 papers (11,342 benchmark records), 3,199 problem entities, 2,173 v5 benchmark families.
- Five folds **by paper**, stratified by Category x Conference; two seeds (42 primary, 43 replication).
- Each fold's index (entity descriptions, entity embeddings, BM25, family paper counts, kNN paper pool) is **rebuilt from the training papers only**.
- One automatic query per held-out paper from its own fields, with every **benchmark name token masked**; gold = the paper's families that exist in the training index ("seen"). Papers without seen gold are "unseen" and not scored.
- Systems: popularity; BM25 only; dense only (all-mpnet-base-v2); full v2 (BM25 + dense, RRF, cross-encoder, family roll-up with evidence bonus); paper-kNN voting; stacked ranker (v2.1/v2.2) (logistic regression over 8 features of the candidates from full v2 and paper-kNN, cross-fitted).
- 95% bootstrap intervals over papers (1,000 resamples).

## Overall, seed 42 (n = 558 scored papers)

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| all | popularity | 558 | 0.066 [0.045, 0.088] | 0.201 [0.165, 0.235] | 0.328 [0.290, 0.371] | 0.227 [0.195, 0.259] | 0.164 [0.140, 0.188] |
| all | bm25_only | 558 | 0.041 [0.025, 0.057] | 0.073 [0.054, 0.095] | 0.113 [0.088, 0.140] | 0.096 [0.074, 0.120] | 0.076 [0.060, 0.094] |
| all | dense_only | 558 | 0.023 [0.013, 0.036] | 0.057 [0.039, 0.077] | 0.099 [0.073, 0.124] | 0.080 [0.059, 0.102] | 0.058 [0.044, 0.073] |
| all | full_v2 | 558 | 0.072 [0.050, 0.093] | 0.156 [0.127, 0.186] | 0.186 [0.156, 0.219] | 0.157 [0.130, 0.187] | 0.116 [0.095, 0.139] |
| all | paper_knn | 558 | 0.066 [0.047, 0.090] | 0.151 [0.122, 0.183] | 0.242 [0.208, 0.281] | 0.194 [0.165, 0.226] | 0.142 [0.122, 0.168] |
| all | stacked ranker (v2.1/v2.2) | 558 | 0.172 [0.143, 0.203] | 0.296 [0.254, 0.333] | 0.376 [0.337, 0.421] | 0.300 [0.265, 0.337] | 0.255 [0.225, 0.285] |

## Overall, seed 43 (n = 548 scored papers)

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| all | popularity | 548 | 0.075 [0.053, 0.099] | 0.210 [0.175, 0.245] | 0.310 [0.268, 0.349] | 0.214 [0.184, 0.247] | 0.171 [0.147, 0.195] |
| all | bm25_only | 548 | 0.042 [0.026, 0.058] | 0.078 [0.058, 0.100] | 0.120 [0.095, 0.146] | 0.099 [0.076, 0.122] | 0.077 [0.061, 0.095] |
| all | dense_only | 548 | 0.024 [0.011, 0.036] | 0.066 [0.046, 0.088] | 0.108 [0.084, 0.133] | 0.080 [0.060, 0.101] | 0.063 [0.048, 0.079] |
| all | full_v2 | 548 | 0.071 [0.049, 0.091] | 0.161 [0.131, 0.192] | 0.208 [0.175, 0.241] | 0.168 [0.141, 0.197] | 0.122 [0.101, 0.145] |
| all | paper_knn | 548 | 0.080 [0.058, 0.104] | 0.161 [0.131, 0.193] | 0.235 [0.199, 0.270] | 0.193 [0.160, 0.223] | 0.150 [0.125, 0.174] |
| all | stacked ranker (v2.1/v2.2) | 548 | 0.166 [0.133, 0.195] | 0.276 [0.239, 0.314] | 0.352 [0.314, 0.392] | 0.288 [0.253, 0.323] | 0.244 [0.212, 0.274] |

## By Category (seed 42)

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| Applied | popularity | 158 | 0.000 [0.000, 0.000] | 0.006 [0.000, 0.019] | 0.013 [0.000, 0.032] | 0.004 [0.000, 0.011] | 0.006 [0.001, 0.014] |
| Applied | bm25_only | 158 | 0.044 [0.013, 0.076] | 0.076 [0.038, 0.120] | 0.120 [0.076, 0.171] | 0.107 [0.062, 0.158] | 0.078 [0.045, 0.113] |
| Applied | dense_only | 158 | 0.044 [0.013, 0.082] | 0.076 [0.038, 0.114] | 0.082 [0.044, 0.127] | 0.067 [0.032, 0.105] | 0.065 [0.034, 0.102] |
| Applied | full_v2 | 158 | 0.101 [0.057, 0.152] | 0.139 [0.088, 0.196] | 0.152 [0.095, 0.209] | 0.134 [0.083, 0.188] | 0.122 [0.076, 0.170] |
| Applied | paper_knn | 158 | 0.006 [0.000, 0.019] | 0.013 [0.000, 0.032] | 0.019 [0.000, 0.038] | 0.012 [0.000, 0.027] | 0.026 [0.014, 0.043] |
| Applied | stacked ranker (v2.1/v2.2) | 158 | 0.089 [0.044, 0.133] | 0.108 [0.057, 0.158] | 0.127 [0.076, 0.177] | 0.113 [0.069, 0.162] | 0.107 [0.063, 0.151] |
| Pure Math | popularity | 400 | 0.092 [0.067, 0.125] | 0.278 [0.235, 0.320] | 0.453 [0.405, 0.502] | 0.315 [0.276, 0.355] | 0.226 [0.198, 0.256] |
| Pure Math | bm25_only | 400 | 0.040 [0.022, 0.058] | 0.072 [0.050, 0.100] | 0.110 [0.080, 0.140] | 0.092 [0.066, 0.118] | 0.075 [0.056, 0.095] |
| Pure Math | dense_only | 400 | 0.015 [0.005, 0.028] | 0.050 [0.030, 0.072] | 0.105 [0.077, 0.135] | 0.085 [0.060, 0.112] | 0.055 [0.041, 0.069] |
| Pure Math | full_v2 | 400 | 0.060 [0.037, 0.083] | 0.163 [0.128, 0.198] | 0.200 [0.160, 0.240] | 0.166 [0.132, 0.200] | 0.114 [0.089, 0.141] |
| Pure Math | paper_knn | 400 | 0.090 [0.062, 0.120] | 0.205 [0.168, 0.245] | 0.330 [0.285, 0.375] | 0.266 [0.227, 0.305] | 0.188 [0.160, 0.218] |
| Pure Math | stacked ranker (v2.1/v2.2) | 400 | 0.205 [0.168, 0.245] | 0.370 [0.323, 0.415] | 0.475 [0.425, 0.522] | 0.374 [0.330, 0.415] | 0.313 [0.277, 0.349] |

## By Category (seed 43)

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| Applied | popularity | 157 | 0.000 [0.000, 0.000] | 0.006 [0.000, 0.019] | 0.013 [0.000, 0.032] | 0.006 [0.000, 0.016] | 0.006 [0.001, 0.014] |
| Applied | bm25_only | 157 | 0.038 [0.013, 0.070] | 0.070 [0.032, 0.115] | 0.102 [0.057, 0.153] | 0.088 [0.046, 0.136] | 0.071 [0.039, 0.107] |
| Applied | dense_only | 157 | 0.045 [0.013, 0.076] | 0.051 [0.019, 0.089] | 0.070 [0.032, 0.108] | 0.055 [0.023, 0.092] | 0.055 [0.024, 0.089] |
| Applied | full_v2 | 157 | 0.083 [0.045, 0.134] | 0.115 [0.064, 0.166] | 0.127 [0.076, 0.185] | 0.108 [0.063, 0.158] | 0.101 [0.057, 0.149] |
| Applied | paper_knn | 157 | 0.006 [0.000, 0.019] | 0.025 [0.006, 0.051] | 0.032 [0.006, 0.064] | 0.025 [0.003, 0.051] | 0.028 [0.013, 0.044] |
| Applied | stacked ranker (v2.1/v2.2) | 157 | 0.070 [0.032, 0.115] | 0.089 [0.045, 0.140] | 0.108 [0.057, 0.159] | 0.094 [0.051, 0.141] | 0.086 [0.046, 0.130] |
| Pure Math | popularity | 391 | 0.105 [0.077, 0.136] | 0.292 [0.246, 0.340] | 0.430 [0.379, 0.481] | 0.297 [0.258, 0.338] | 0.237 [0.208, 0.268] |
| Pure Math | bm25_only | 391 | 0.043 [0.026, 0.064] | 0.082 [0.054, 0.113] | 0.128 [0.095, 0.164] | 0.104 [0.074, 0.133] | 0.080 [0.059, 0.102] |
| Pure Math | dense_only | 391 | 0.015 [0.005, 0.028] | 0.072 [0.049, 0.097] | 0.123 [0.092, 0.156] | 0.090 [0.065, 0.116] | 0.067 [0.051, 0.084] |
| Pure Math | full_v2 | 391 | 0.066 [0.043, 0.092] | 0.179 [0.141, 0.217] | 0.240 [0.199, 0.284] | 0.192 [0.155, 0.231] | 0.131 [0.105, 0.159] |
| Pure Math | paper_knn | 391 | 0.110 [0.079, 0.141] | 0.215 [0.171, 0.256] | 0.317 [0.271, 0.366] | 0.260 [0.218, 0.301] | 0.199 [0.168, 0.231] |
| Pure Math | stacked ranker (v2.1/v2.2) | 391 | 0.205 [0.166, 0.246] | 0.350 [0.304, 0.399] | 0.450 [0.402, 0.499] | 0.366 [0.320, 0.409] | 0.307 [0.268, 0.348] |

## Pre-registered criterion

d = hit@5(stacked) - hit@5(reference), paired bootstrap 95% interval. (a) overall upper >= 0; (b) Pure Math upper >= 0; (c) Applied lower > 0; required on both seeds.

| seed | reference | overall d | Pure Math d | Applied d | (a) | (b) | (c) |
|---|---|---|---|---|---|---|---|
| 42 | popularity | 0.048 [0.016, 0.082] | 0.022 [-0.020, 0.065] | 0.114 [0.070, 0.165] | True | True | True |
| 42 | popularity_clean | 0.048 [0.016, 0.082] | 0.022 [-0.020, 0.065] | 0.114 [0.070, 0.165] | True | True | True |
| 43 | popularity | 0.042 [0.011, 0.078] | 0.020 [-0.026, 0.069] | 0.096 [0.045, 0.146] | True | True | True |
| 43 | popularity_clean | 0.042 [0.011, 0.078] | 0.020 [-0.026, 0.069] | 0.096 [0.045, 0.146] | True | True | True |

**Criterion (against the Part B popularity baseline, both seeds): MET.**

## Reliability of the confidence tiers (stacked)

**Seed 42**

Cut-offs per fold: fold 0: 0.078 / 0.149; fold 1: 0.071 / 0.134; fold 2: 0.070 / 0.132; fold 3: 0.071 / 0.129; fold 4: 0.072 / 0.138

| tier | n | mean predicted p(top-1 gold) | hit@1 |
|---|---|---|---|
| low | 187 | 0.049 | 0.096 [0.059, 0.139] |
| medium | 179 | 0.101 | 0.179 [0.123, 0.235] |
| high | 192 | 0.211 | 0.240 [0.182, 0.302] |

Spearman(top-1 probability, hit@1) = 0.187; Brier score = 0.140

**Seed 43**

Cut-offs per fold: fold 0: 0.069 / 0.141; fold 1: 0.070 / 0.135; fold 2: 0.072 / 0.145; fold 3: 0.073 / 0.148; fold 4: 0.073 / 0.148

| tier | n | mean predicted p(top-1 gold) | hit@1 |
|---|---|---|---|
| low | 185 | 0.051 | 0.076 [0.043, 0.119] |
| medium | 183 | 0.105 | 0.175 [0.126, 0.230] |
| high | 180 | 0.218 | 0.250 [0.189, 0.317] |

Spearman(top-1 probability, hit@1) = 0.228; Brier score = 0.133

## Unseen analysis and oracle (seed 42)

Unseen papers: 930 of 1488. Of these, 910 (97.8%) have only gold families with a single paper in the whole data (no split can make them seen).

| Category | papers | unseen | unseen share | oracle hit@5 | popularity hit@5 (all papers) | full_v2 hit@5 (all papers) | paper_knn hit@5 (all papers) | stacked hit@5 (all papers) |
|---|---|---|---|---|---|---|---|---|
| Applied | 872 | 714 | 0.819 | 0.181 | 0.002 | 0.028 | 0.003 | 0.023 |
| Pure Math | 616 | 216 | 0.351 | 0.649 | 0.294 | 0.130 | 0.214 | 0.308 |

| Conference | papers | unseen | unseen share | oracle hit@5 | popularity hit@5 (all papers) | full_v2 hit@5 (all papers) | paper_knn hit@5 (all papers) | stacked hit@5 (all papers) |
|---|---|---|---|---|---|---|---|---|
| CEC | 378 | 226 | 0.598 | 0.402 | 0.124 | 0.090 | 0.180 | 0.167 |
| FOGA | 69 | 22 | 0.319 | 0.681 | 0.391 | 0.159 | 0.087 | 0.377 |
| GECCO | 750 | 437 | 0.583 | 0.417 | 0.132 | 0.057 | 0.069 | 0.137 |
| PPSN | 5 | 0 | 0.000 | 1.000 | 1.000 | 0.200 | 0.600 | 0.800 |
| PReMI | 286 | 245 | 0.857 | 0.143 | 0.017 | 0.052 | 0.021 | 0.049 |

| entities | papers | unseen | unseen share | oracle hit@5 | popularity hit@5 (all papers) | full_v2 hit@5 (all papers) | paper_knn hit@5 (all papers) | stacked hit@5 (all papers) |
|---|---|---|---|---|---|---|---|---|
| 1 | 817 | 603 | 0.738 | 0.262 | 0.064 | 0.055 | 0.072 | 0.098 |
| 2 | 236 | 147 | 0.623 | 0.377 | 0.165 | 0.102 | 0.114 | 0.191 |
| 3-5 | 280 | 131 | 0.468 | 0.532 | 0.196 | 0.082 | 0.093 | 0.179 |
| >=6 | 155 | 49 | 0.316 | 0.684 | 0.239 | 0.077 | 0.148 | 0.226 |

All papers: oracle hit@5 = 0.375; hit@5 over all papers (unseen = miss): popularity 0.123, full_v2 0.070, paper_knn 0.091, stacked 0.141

## Stacked ranker weights (deployment model, standardised features)

| feature | coefficient |
|---|---|
| ce_best | +0.348 |
| bm25_best_rel | +0.618 |
| dense_best | +0.347 |
| knn_vote | -0.106 |
| log_n_papers | +1.060 |
| kind_suite_or_series | +0.127 |
| kind_stem_group | +0.109 |
| kind_template_grid | +0.018 |
| intercept | -4.273 |

paper-kNN K = 100; tier cut-offs 0.0723 / 0.1372.

## Written query set (queries_v2, 55 queries, published index)

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| all | popularity | 55 | 0.036 [0.000, 0.091] | 0.164 [0.073, 0.273] | 0.200 [0.091, 0.309] | 0.103 [0.045, 0.164] | 0.102 [0.048, 0.172] |
| all | bm25_only | 55 | 0.236 [0.127, 0.345] | 0.400 [0.272, 0.527] | 0.455 [0.327, 0.582] | 0.230 [0.158, 0.309] | 0.316 [0.207, 0.422] |
| all | dense_only | 55 | 0.218 [0.109, 0.345] | 0.455 [0.309, 0.582] | 0.527 [0.400, 0.655] | 0.367 [0.258, 0.473] | 0.354 [0.252, 0.460] |
| all | full_v2 | 55 | 0.327 [0.200, 0.455] | 0.509 [0.382, 0.636] | 0.564 [0.436, 0.691] | 0.364 [0.264, 0.464] | 0.423 [0.311, 0.536] |
| all | paper_knn | 55 | 0.091 [0.018, 0.182] | 0.309 [0.200, 0.436] | 0.400 [0.273, 0.527] | 0.242 [0.161, 0.336] | 0.230 [0.161, 0.316] |
| all | stacked ranker (v2.1/v2.2) | 55 | 0.200 [0.091, 0.309] | 0.400 [0.273, 0.527] | 0.491 [0.363, 0.618] | 0.294 [0.206, 0.394] | 0.336 [0.239, 0.433] |

### Primary comparisons (paired bootstrap, stacked minus reference)

| comparison | d hit@5 | d MRR |
|---|---|---|
| stacked ranker (v2.1/v2.2) - popularity | 0.291 [0.127, 0.436] | 0.234 [0.131, 0.341] |
| stacked ranker (v2.1/v2.2) - full_v2 | -0.073 [-0.182, 0.036] | -0.086 [-0.186, 0.002] |

### By group

Group sizes: continuous single-objective 15, multi-objective 10, combinatorial 10, machine learning 10, vague 5, control / RL 5

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| combinatorial | popularity | 10 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| combinatorial | bm25_only | 10 | 0.400 [0.100, 0.700] | 0.700 [0.400, 0.902] | 0.700 [0.400, 0.902] | 0.433 [0.233, 0.617] | 0.517 [0.250, 0.784] |
| combinatorial | dense_only | 10 | 0.400 [0.100, 0.700] | 0.900 [0.700, 1.000] | 0.900 [0.700, 1.000] | 0.750 [0.550, 0.917] | 0.646 [0.442, 0.850] |
| combinatorial | full_v2 | 10 | 0.800 [0.500, 1.000] | 0.900 [0.700, 1.000] | 0.900 [0.700, 1.000] | 0.783 [0.550, 1.000] | 0.850 [0.600, 1.000] |
| combinatorial | paper_knn | 10 | 0.100 [0.000, 0.300] | 0.300 [0.000, 0.600] | 0.500 [0.200, 0.800] | 0.383 [0.133, 0.650] | 0.263 [0.087, 0.475] |
| combinatorial | stacked ranker (v2.1/v2.2) | 10 | 0.300 [0.100, 0.600] | 0.600 [0.300, 0.900] | 0.700 [0.400, 0.900] | 0.467 [0.250, 0.683] | 0.481 [0.262, 0.706] |
| continuous single-objective | popularity | 15 | 0.000 [0.000, 0.000] | 0.400 [0.200, 0.667] | 0.467 [0.267, 0.733] | 0.233 [0.111, 0.367] | 0.194 [0.089, 0.311] |
| continuous single-objective | bm25_only | 15 | 0.133 [0.000, 0.333] | 0.200 [0.000, 0.400] | 0.200 [0.000, 0.400] | 0.067 [0.000, 0.133] | 0.167 [0.000, 0.367] |
| continuous single-objective | dense_only | 15 | 0.067 [0.000, 0.200] | 0.267 [0.067, 0.467] | 0.333 [0.133, 0.600] | 0.178 [0.056, 0.333] | 0.183 [0.050, 0.350] |
| continuous single-objective | full_v2 | 15 | 0.200 [0.000, 0.400] | 0.267 [0.067, 0.533] | 0.333 [0.133, 0.600] | 0.133 [0.056, 0.233] | 0.250 [0.083, 0.467] |
| continuous single-objective | paper_knn | 15 | 0.133 [0.000, 0.333] | 0.267 [0.067, 0.467] | 0.333 [0.133, 0.600] | 0.167 [0.056, 0.322] | 0.243 [0.106, 0.423] |
| continuous single-objective | stacked ranker (v2.1/v2.2) | 15 | 0.200 [0.000, 0.400] | 0.400 [0.200, 0.667] | 0.400 [0.200, 0.667] | 0.222 [0.089, 0.400] | 0.300 [0.122, 0.511] |
| control / RL | popularity | 5 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| control / RL | bm25_only | 5 | 0.400 [0.000, 0.800] | 0.400 [0.000, 0.800] | 0.600 [0.200, 1.000] | 0.233 [0.067, 0.400] | 0.440 [0.040, 0.840] |
| control / RL | dense_only | 5 | 0.200 [0.000, 0.600] | 0.600 [0.200, 1.000] | 0.800 [0.400, 1.000] | 0.400 [0.200, 0.600] | 0.407 [0.140, 0.733] |
| control / RL | full_v2 | 5 | 0.200 [0.000, 0.600] | 0.800 [0.400, 1.000] | 0.800 [0.400, 1.000] | 0.433 [0.200, 0.633] | 0.467 [0.267, 0.733] |
| control / RL | paper_knn | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.200 [0.000, 0.467] | 0.140 [0.000, 0.340] |
| control / RL | stacked ranker (v2.1/v2.2) | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.600 [0.200, 1.000] | 0.233 [0.067, 0.400] | 0.205 [0.065, 0.365] |
| machine learning | popularity | 10 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| machine learning | bm25_only | 10 | 0.300 [0.000, 0.600] | 0.600 [0.300, 0.900] | 0.600 [0.300, 0.900] | 0.317 [0.133, 0.517] | 0.417 [0.167, 0.683] |
| machine learning | dense_only | 10 | 0.400 [0.100, 0.700] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.333 [0.100, 0.600] | 0.450 [0.175, 0.738] |
| machine learning | full_v2 | 10 | 0.200 [0.000, 0.500] | 0.600 [0.300, 0.900] | 0.600 [0.300, 0.900] | 0.350 [0.150, 0.567] | 0.350 [0.133, 0.583] |
| machine learning | paper_knn | 10 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.500] | 0.300 [0.098, 0.600] | 0.200 [0.049, 0.450] | 0.120 [0.033, 0.227] |
| machine learning | stacked ranker (v2.1/v2.2) | 10 | 0.200 [0.000, 0.500] | 0.400 [0.100, 0.700] | 0.400 [0.100, 0.700] | 0.250 [0.050, 0.483] | 0.308 [0.087, 0.562] |
| multi-objective | popularity | 10 | 0.100 [0.000, 0.300] | 0.100 [0.000, 0.300] | 0.100 [0.000, 0.300] | 0.050 [0.000, 0.150] | 0.111 [0.000, 0.311] |
| multi-objective | bm25_only | 10 | 0.200 [0.000, 0.500] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.267 [0.083, 0.467] | 0.299 [0.091, 0.553] |
| multi-objective | dense_only | 10 | 0.200 [0.000, 0.500] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.367 [0.133, 0.667] | 0.325 [0.100, 0.550] |
| multi-objective | full_v2 | 10 | 0.300 [0.000, 0.600] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.317 [0.117, 0.567] | 0.392 [0.150, 0.667] |
| multi-objective | paper_knn | 10 | 0.100 [0.000, 0.300] | 0.400 [0.100, 0.700] | 0.400 [0.100, 0.700] | 0.217 [0.050, 0.400] | 0.242 [0.078, 0.462] |
| multi-objective | stacked ranker (v2.1/v2.2) | 10 | 0.100 [0.000, 0.300] | 0.300 [0.000, 0.600] | 0.400 [0.100, 0.700] | 0.233 [0.050, 0.433] | 0.266 [0.118, 0.452] |
| vague | popularity | 5 | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.600 [0.200, 1.000] | 0.333 [0.100, 0.567] | 0.317 [0.050, 0.667] |
| vague | bm25_only | 5 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.067 [0.000, 0.200] | 0.070 [0.000, 0.170] |
| vague | dense_only | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.100 [0.000, 0.300] |
| vague | full_v2 | 5 | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.267 [0.000, 0.600] | 0.250 [0.000, 0.600] |
| vague | paper_knn | 5 | 0.200 [0.000, 0.600] | 0.600 [0.200, 1.000] | 0.600 [0.200, 1.000] | 0.367 [0.067, 0.700] | 0.412 [0.157, 0.725] |
| vague | stacked ranker (v2.1/v2.2) | 5 | 0.400 [0.000, 0.800] | 0.400 [0.000, 0.800] | 0.600 [0.200, 1.000] | 0.433 [0.100, 0.767] | 0.484 [0.129, 0.840] |

### Confidence tiers on the written queries

| tier | n | mean predicted p(top-1 gold) | hit@1 |
|---|---|---|---|
| low | 23 | 0.048 | 0.130 [0.000, 0.304] |
| medium | 19 | 0.097 | 0.158 [0.000, 0.316] |
| high | 13 | 0.306 | 0.385 [0.154, 0.615] |

Secondary sets `ai_queries_v1.csv` and `queries_reworded_v1.csv`: not run (files not supplied).

## Limitations

- **Stacking, not strict nesting.** The stacked ranker for fold i is trained on the out-of-fold features of the other folds, whose indexes contain fold i's papers as training data.
- **Candidate ceiling.** A gold family is among the stacked ranker's candidates for only 56.6% (seed 42) / 52.2% (seed 43) of scored queries; no re-ranking can recover the rest.
- **Unseen papers.** 930 of 1,488 papers (seed 42) have no gold family in the training index, and 97.8% of these use only single-paper benchmarks, so no split could make them findable (oracle hit@5 over all papers .375).
- **Applied problems.** Stacked hit@5 on Applied papers is .127 (seed 42), slightly below full v2 (.152; paired difference -.025 [-.057, .006]); the gain over popularity comes from Pure Math.
- **Under-confident tiers.** In every tier the measured hit@1 is above the mean predicted probability; the tiers rank queries but their probabilities are not calibrated.
- **Automatic Pure Math queries carry little information.** With benchmark names masked, a Pure Math query is mostly an algorithm name, a dimension and generic landscape words, which favours popular suites.
- **Gold selection.** Gold for all query sets (automatic and written) was chosen with the families browse file (`evaluation/families_browse.csv`), i.e. within the v5 family layer.
- **Written queries.** On the 55 written queries, stacked is below full v2 (hit@5 difference -.073 [-.182, .036], MRR -.086 [-.186, .002]); the stacked ranker often fills the top 5 with large generic suites (BBOB, CEC 2017, DTLZ) for specific queries.
- **queries_v2 is a selection set.** The v2.2 lambda was selected on queries_v2 (MRR), so every number on queries_v2 after the blend experiment is a selection number, not a test number.
- **Provenance.** The provenance statement is in `evaluation/PROVENANCE.md`: "Queries written by: Sanjesh. Gold families chosen by: Darshan . Date and time finished: 3/11/26 11:43.
Tools used (including any AI tool): IEEE(reference. System outputs seen before the file was final: Unknown." It is unknown whether system outputs were seen before the file was final.

## Blend experiment (v2.2)

Final ranking = weighted reciprocal rank fusion of the full v2 family ranking and the stacked family ranking: score = (1 - lambda) / (60 + rank_full) + lambda / (60 + rank_stacked); a family missing from one list gets no contribution from that term; lambda in {0, 0.25, 0.5, 0.75, 1}. Pre-registered in `v22/PREREGISTRATION_v22.md` before any run.

Reproduction checks (top-5 identical to the earlier results files): queries_v2: full_v2 55/55, lambda=1 vs stacked 55/55; seed 42: full_v2 558/558, lambda=1 vs stacked 558/558; seed 43: full_v2 548/548, lambda=1 vs stacked 548/548

| data | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| queries_v2 (55) | popularity (reference) | 55 | 0.036 [0.000, 0.091] | 0.164 [0.073, 0.273] | 0.200 [0.091, 0.309] | 0.103 [0.045, 0.164] | 0.102 [0.048, 0.172] |
| queries_v2 (55) | full_v2 (reference) | 55 | 0.327 [0.200, 0.455] | 0.509 [0.382, 0.636] | 0.564 [0.436, 0.691] | 0.364 [0.264, 0.464] | 0.423 [0.311, 0.536] |
| queries_v2 (55) | stacked v2.1 (reference) | 55 | 0.200 [0.091, 0.309] | 0.400 [0.273, 0.527] | 0.491 [0.363, 0.618] | 0.294 [0.206, 0.394] | 0.336 [0.239, 0.433] |
| queries_v2 (55) | blend lambda=0.0 | 55 | 0.327 [0.200, 0.455] | 0.509 [0.382, 0.636] | 0.564 [0.436, 0.691] | 0.364 [0.264, 0.464] | 0.428 [0.315, 0.542] |
| queries_v2 (55) | blend lambda=0.25 | 55 | 0.309 [0.182, 0.436] | 0.527 [0.400, 0.655] | 0.582 [0.455, 0.709] | 0.382 [0.276, 0.488] | 0.426 [0.319, 0.537] |
| queries_v2 (55) | blend lambda=0.5 | 55 | 0.382 [0.255, 0.509] | 0.527 [0.400, 0.655] | 0.600 [0.473, 0.727] | 0.382 [0.276, 0.485] | 0.468 [0.349, 0.585] |
| queries_v2 (55) | blend lambda=0.75 | 55 | 0.382 [0.255, 0.509] | 0.527 [0.400, 0.655] | 0.582 [0.455, 0.709] | 0.382 [0.276, 0.488] | 0.468 [0.347, 0.585] |
| queries_v2 (55) | blend lambda=1.0 | 55 | 0.200 [0.091, 0.309] | 0.400 [0.273, 0.527] | 0.491 [0.363, 0.618] | 0.294 [0.206, 0.394] | 0.336 [0.239, 0.433] |
| auto seed 42 (558) | popularity (reference) | 558 | 0.066 [0.045, 0.088] | 0.201 [0.165, 0.235] | 0.328 [0.290, 0.371] | 0.227 [0.195, 0.259] | 0.164 [0.140, 0.188] |
| auto seed 42 (558) | stacked v2.1 (reference) | 558 | 0.172 [0.143, 0.203] | 0.296 [0.254, 0.333] | 0.376 [0.337, 0.421] | 0.300 [0.265, 0.337] | 0.255 [0.225, 0.285] |
| auto seed 42 (558) | full_v2 (reference) | 558 | 0.072 [0.050, 0.093] | 0.156 [0.127, 0.186] | 0.186 [0.156, 0.219] | 0.157 [0.130, 0.187] | 0.116 [0.095, 0.139] |
| auto seed 42 (558) | blend lambda=0.0 | 558 | 0.072 [0.050, 0.093] | 0.156 [0.127, 0.186] | 0.186 [0.156, 0.219] | 0.157 [0.130, 0.187] | 0.118 [0.096, 0.141] |
| auto seed 42 (558) | blend lambda=0.25 | 558 | 0.108 [0.082, 0.134] | 0.181 [0.150, 0.213] | 0.192 [0.159, 0.226] | 0.161 [0.134, 0.191] | 0.147 [0.121, 0.174] |
| auto seed 42 (558) | blend lambda=0.5 | 558 | 0.116 [0.091, 0.143] | 0.179 [0.149, 0.211] | 0.190 [0.158, 0.222] | 0.159 [0.131, 0.190] | 0.159 [0.133, 0.186] |
| auto seed 42 (558) | blend lambda=0.75 | 558 | 0.129 [0.102, 0.158] | 0.177 [0.145, 0.210] | 0.194 [0.161, 0.228] | 0.163 [0.135, 0.193] | 0.166 [0.138, 0.193] |
| auto seed 42 (558) | blend lambda=1.0 | 558 | 0.172 [0.143, 0.203] | 0.296 [0.254, 0.333] | 0.376 [0.337, 0.421] | 0.300 [0.265, 0.337] | 0.255 [0.225, 0.285] |
| auto seed 43 (548) | popularity (reference) | 548 | 0.075 [0.053, 0.099] | 0.210 [0.175, 0.245] | 0.310 [0.268, 0.349] | 0.214 [0.184, 0.247] | 0.171 [0.147, 0.195] |
| auto seed 43 (548) | stacked v2.1 (reference) | 548 | 0.166 [0.133, 0.195] | 0.276 [0.239, 0.314] | 0.352 [0.314, 0.392] | 0.288 [0.253, 0.323] | 0.244 [0.212, 0.274] |
| auto seed 43 (548) | full_v2 (reference) | 548 | 0.071 [0.049, 0.091] | 0.161 [0.131, 0.192] | 0.208 [0.175, 0.241] | 0.168 [0.141, 0.197] | 0.122 [0.101, 0.145] |
| auto seed 43 (548) | blend lambda=0.0 | 548 | 0.071 [0.049, 0.091] | 0.161 [0.131, 0.192] | 0.208 [0.175, 0.241] | 0.168 [0.141, 0.197] | 0.124 [0.103, 0.146] |
| auto seed 43 (548) | blend lambda=0.25 | 548 | 0.108 [0.082, 0.133] | 0.195 [0.162, 0.230] | 0.212 [0.181, 0.246] | 0.171 [0.144, 0.199] | 0.153 [0.128, 0.180] |
| auto seed 43 (548) | blend lambda=0.5 | 548 | 0.111 [0.088, 0.139] | 0.193 [0.161, 0.226] | 0.212 [0.181, 0.246] | 0.171 [0.144, 0.199] | 0.160 [0.134, 0.186] |
| auto seed 43 (548) | blend lambda=0.75 | 548 | 0.128 [0.102, 0.155] | 0.193 [0.161, 0.226] | 0.210 [0.177, 0.245] | 0.170 [0.142, 0.199] | 0.170 [0.143, 0.197] |
| auto seed 43 (548) | blend lambda=1.0 | 548 | 0.166 [0.133, 0.195] | 0.276 [0.239, 0.314] | 0.352 [0.314, 0.392] | 0.288 [0.253, 0.323] | 0.244 [0.212, 0.274] |

**Selection rule (fixed before the run).** Among the lambdas whose automatic-evaluation hit@5 is not below popularity's on both seeds (.328 / .310), choose the highest MRR on queries_v2; ties go to the smaller lambda.

Popularity automatic hit@5: seed 42 0.328, seed 43 0.310.

| lambda | auto hit@5 seed 42 | auto hit@5 seed 43 | eligible | queries_v2 MRR |
|---|---|---|---|---|
| 0.0 | 0.186 | 0.208 | False | 0.428 |
| 0.25 | 0.192 | 0.212 | False | 0.426 |
| 0.5 | 0.190 | 0.212 | False | 0.468 |
| 0.75 | 0.194 | 0.210 | False | 0.468 |
| 1.0 | 0.376 | 0.352 | True | 0.336 |

**Why the rule chose lambda = 1.0.** Only lambda = 1.0 meets the eligibility condition: it keeps the stacked ranker's automatic hit@5 (.376 / .352), while every lambda < 1 falls to about .19 / .21, far below popularity. lambda = 0.5 and 0.75 have the higher queries_v2 MRR (.468 vs .336) but are not eligible.

**Why every lambda < 1 collapses on the automatic evaluation.** Full v2's families (its shortlist roll-up) are always also stacked candidates, because the stacked candidate set is the shortlist families plus the top kNN families. A family on both lists receives both terms of the fused score, so as soon as full v2 has any weight its families outrank the families that only the stacked ranking places high; the blended top 5 is then essentially full v2's families in a new order, and inherits full v2's low automatic hit@5.

**Selection, not test.** lambda was selected on queries_v2, so the queries_v2 numbers in this section are selection numbers, not test numbers. The final independent test is pre-registered in `evaluation/PREREGISTRATION_final.md`.

## Known weaknesses (from `v22/report_v22.md`)

- **Size bias.** The stacked ranker favours large families: on the 21 cause-(b) misses of queries_v2 the mean size of its top-5 families is 25.8 papers vs 5.7 for full v2 (24.8 vs 4.8 on all 55 queries). In 7 of those 21 queries full v2 had a gold family in its top 5 (e.g. linear ordering and symbolic regression at rank 1) that the stacked ranker pushed below rank 5.
- **(1+1) EA runtime example.** For "I need benchmarks for a runtime analysis of a (1+1) EA on pseudo-Boolean functions", OneMax is rank 7 and LeadingOnes rank 30 (reached only through popularity padding) in the stacked ranker; neither is a candidate in BM25 only or in full v2.
- **Full v2 brings in odd single-paper families.** E.g. "Stackelberg duopoly" (rank 1) and "Indoor localization using TOA and RSS" for the differential-evolution demo query, "Gymnasium environments" and "Test-Assignment Problem" for the TSP query; the stacked ranker instead pads with generic suites (DTLZ for TSP; sphere, rastrigin, mnist for software defect prediction).


## Decisions made after seeing queries_v2

queries_v2 was committed at c0f8802 and first scored at 27c4b84 (2026-11-03 06:34 UTC). Nothing was trained on
queries_v2 text or gold, with one exception, the v2.2 λ selection:

- The frozen model files were last changed before queries_v2 was committed: `v21_model.json` (stacker weights,
  tier cut-offs, K) at c7a0e04, `v21.py` at 6b0e1fc, `hybrid.py` and `config.json` at 31b4d55, and families,
  entities and embeddings even earlier. Their hashes are in `evaluation/FROZEN_HASHES.txt`.
- The only code that reads queries_v2 is the scorer and report scripts (`score_human_queries.py`,
  `report_query_sets.py`, `build_results_md.py`) and `v22/run_v22.py`.

Every decision taken after the queries_v2 results were seen:

1. **v2.2 λ, selected on queries_v2 (tuning).** λ was the argmax of queries_v2 MRR among the eligible values
   (`v22/run_v22.py`). The rule chose λ = 1.0, i.e. no change to the ranking. Even so, queries_v2 numbers from then
   on are selection numbers, not test numbers.
2. **Design of the v2.2 experiment (design choice).** The idea of blending full v2 with the stacked ranker, the
   RRF form with k = 60 and the λ grid {0, 0.25, 0.5, 0.75, 1} were all chosen after queries_v2 showed full v2 ahead
   of the stacked ranker.
3. **Eligibility condition for λ (threshold).** The rule required automatic hit@5 ≥ popularity's on both seeds
   (.328 / .310). It was written before the v2.2 run, but after queries_v2 results were known.
4. **Diagnostics (report only).** The diagnostics A1/A2 and the "Known weaknesses" section were chosen because of
   the queries_v2 misses (size bias, the (1+1) EA example).
5. **Secondary systems of the final test (design choice).** Full v2 (λ = 0) and blend λ = 0.5 are in the final
   pre-registration because they did well on queries_v2. Blend 0.5 had the highest queries_v2 MRR (tied with 0.75),
   and the final decision rule lets it replace the primary. It was therefore picked after looking at queries_v2.
6. **Final decision rule on the pooled set (design choice).** Using the pooled t1+t2+t3 set for the product
   decision was decided while writing `evaluation/PREREGISTRATION_final.md`, after queries_v2 and v2.2 results.
7. **CLI wording (display only, no ranking change).** The plain tier meanings in `recommend_v21.py` ("about 1 in 10 /
   6 / 4") were added after queries_v2 was scored. The numbers come from the automatic evaluation, not from queries_v2.
8. **Documentation.** The RESULTS.md limitations about queries_v2 (stacked below full v2, generic suites in the top 5)
   and the provenance answer "Unknown" were added afterwards. They are text only.

Not decided after queries_v2: index hygiene, paper-kNN K, the stacker features and weights, the tier cut-offs, the
dropped margin gate, the two-slate output and the gold of queries_v2. All of these predate it (Part C,
pre-registered in `evaluation/PREREGISTRATION.md`). The gold of queries_v2 and its 55 queries were never edited.

## Independent test

Scoring run started 2026-11-12 15:21:09 IST (cut-off 12 November 2026, 10:00 IST, amendment 6). Single scoring run on t1, t3, t4. Frozen system tag retrieval-v2.2; environment FROZEN_ENV.txt; batched path; ties by family id ascending. Pre-registered in `evaluation/PREREGISTRATION_final.md` and amendments 1-6; scorer `evaluation/score_final.py`; full report `evaluation/report_final.md`; per-query top 5 of every system in `evaluation/scored_queries_final.csv`.

**Sets.** Accepted: t1 (20 valid queries), t3 (20), t4 (20). **t2 was rejected** (100% invalid: every gold id's stored family name differs from the name written next to it; amendment 1) and is excluded from every analysis. No t2b or t5 file was received. No duplicates (maximum cross-set cosine below 0.95).

### Pooled results

| system | role | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| stacked | PRIMARY | 60 | 0.117 [0.050, 0.200] | 0.350 [0.233, 0.467] | 0.433 [0.317, 0.567] | 0.264 [0.181, 0.361] | 0.253 [0.177, 0.341] |
| popularity | secondary | 60 | 0.000 [0.000, 0.000] | 0.050 [0.000, 0.117] | 0.083 [0.017, 0.167] | 0.058 [0.017, 0.125] | 0.034 [0.011, 0.066] |
| full_v2_lambda0 | secondary | 60 | 0.300 [0.183, 0.417] | 0.483 [0.367, 0.617] | 0.517 [0.400, 0.650] | 0.353 [0.253, 0.461] | 0.397 [0.295, 0.513] |
| blend_0.5 | secondary | 60 | 0.283 [0.183, 0.400] | 0.450 [0.333, 0.583] | 0.500 [0.383, 0.633] | 0.336 [0.242, 0.444] | 0.385 [0.285, 0.500] |
| bm25_only | exploratory | 60 | 0.267 [0.150, 0.383] | 0.317 [0.200, 0.433] | 0.350 [0.233, 0.467] | 0.217 [0.131, 0.311] | 0.310 [0.205, 0.426] |
| dense_only | exploratory | 60 | 0.250 [0.150, 0.367] | 0.367 [0.250, 0.483] | 0.417 [0.300, 0.550] | 0.319 [0.219, 0.436] | 0.327 [0.224, 0.440] |
| paper_knn | exploratory | 60 | 0.083 [0.017, 0.167] | 0.100 [0.033, 0.183] | 0.183 [0.083, 0.283] | 0.100 [0.044, 0.169] | 0.130 [0.061, 0.211] |

### Paired comparisons

| comparison | d hit@5 | d MRR |
|---|---|---|
| stacked - popularity | +0.350 [+0.217, +0.483] | +0.219 [+0.140, +0.303] |
| stacked - full_v2_lambda0 | -0.083 [-0.183, +0.017] | -0.144 [-0.223, -0.069] |
| stacked - blend_0.5 | -0.067 [-0.167, +0.033] | -0.132 [-0.202, -0.067] |

### Primary claim

Paired difference in hit@5, stacked ranker v2.2 minus popularity, pooled valid queries: **+0.350 [+0.217, +0.483]**, n = 60, interval width 0.267 (paired bootstrap, 10,000 resamples, seed 42). Lower bound above 0: **SUPPORTED**. The cluster bootstrap over 38 groups of queries sharing a gold family (sensitivity (c)) gives +0.350 [+0.176, +0.530], which agrees with this conclusion.

### Blend decision

Paired MRR advantage of blend 0.5 over the primary: +0.132 [+0.067, +0.202] (10,000 resamples, seed 42). The interval is entirely above 0: **blend 0.5 replaces the primary**. This choice was made after seeing the test. The decision rule was applied after the test results were seen, as pre-registered. The frozen system (tag retrieval-v2.2) and the demo app are not changed by this report.

### Error causes

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

### By group

| group | n | stacked hit@5 | popularity hit@5 | full_v2_lambda0 hit@5 | blend_0.5 hit@5 | stacked MRR |
|---|---|---|---|---|---|---|
| applied / real-world | 21 | 0.619 [0.429, 0.810] | 0.000 [0.000, 0.000] | 0.714 [0.524, 0.905] | 0.714 [0.524, 0.905] | 0.337 [0.212, 0.487] |
| theory / algorithm analysis | 21 | 0.429 [0.238, 0.619] | 0.238 [0.048, 0.429] | 0.381 [0.190, 0.571] | 0.381 [0.190, 0.571] | 0.246 [0.129, 0.374] |
| unusual / niche | 18 | 0.222 [0.056, 0.444] | 0.000 [0.000, 0.000] | 0.444 [0.222, 0.667] | 0.389 [0.167, 0.611] | 0.164 [0.043, 0.336] |

### Confidence tiers

| tier | n | mean top-1 probability | hit@1 |
|---|---|---|---|
| low | 27 | 0.053 | 0.111 [0.000, 0.259] |
| medium | 17 | 0.094 | 0.059 [0.000, 0.176] |
| high | 16 | 0.225 | 0.188 [0.000, 0.375] |

### Sensitivity analyses (descriptive)

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

### Limitations of the independent test

- **Topic overlap between sets.** Gold families shared between sets: {'t1&t3': 9, 't1&t4': 5, 't3&t4': 11}. The same water-network, traffic-signal and UAV path-planning families appear in several sets, and t1 and t4 have the same writer. The cluster bootstrap over 38 groups of queries sharing a gold family gives +0.350 [+0.176, +0.530] for the primary claim.
- **Dependence on one set.** The advantage over popularity is largest on t1; on t3 alone (the only set by the second writer) the interval for hit@5 includes 0 (see sensitivity (a) and leave-one-writer-out).
- **Single-paper gold families.** 73 of the 104 distinct gold families (70%) have fewer than 2 papers in the index, so popularity can rarely find them and every system misses many of them.
- **Provenance gaps.** t1 and t3 have no AI-use statement ("provenance not stated", amendment 3); the t4 statement was relayed by the user, mentions only Copilot (formatting only), and is not in the writer's own words. Sensitivity (d) (only t4) is reported above.
- **Tiers.** On the test, hit@1 by tier is not monotone (low / medium / high), with wide intervals at these sizes.
- **Size.** n = 60; the primary hit@5 interval width is 0.267.
- **Pre-check note.** Before scoring, pre-check (c) found additions since amendment 4 beyond PROVENANCE_t.md: amendments 5 and 6 (pre-registration documents; amendment 6 sets the scoring time used) and the demo app under app/. None changes a frozen file (FROZEN_HASHES.txt verified immediately before the run), so the run went ahead with these documented exceptions.

