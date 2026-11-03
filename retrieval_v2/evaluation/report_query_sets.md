# Written query sets: scoring report

Models frozen at tag `retrieval-v2.1-frozen` (c0f8802). Pre-registration: `PREREGISTRATION_queries.md` (aed8464, committed before scoring). The query file was committed before any scoring (c0f8802; marker 2bf6321).

## Provenance (from `PROVENANCE.md`, unedited)

> Queries written by: Sanjesh. Gold families chosen by: Darshan . Date and time finished: 3/11/26 11:43.
> Tools used (including any AI tool): IEEE(reference. System outputs seen before the file was final: Unknown.

The answer to "System outputs seen before the file was final" is "Unknown" (filled in by the user on request). The "Tools used" entry reads "IEEE(reference." as given.

## Gold validation

126 gold ids in 55 queries; every id exists in families_v5, none is a hygiene-excluded family (F02124 "Not Reported", F00334 "Evolutionary Algorithm"), every `gold_family_names` entry equals the family name: **0 mismatches**; no query without valid gold.

## Primary set: `queries_v2.csv`


Frozen models (tag retrieval-v2.1-frozen). Means with 95% bootstrap intervals over queries.

### Overall

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| all | popularity | 55 | 0.036 [0.000, 0.091] | 0.164 [0.073, 0.273] | 0.200 [0.091, 0.309] | 0.103 [0.045, 0.164] | 0.102 [0.048, 0.172] |
| all | bm25_only | 55 | 0.236 [0.127, 0.345] | 0.400 [0.272, 0.527] | 0.455 [0.327, 0.582] | 0.230 [0.158, 0.309] | 0.316 [0.207, 0.422] |
| all | dense_only | 55 | 0.218 [0.109, 0.345] | 0.455 [0.309, 0.582] | 0.527 [0.400, 0.655] | 0.367 [0.258, 0.473] | 0.354 [0.252, 0.460] |
| all | full_v2 | 55 | 0.327 [0.200, 0.455] | 0.509 [0.382, 0.636] | 0.564 [0.436, 0.691] | 0.364 [0.264, 0.464] | 0.423 [0.311, 0.536] |
| all | paper_knn | 55 | 0.091 [0.018, 0.182] | 0.309 [0.200, 0.436] | 0.400 [0.273, 0.527] | 0.242 [0.161, 0.336] | 0.230 [0.161, 0.316] |
| all | stacked | 55 | 0.200 [0.091, 0.309] | 0.400 [0.273, 0.527] | 0.491 [0.363, 0.618] | 0.294 [0.206, 0.394] | 0.336 [0.239, 0.433] |

### Primary comparisons (paired bootstrap, stacked minus reference)

| comparison | d hit@5 | d MRR |
|---|---|---|
| stacked - popularity | 0.291 [0.127, 0.436] | 0.234 [0.131, 0.341] |
| stacked - full_v2 | -0.073 [-0.182, 0.036] | -0.086 [-0.186, 0.002] |

### By group

Group sizes: continuous single-objective 15, multi-objective 10, combinatorial 10, machine learning 10, vague 5, control / RL 5

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr |
|---|---|---|---|---|---|---|---|
| combinatorial | popularity | 10 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| combinatorial | bm25_only | 10 | 0.400 [0.100, 0.700] | 0.700 [0.400, 0.902] | 0.700 [0.400, 0.902] | 0.433 [0.233, 0.617] | 0.517 [0.250, 0.784] |
| combinatorial | dense_only | 10 | 0.400 [0.100, 0.700] | 0.900 [0.700, 1.000] | 0.900 [0.700, 1.000] | 0.750 [0.550, 0.917] | 0.646 [0.442, 0.850] |
| combinatorial | full_v2 | 10 | 0.800 [0.500, 1.000] | 0.900 [0.700, 1.000] | 0.900 [0.700, 1.000] | 0.783 [0.550, 1.000] | 0.850 [0.600, 1.000] |
| combinatorial | paper_knn | 10 | 0.100 [0.000, 0.300] | 0.300 [0.000, 0.600] | 0.500 [0.200, 0.800] | 0.383 [0.133, 0.650] | 0.263 [0.087, 0.475] |
| combinatorial | stacked | 10 | 0.300 [0.100, 0.600] | 0.600 [0.300, 0.900] | 0.700 [0.400, 0.900] | 0.467 [0.250, 0.683] | 0.481 [0.262, 0.706] |
| continuous single-objective | popularity | 15 | 0.000 [0.000, 0.000] | 0.400 [0.200, 0.667] | 0.467 [0.267, 0.733] | 0.233 [0.111, 0.367] | 0.194 [0.089, 0.311] |
| continuous single-objective | bm25_only | 15 | 0.133 [0.000, 0.333] | 0.200 [0.000, 0.400] | 0.200 [0.000, 0.400] | 0.067 [0.000, 0.133] | 0.167 [0.000, 0.367] |
| continuous single-objective | dense_only | 15 | 0.067 [0.000, 0.200] | 0.267 [0.067, 0.467] | 0.333 [0.133, 0.600] | 0.178 [0.056, 0.333] | 0.183 [0.050, 0.350] |
| continuous single-objective | full_v2 | 15 | 0.200 [0.000, 0.400] | 0.267 [0.067, 0.533] | 0.333 [0.133, 0.600] | 0.133 [0.056, 0.233] | 0.250 [0.083, 0.467] |
| continuous single-objective | paper_knn | 15 | 0.133 [0.000, 0.333] | 0.267 [0.067, 0.467] | 0.333 [0.133, 0.600] | 0.167 [0.056, 0.322] | 0.243 [0.106, 0.423] |
| continuous single-objective | stacked | 15 | 0.200 [0.000, 0.400] | 0.400 [0.200, 0.667] | 0.400 [0.200, 0.667] | 0.222 [0.089, 0.400] | 0.300 [0.122, 0.511] |
| control / RL | popularity | 5 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| control / RL | bm25_only | 5 | 0.400 [0.000, 0.800] | 0.400 [0.000, 0.800] | 0.600 [0.200, 1.000] | 0.233 [0.067, 0.400] | 0.440 [0.040, 0.840] |
| control / RL | dense_only | 5 | 0.200 [0.000, 0.600] | 0.600 [0.200, 1.000] | 0.800 [0.400, 1.000] | 0.400 [0.200, 0.600] | 0.407 [0.140, 0.733] |
| control / RL | full_v2 | 5 | 0.200 [0.000, 0.600] | 0.800 [0.400, 1.000] | 0.800 [0.400, 1.000] | 0.433 [0.200, 0.633] | 0.467 [0.267, 0.733] |
| control / RL | paper_knn | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.200 [0.000, 0.467] | 0.140 [0.000, 0.340] |
| control / RL | stacked | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.600 [0.200, 1.000] | 0.233 [0.067, 0.400] | 0.205 [0.065, 0.365] |
| machine learning | popularity | 10 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| machine learning | bm25_only | 10 | 0.300 [0.000, 0.600] | 0.600 [0.300, 0.900] | 0.600 [0.300, 0.900] | 0.317 [0.133, 0.517] | 0.417 [0.167, 0.683] |
| machine learning | dense_only | 10 | 0.400 [0.100, 0.700] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.333 [0.100, 0.600] | 0.450 [0.175, 0.738] |
| machine learning | full_v2 | 10 | 0.200 [0.000, 0.500] | 0.600 [0.300, 0.900] | 0.600 [0.300, 0.900] | 0.350 [0.150, 0.567] | 0.350 [0.133, 0.583] |
| machine learning | paper_knn | 10 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.500] | 0.300 [0.098, 0.600] | 0.200 [0.049, 0.450] | 0.120 [0.033, 0.227] |
| machine learning | stacked | 10 | 0.200 [0.000, 0.500] | 0.400 [0.100, 0.700] | 0.400 [0.100, 0.700] | 0.250 [0.050, 0.483] | 0.308 [0.087, 0.562] |
| multi-objective | popularity | 10 | 0.100 [0.000, 0.300] | 0.100 [0.000, 0.300] | 0.100 [0.000, 0.300] | 0.050 [0.000, 0.150] | 0.111 [0.000, 0.311] |
| multi-objective | bm25_only | 10 | 0.200 [0.000, 0.500] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.267 [0.083, 0.467] | 0.299 [0.091, 0.553] |
| multi-objective | dense_only | 10 | 0.200 [0.000, 0.500] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.367 [0.133, 0.667] | 0.325 [0.100, 0.550] |
| multi-objective | full_v2 | 10 | 0.300 [0.000, 0.600] | 0.400 [0.100, 0.700] | 0.500 [0.200, 0.800] | 0.317 [0.117, 0.567] | 0.392 [0.150, 0.667] |
| multi-objective | paper_knn | 10 | 0.100 [0.000, 0.300] | 0.400 [0.100, 0.700] | 0.400 [0.100, 0.700] | 0.217 [0.050, 0.400] | 0.242 [0.078, 0.462] |
| multi-objective | stacked | 10 | 0.100 [0.000, 0.300] | 0.300 [0.000, 0.600] | 0.400 [0.100, 0.700] | 0.233 [0.050, 0.433] | 0.266 [0.118, 0.452] |
| vague | popularity | 5 | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.600 [0.200, 1.000] | 0.333 [0.100, 0.567] | 0.317 [0.050, 0.667] |
| vague | bm25_only | 5 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.067 [0.000, 0.200] | 0.070 [0.000, 0.170] |
| vague | dense_only | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.100 [0.000, 0.300] |
| vague | full_v2 | 5 | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.267 [0.000, 0.600] | 0.250 [0.000, 0.600] |
| vague | paper_knn | 5 | 0.200 [0.000, 0.600] | 0.600 [0.200, 1.000] | 0.600 [0.200, 1.000] | 0.367 [0.067, 0.700] | 0.412 [0.157, 0.725] |
| vague | stacked | 5 | 0.400 [0.000, 0.800] | 0.400 [0.000, 0.800] | 0.600 [0.200, 1.000] | 0.433 [0.100, 0.767] | 0.484 [0.129, 0.840] |

### Stacked confidence tiers (frozen cut-offs)

| tier | n | mean predicted p(top-1 gold) | hit@1 |
|---|---|---|---|
| low | 23 | 0.048 | 0.130 [0.000, 0.304] |
| medium | 19 | 0.097 | 0.158 [0.000, 0.316] |
| high | 13 | 0.306 | 0.385 [0.154, 0.615] |


## Secondary set: `ai_queries_v1.csv`

**Not run**: `ai_queries_v1.csv` is not in the repository, on any branch, or among the uploaded files. It will be scored with the same frozen script when supplied.

## Secondary set: `queries_reworded_v1.csv`

**Not run**: `queries_reworded_v1.csv` is not in the repository, on any branch, or among the uploaded files. It will be scored with the same frozen script when supplied.

## Error analysis (primary set, stacked ranker, no gold family in the top 5)

Misses: 28 of 55 queries.

| cause | queries | of which (c): every gold family has < 2 papers |
|---|---|---|
| (a) no gold family among the candidates | 7 | 0 |
| (b) gold among candidates, ranked below 5 | 21 | 1 |

(c) every gold family has fewer than 2 papers in the index: 1 of 28 misses; at least one gold family with fewer than 2 papers: 7.

Misses by group: continuous single-objective 9, machine learning 6, multi-objective 6, combinatorial 3, vague 2, control / RL 2

### First 15 misses (query_id order)

- **Q01** (vague), cause (b)
  - query: what are the 'standard' test problems for multi objective stuff
  - gold: ZDT; DTLZ
  - stacked top 5: 19 dynamic multi-objective test problems; BBOB (COCO); custom multi objective; Multi-objective problems (unspecified); CEC 2017 suite
- **Q02** (continuous single-objective), cause (b)
  - query: want to compare against this years single objective competition winners on the same functions, 10D and 20D, bound constrained. which is the newest set?
  - gold: CEC 2022 suite; CEC 2024 suite
  - stacked top 5: CEC 2021 suite; CEC 2020 suite; DTLZ; BBOB (COCO); CEC 2014 suite
- **Q05** (combinatorial), cause (b)
  - query: my TSP heuristic should scale to really large instances, 10k+ cities, some clustered. which instance libraries have that with best known tours
  - gold: traveling salesman; TSPLIB
  - stacked top 5: TSP Instance Generation; rosenbrock; CEC 2013 suite; Orienteering Problem (21 Large-Scale Instances); tsp instance generation for {...} vs {...}
- **Q06** (machine learning), cause (a)
  - query: evolving boolean programs / classifier systems on tasks where address bits select one data bit, or where the output depends on whether the number of ones is odd or even
  - gold: parity; multiplexer
  - stacked top 5: OneMax; BBOB (COCO); sphere; 10-bit Carry-one and 11-bit Even-parity; cryptographic boolean
- **Q08** (control / RL), cause (b)
  - query: procedural content generation, evolving levels for 2D platformer games and dungeons for adventure games, judged by playability
  - gold: The Legend of Zelda Dungeon Generation; Super Mario Bros. Level Generation; mega man level generation
  - stacked top 5: Maze Generation; Game Content Generation Problems; game mechanic generation; sphere; rastrigin
- **Q10** (multi-objective), cause (b)
  - query: structural optimisation with two objectives, min weight and min displacement for truss structures. which test cases are common
  - gold: bar truss
  - stacked top 5: BBOB (COCO); CEC 2017 suite; DTLZ; CEC 2013 suite; RE2-4-1
- **Q11** (multi-objective), cause (b)
  - query: my constraint handling for MOEAs needs problems where infeasible barriers sit right in front of the true front. two objectives, maybe 15 vars
  - gold: DASCMOP; MW; lir cmop
  - stacked top 5: DTLZ; OneMax; CEC 2017 suite; LeadingOnes; WFG
- **Q13** (multi-objective), cause (a)
  - query: is there a tunable multi objective problem on bit strings where i can control how correlated the objectives are and how rugged each one is?
  - gold: rho-mnk-landscapes; MNK-landscapes
  - stacked top 5: BBOB (COCO); DTLZ; {...} objective {...} problem; custom multi objective; CEC 2017 suite
- **Q15** (multi-objective), cause (b)
  - query: many-objective, 8 to 15 obj, with a few hundred decision variables. my algorithm uses variable grouping. what test problems scale like that
  - gold: LSMOP; MaF
  - stacked top 5: DTLZ; BBOB (COCO); objective; custom multi objective; ZDT
- **Q16** (machine learning), cause (b)
  - query: doing GP symbolic regression and want ground-truth physics style equations so i can check if it recovers the exact formula
  - gold: nguyen; Synthetic Symbolic Regression Suite; Symbolic Regression
  - stacked top 5: CEC 2017 suite; DTLZ; BBOB (COCO); sphere; CEC 2013 suite
- **Q19** (combinatorial), cause (b)
  - query: need instances for ordering the rows/cols of a matrix to maximise the sum above the diagonal. sizes 50 to 250
  - gold: linear ordering
  - stacked top 5: CEC 2017 suite; BBOB (COCO); OneMax; traveling salesman; CEC 2013 suite
- **Q20** (multi-objective), cause (b)
  - query: teaching NSGA-II vs MOEA/D in a lab session, need really simple bi-objective problems with 1 or 2 variables so we can plot both spaces
  - gold: ZDT; Schaffer
  - stacked top 5: BBOB (COCO); DTLZ; NK landscape; {...} objective {...} problem; OneMax
- **Q24** (continuous single-objective), cause (a)
  - query: Is there a test set where the goal is to hit the optimum to like 10 correct digits on a few really hard functions? want to see how far my DE can push accuracy
  - gold: CEC 2019 suite
  - stacked top 5: CEC 2013 suite; BBOB (COCO); CEC 2017 suite; DTLZ; CEC 2014 suite
- **Q25** (continuous single-objective), cause (b)
  - query: made a new grey wolf style optimizer and my supervisor wants the usual classic test functions, the smooth bowl one plus a couple of multimodal ones, all at 30 dims. which ones should i include
  - gold: rastrigin; sphere; ackley
  - stacked top 5: LeadingOnes; BBOB (COCO); CEC 2013 suite; DTLZ; CEC 2017 suite
- **Q28** (machine learning), cause (b)
  - query: using an EA to tune echo state networks for predicting a chaotic time series generated by a delay differential equation
  - gold: mackey glass; mg (hyperparameter tuning of echo state networks) series
  - stacked top 5: spanish electricity market; sphere; CEC 2013 suite; Time Series Forecasting; Spatio-temporal prediction
