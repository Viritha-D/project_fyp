# Retrieval v2.2 experiment: report

Pre-registered in `PREREGISTRATION_v22.md` (71e6287). Frozen v2.1 model only read. **queries_v2 is the selection set for lambda; its numbers for the chosen lambda are optimistic.**

## A1. Demo queries

**I built a new differential evolution variant for 30-dimensional single-objective problems with many local optima.**

| rank | full_v2 | stacked |
|---|---|---|
| 1 | Stackelberg duopoly | BBOB (COCO) |
| 2 | BBOB (COCO) | rastrigin |
| 3 | CEC 2020 suite | DTLZ |
| 4 | Indoor localization using TOA and RSS | CEC 2017 suite |
| 5 | CEC 2011 suite | CEC 2021 suite |

**My multi-objective evolutionary algorithm handles 3 objectives with a concave Pareto front.**

| rank | full_v2 | stacked |
|---|---|---|
| 1 | DTLZ | DTLZ |
| 2 | WFG | ZDT |
| 3 | hypervolume subset selection on {...} pareto fronts | WFG |
| 4 | Multifactorial Evolutionary Algorithm (MFEA) / MFTO-MFEA | CEC 2017 suite |
| 5 | MaF | hypervolume subset selection on {...} pareto fronts |

**I am testing a genetic algorithm for the traveling salesman problem on instances with a few hundred cities.**

| rank | full_v2 | stacked |
|---|---|---|
| 1 | ordered clustered traveling salesman | traveling salesman |
| 2 | traveling salesman | ordered clustered traveling salesman |
| 3 | P-MPR | Traveling Salesman Problem |
| 4 | Test-Assignment Problem | TSPLIB |
| 5 | Gymnasium environments | DTLZ |

**I want to evaluate a feature selection method for high-dimensional gene expression data.**

| rank | full_v2 | stacked |
|---|---|---|
| 1 | eeg feature selection | Feature Selection |
| 2 | Feature Selection | eeg feature selection |
| 3 | High-dimensional feature selection | High-dimensional feature selection |
| 4 | Madelon Feature Selection | Madelon Feature Selection |
| 5 | mRMR Feature Selection | Breast Cancer Feature Selection |

**My evolutionary algorithm tunes hyper-parameters of tree-based models for software defect prediction.**

| rank | full_v2 | stacked |
|---|---|---|
| 1 | hyper parameter optimization of {...} for software bug prediction on {...} | hyper parameter optimization of {...} for software bug prediction on {...} |
| 2 | - | sphere |
| 3 | - | rastrigin |
| 4 | - | mnist |
| 5 | - | rosenbrock |

**I need benchmarks for a runtime analysis of a (1+1) EA on pseudo-Boolean functions.**

| family | n_papers | popularity | bm25_only | dense_only | full_v2 | paper_knn | stacked |
|---|---|---|---|---|---|---|---|
| F00445 OneMax | 32 | 5 | not a candidate | 16 | not a candidate | 5 | 7 |
| F00455 LeadingOnes | 18 | 10 | not a candidate | not a candidate | not a candidate | 137 | 30 (padding) |

**A neuroevolution method for continuous control tasks in simulation.**

| family | n_papers | popularity | bm25_only | dense_only | full_v2 | paper_knn | stacked |
|---|---|---|---|---|---|---|---|
| F00431 Evolution Gym | 1 | 604 | not a candidate | not a candidate | not a candidate | not a candidate | 612 (padding) |
| F00924 OpenAI Gym tasks | 1 | 1016 | 1 | 2 | 2 | 22 | 1 |
| F01314 Evolution Gym | 1 | 1352 | not a candidate | not a candidate | not a candidate | 46 | 1355 (padding) |
| F01404 Gym Hopper | 1 | 1439 | 5 | 37 | 1 | 153 | 6 |
| F01522 Gymnasium environments | 1 | 1552 | not a candidate | 4 | 10 | 71 | 19 |
| F01839 Gymnasium Suite (CartPole-v1, MountainCar-v0, Acrobot-v1, LunarLander-v3, HalfCheetah-v5) | 1 | 1851 | not a candidate | not a candidate | not a candidate | not a candidate | 1850 (padding) |
| F01054 Walker2d | 3 | 81 | 8 | 23 | not a candidate | 3 | 2 |
| F01298 Walker2D | 2 | 214 | not a candidate | not a candidate | not a candidate | 65 | 226 (padding) |
| F01600 Walker2DBullet | 1 | 1625 | not a candidate | not a candidate | not a candidate | not a candidate | 1625 (padding) |
| F01601 Walker2DMuJoCo | 1 | 1626 | not a candidate | not a candidate | not a candidate | not a candidate | 1626 (padding) |

## A2. Cause-(b) misses in queries_v2

21 queries.

| query | gold family | n_papers | rank full_v2 | rank stacked |
|---|---|---|---|---|
| Q01 | ZDT | 20 | not a candidate | 9 |
| Q01 | DTLZ | 45 | not a candidate | 10 |
| Q02 | CEC 2022 suite | 11 | not a candidate | 13 |
| Q02 | CEC 2024 suite | 2 | not a candidate | 21 |
| Q05 | traveling salesman | 8 | not a candidate | 14 |
| Q05 | TSPLIB | 9 | not a candidate | 15 |
| Q08 | The Legend of Zelda Dungeon Generation | 2 | not a candidate | 8 |
| Q08 | Super Mario Bros. Level Generation | 2 | 6 | 10 |
| Q08 | mega man level generation | 1 | not a candidate | 959 (padding) |
| Q10 | bar truss | 2 | 2 | 6 |
| Q11 | DASCMOP | 5 | 4 | 14 |
| Q11 | MW | 2 | not a candidate | 223 (padding) |
| Q11 | lir cmop | 3 | not a candidate | 8 |
| Q15 | LSMOP | 7 | not a candidate | 7 |
| Q15 | MaF | 6 | not a candidate | 48 (padding) |
| Q16 | nguyen | 3 | not a candidate | 89 (padding) |
| Q16 | Synthetic Symbolic Regression Suite | 1 | 5 | 16 |
| Q16 | Symbolic Regression | 1 | 1 | 7 |
| Q19 | linear ordering | 3 | 1 | 9 |
| Q20 | ZDT | 20 | not a candidate | 7 |
| Q20 | Schaffer | 2 | not a candidate | 238 (padding) |
| Q25 | rastrigin | 27 | not a candidate | 9 |
| Q25 | sphere | 32 | not a candidate | 6 |
| Q25 | ackley | 8 | not a candidate | 36 (padding) |
| Q28 | mackey glass | 2 | not a candidate | 16 |
| Q28 | mg (hyperparameter tuning of echo state networks) series | 1 | not a candidate | 1174 (padding) |
| Q34 | Ising Spin Glasses | 1 | 4 | 6 |
| Q34 | Ising spin glass | 2 | 5 | 18 |
| Q34 | Max-Cut Set A (Fully Connected) | 1 | 1 | 10 |
| Q35 | Glass | 2 | not a candidate | 109 (padding) |
| Q35 | Iris | 2 | not a candidate | 130 (padding) |
| Q35 | wine | 4 | not a candidate | 27 |
| Q36 | Neural Architecture Search | 2 | not a candidate | 131 (padding) |
| Q36 | NAS-Bench-201 | 2 | not a candidate | 223 (padding) |
| Q36 | MobileNet-style Neural Architecture Search | 1 | 3 | 10 |
| Q38 | RWMOP (CEC 2021 real-world MOPs) | 1 | 6 | 16 |
| Q38 | RE3-5-4 | 2 | not a candidate | 26 |
| Q38 | RE3-4-7 | 2 | not a candidate | 28 |
| Q39 | rastrigin | 27 | not a candidate | 31 (padding) |
| Q39 | sphere | 32 | not a candidate | 9 |
| Q39 | OneMax | 32 | not a candidate | 30 (padding) |
| Q42 | different powers | 2 | not a candidate | 104 (padding) |
| Q42 | discus | 2 | not a candidate | 133 (padding) |
| Q42 | Ridge | 3 | not a candidate | 13 |
| Q44 | Humanoid (Brax) | 1 | 2 | 23 |
| Q44 | HumanoidBullet | 1 | not a candidate | 1620 (padding) |
| Q44 | Humanoid | 1 | not a candidate | 1736 (padding) |
| Q50 | Fashion_MNIST | 4 | not a candidate | 22 |
| Q50 | FashionMNIST Image Classification | 4 | not a candidate | 54 (padding) |
| Q53 | CEC 2005 suite | 5 | 6 | 12 |

| mean n_papers of the top-5 families | stacked | full_v2 |
|---|---|---|
| the 21 cause-(b) misses | 25.8 | 5.7 |
| all 55 queries | 24.8 | 4.8 |

## B1. Blend curves (score = (1-lambda)/(60+rank_full) + lambda/(60+rank_stacked))

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

## B2. Selection

Popularity automatic hit@5: seed 42 0.328, seed 43 0.310.

| lambda | auto hit@5 seed 42 | auto hit@5 seed 43 | eligible | queries_v2 MRR |
|---|---|---|---|---|
| 0.0 | 0.186 | 0.208 | False | 0.428 |
| 0.25 | 0.192 | 0.212 | False | 0.426 |
| 0.5 | 0.190 | 0.212 | False | 0.468 |
| 0.75 | 0.194 | 0.210 | False | 0.468 |
| 1.0 | 0.376 | 0.352 | True | 0.336 |

**Chosen lambda = 1.0**.

Tier hit@1 of the blended top-1 (lambda = 1.0, automatic evaluation, seeds pooled): low 0.086 (n 372, about 1 in 12), medium 0.177 (n 362, about 1 in 6), high 0.245 (n 372, about 1 in 4)

