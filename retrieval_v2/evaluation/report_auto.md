# Retrieval v2: five-fold automatic evaluation

Papers: 1488; scored queries: 558; **unseen** (no gold family in the fold index, excluded): **930** (62.5%).

Values are means with 95% bootstrap intervals over papers (1,000 resamples). hit@k: a gold family in the top k; recall@5: share of the (seen) gold families in the top 5; MRR: first gold family within the top 10.

## Overall

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr | unmapped |
|---|---|---|---|---|---|---|---|---|
| all | popularity | 558 | 0.066 [0.045, 0.088] | 0.201 [0.165, 0.235] | 0.328 [0.290, 0.371] | 0.227 [0.195, 0.259] | 0.164 [0.140, 0.188] |  |
| all | bm25_only | 558 | 0.041 [0.025, 0.057] | 0.073 [0.054, 0.095] | 0.113 [0.088, 0.140] | 0.096 [0.074, 0.120] | 0.076 [0.060, 0.094] |  |
| all | dense_only | 558 | 0.023 [0.013, 0.036] | 0.057 [0.039, 0.077] | 0.099 [0.073, 0.124] | 0.080 [0.059, 0.102] | 0.058 [0.044, 0.073] |  |
| all | full | 558 | 0.072 [0.050, 0.093] | 0.156 [0.127, 0.186] | 0.186 [0.156, 0.219] | 0.157 [0.130, 0.187] | 0.116 [0.095, 0.139] | 0.520 [0.478, 0.559] |

**The full pipeline does not beat the popularity baseline on: hit@3, hit@5, recall@5, mrr.**

## By Category

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr | unmapped |
|---|---|---|---|---|---|---|---|---|
| Applied | popularity | 158 | 0.000 [0.000, 0.000] | 0.006 [0.000, 0.019] | 0.013 [0.000, 0.032] | 0.004 [0.000, 0.011] | 0.006 [0.001, 0.014] |  |
| Applied | bm25_only | 158 | 0.044 [0.013, 0.076] | 0.076 [0.038, 0.120] | 0.120 [0.076, 0.171] | 0.107 [0.062, 0.158] | 0.078 [0.045, 0.113] |  |
| Applied | dense_only | 158 | 0.044 [0.013, 0.082] | 0.076 [0.038, 0.114] | 0.082 [0.044, 0.127] | 0.067 [0.032, 0.105] | 0.065 [0.034, 0.102] |  |
| Applied | full | 158 | 0.101 [0.057, 0.152] | 0.139 [0.088, 0.196] | 0.152 [0.095, 0.209] | 0.134 [0.083, 0.188] | 0.122 [0.076, 0.170] | 0.582 [0.506, 0.658] |
| Pure Math | popularity | 400 | 0.092 [0.067, 0.125] | 0.278 [0.235, 0.320] | 0.453 [0.405, 0.502] | 0.315 [0.276, 0.355] | 0.226 [0.198, 0.256] |  |
| Pure Math | bm25_only | 400 | 0.040 [0.022, 0.058] | 0.072 [0.050, 0.100] | 0.110 [0.080, 0.140] | 0.092 [0.066, 0.118] | 0.075 [0.056, 0.095] |  |
| Pure Math | dense_only | 400 | 0.015 [0.005, 0.028] | 0.050 [0.030, 0.072] | 0.105 [0.077, 0.135] | 0.085 [0.060, 0.112] | 0.055 [0.041, 0.069] |  |
| Pure Math | full | 400 | 0.060 [0.037, 0.083] | 0.163 [0.128, 0.198] | 0.200 [0.160, 0.240] | 0.166 [0.132, 0.200] | 0.114 [0.089, 0.141] | 0.495 [0.447, 0.547] |

## By Conference

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr | unmapped |
|---|---|---|---|---|---|---|---|---|
| CEC | popularity | 152 | 0.092 [0.046, 0.138] | 0.289 [0.211, 0.362] | 0.309 [0.230, 0.382] | 0.236 [0.176, 0.300] | 0.211 [0.159, 0.263] |  |
| CEC | bm25_only | 152 | 0.026 [0.007, 0.053] | 0.039 [0.013, 0.072] | 0.039 [0.013, 0.072] | 0.036 [0.013, 0.069] | 0.044 [0.021, 0.073] |  |
| CEC | dense_only | 152 | 0.020 [0.000, 0.046] | 0.086 [0.046, 0.132] | 0.164 [0.105, 0.224] | 0.145 [0.089, 0.202] | 0.088 [0.059, 0.120] |  |
| CEC | full | 152 | 0.072 [0.033, 0.118] | 0.211 [0.151, 0.276] | 0.224 [0.158, 0.296] | 0.197 [0.137, 0.259] | 0.135 [0.091, 0.182] | 0.559 [0.480, 0.638] |
| FOGA | popularity | 47 | 0.000 [0.000, 0.000] | 0.128 [0.043, 0.234] | 0.574 [0.426, 0.723] | 0.384 [0.268, 0.505] | 0.154 [0.119, 0.189] |  |
| FOGA | bm25_only | 47 | 0.043 [0.000, 0.106] | 0.106 [0.021, 0.191] | 0.213 [0.085, 0.319] | 0.181 [0.074, 0.287] | 0.113 [0.053, 0.178] |  |
| FOGA | dense_only | 47 | 0.000 [0.000, 0.000] | 0.021 [0.000, 0.064] | 0.085 [0.021, 0.170] | 0.074 [0.011, 0.149] | 0.030 [0.008, 0.057] |  |
| FOGA | full | 47 | 0.128 [0.043, 0.234] | 0.170 [0.064, 0.277] | 0.234 [0.106, 0.362] | 0.202 [0.096, 0.319] | 0.156 [0.067, 0.256] | 0.574 [0.426, 0.723] |
| GECCO | popularity | 313 | 0.070 [0.042, 0.102] | 0.182 [0.141, 0.227] | 0.316 [0.265, 0.364] | 0.221 [0.182, 0.260] | 0.153 [0.122, 0.185] |  |
| GECCO | bm25_only | 313 | 0.032 [0.016, 0.054] | 0.064 [0.038, 0.096] | 0.105 [0.073, 0.141] | 0.087 [0.058, 0.117] | 0.067 [0.048, 0.091] |  |
| GECCO | dense_only | 313 | 0.013 [0.003, 0.026] | 0.029 [0.013, 0.048] | 0.045 [0.022, 0.067] | 0.029 [0.014, 0.046] | 0.030 [0.016, 0.045] |  |
| GECCO | full | 313 | 0.042 [0.019, 0.064] | 0.099 [0.067, 0.134] | 0.137 [0.096, 0.176] | 0.109 [0.077, 0.141] | 0.079 [0.054, 0.103] | 0.505 [0.450, 0.559] |
| PPSN | popularity | 5 | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 1.000 [1.000, 1.000] | 0.311 [0.267, 0.333] | 0.440 [0.230, 0.750] |  |
| PPSN | bm25_only | 5 | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.400 [0.000, 0.800] | 0.100 [0.000, 0.233] | 0.250 [0.000, 0.601] |  |
| PPSN | dense_only | 5 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.033 [0.000, 0.100] | 0.040 [0.000, 0.120] |  |
| PPSN | full | 5 | 0.000 [0.000, 0.000] | 0.200 [0.000, 0.600] | 0.200 [0.000, 0.600] | 0.067 [0.000, 0.200] | 0.100 [0.000, 0.233] | 0.400 [0.000, 0.800] |
| PReMI | popularity | 41 | 0.000 [0.000, 0.000] | 0.073 [0.000, 0.146] | 0.122 [0.024, 0.220] | 0.044 [0.012, 0.088] | 0.048 [0.012, 0.091] |  |
| PReMI | bm25_only | 41 | 0.146 [0.049, 0.244] | 0.220 [0.098, 0.341] | 0.293 [0.146, 0.439] | 0.293 [0.146, 0.439] | 0.194 [0.085, 0.304] |  |
| PReMI | dense_only | 41 | 0.146 [0.049, 0.244] | 0.220 [0.098, 0.341] | 0.268 [0.122, 0.390] | 0.240 [0.110, 0.362] | 0.192 [0.089, 0.294] |  |
| PReMI | full | 41 | 0.244 [0.098, 0.390] | 0.366 [0.220, 0.488] | 0.366 [0.220, 0.488] | 0.337 [0.195, 0.476] | 0.293 [0.163, 0.423] | 0.439 [0.293, 0.586] |

## By gold evidence

| group | system | n | hit@1 | hit@3 | hit@5 | recall@5 | mrr | unmapped |
|---|---|---|---|---|---|---|---|---|
| gold families < 2 training papers | popularity | 124 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |  |
| gold families < 2 training papers | bm25_only | 124 | 0.048 [0.016, 0.089] | 0.065 [0.024, 0.113] | 0.105 [0.056, 0.169] | 0.105 [0.056, 0.169] | 0.071 [0.035, 0.115] |  |
| gold families < 2 training papers | dense_only | 124 | 0.056 [0.024, 0.097] | 0.065 [0.032, 0.113] | 0.065 [0.032, 0.113] | 0.065 [0.032, 0.113] | 0.065 [0.030, 0.109] |  |
| gold families < 2 training papers | full | 124 | 0.081 [0.032, 0.129] | 0.097 [0.048, 0.153] | 0.105 [0.056, 0.161] | 0.105 [0.056, 0.161] | 0.090 [0.046, 0.139] | 0.508 [0.419, 0.597] |
| gold family >= 2 training papers | popularity | 434 | 0.085 [0.060, 0.113] | 0.258 [0.219, 0.300] | 0.422 [0.373, 0.468] | 0.291 [0.255, 0.329] | 0.210 [0.183, 0.240] |  |
| gold family >= 2 training papers | bm25_only | 434 | 0.039 [0.023, 0.058] | 0.076 [0.053, 0.101] | 0.115 [0.087, 0.145] | 0.094 [0.069, 0.119] | 0.077 [0.059, 0.097] |  |
| gold family >= 2 training papers | dense_only | 434 | 0.014 [0.005, 0.028] | 0.055 [0.035, 0.078] | 0.108 [0.081, 0.138] | 0.084 [0.061, 0.110] | 0.055 [0.042, 0.072] |  |
| gold family >= 2 training papers | full | 434 | 0.069 [0.046, 0.092] | 0.173 [0.141, 0.207] | 0.210 [0.173, 0.249] | 0.172 [0.140, 0.206] | 0.124 [0.100, 0.149] | 0.523 [0.475, 0.567] |

## Margin gate (full pipeline)

| subset | n | hit@1 |
|---|---|---|
| mapped (margin >= threshold or one family) | 268 | 0.067 [0.037, 0.097] |
| not mapped | 290 | 0.076 [0.048, 0.107] |

| margin quintile | n | hit@1 |
|---|---|---|
| (-0.001, 0.252] | 112 | 0.071 [0.027, 0.125] |
| (0.252, 0.668] | 111 | 0.081 [0.036, 0.135] |
| (0.668, 1.361] | 112 | 0.071 [0.027, 0.116] |
| (1.361, 2.437] | 111 | 0.045 [0.009, 0.081] |
| (2.437, 11.962] | 112 | 0.089 [0.044, 0.143] |

Spearman correlation of margin and hit@1 (queries with a margin): 0.015
Queries whose shortlist held one family only (no margin, counted as mapped): 0, hit@1 -
Margin distribution (full pipeline): {0.0: 0.0, 0.1: 0.136, 0.25: 0.335, 0.5: 0.918, 0.75: 2.067, 0.9: 3.376, 1.0: 11.962}; share >= 1.0: 0.480

## Examples (full pipeline)

- **HIT (gold family ranked 1st)** `CEC|2020|moeadwithrandompartialupdatestrategy` (Pure Math, CEC), mapped=False
  - query: I developed MOEA/D-PS (ps=0.), MOEA/D-DE (standard), MOEA/D-RI (Relative Improvement-based resource allocation) for Evaluating mathematical landscapes; dimension 100D; landscape Multimodal, Concave Pareto Front, Linear Pareto Front, Convex Pareto Front; results measured by Hypervolume (HV), Inverted Generational Distance (IGD), Proportion of non-dominated solutions (NDOM). Which benchmarks should I test it on?
  - top 3: DTLZ (-5.562); Not Reported (-6.229); CEC 2009 suite (-6.509)
  - gold: DTLZ; UF (CEC 2009 unconstrained)
- **HIT (gold family ranked 1st)** `FOGA|2017|resamplingvsrecombinationastatisticalruntimeestimation` (Pure Math, FOGA), mapped=False
  - query: I developed (mu + 1)-EA, (mu + 1)-GA, Compact Genetic Algorithm (cGA) for Evaluating mathematical landscapes; dimension 100D; landscape Unimodal, Separable, noisy, additive posterior Gaussian noise; results measured by Number of fitness evaluations to reach the optimum. Which benchmarks should I test it on?
  - top 3: OneMax (-4.054); Not Reported (-4.755); BBOB (COCO) (-6.138)
  - gold: OneMax
- **HIT (gold family ranked 1st)** `CEC|2022|randomlearningparticleswarmoptimizationwithquasinewtonexploitationmechanism` (Pure Math, CEC), mapped=False
  - query: I developed RQ-PSO for Evaluating mathematical landscapes; dimension 30D; landscape Multimodal, unimodal, multimodal, composition; results measured by Mean value, standard deviation, and ranking. Which benchmarks should I test it on?
  - top 3: CEC 2013 suite (0.427); 23 classical benchmark functions (unimodal, multimodal, fixed-dimension multimodal) (0.171); CEC 2014 suite (-0.529)
  - gold: CEC 2017 suite; CEC 2013 suite
- **HIT (gold family ranked 1st)** `GECCO|2026|parentselectionmechanismsinelitistcrossoverbasedalgorithms` (Pure Math, GECCO), mapped=False
  - query: I developed (\mu + 1) GA with furthest parent selection for Evaluating mathematical landscapes; dimension Variable; landscape Multimodal, plateau, local optima, fitness valley; results measured by Expected number of fitness evaluations to find the global optimum. Which benchmarks should I test it on?
  - top 3: Jump (-3.653); Not Reported (-3.700); OneMax (-4.291)
  - gold: Jump
- **HIT (gold family ranked 1st)** `GECCO|2021|geneticprogrammingforborderlineinstancedetectioninhighdimensionalunbalancedclassification` (Applied, GECCO), mapped=False
  - query: I developed COSGP, GP_Aucw for High-dimensional unbalanced classification in Medical/Healthcare; dimension 1081D; landscape high-dimensional, unbalanced, class overlap; results measured by Mean AUC of 98.42% on test set. Which benchmarks should I test it on?
  - top 3: leukemia (-3.105); tumors (-3.504); brain tumor (-3.593)
  - gold: leukemia
- **MISS (no gold family in the top 5)** `FOGA|2017|qualitygainanalysisoftheweightedrecombinationevolutionstrategyongeneralconvexquadraticfunctions` (Pure Math, FOGA), mapped=False
  - query: I developed Weighted Recombination Evolution Strategy for Evaluating mathematical landscapes; dimension Variable; landscape Unimodal, Separable, convex, quadratic, ill-conditioned; results measured by Empirical normalized quality gain. Which benchmarks should I test it on?
  - top 3: separable ellipsoid (-2.542); BBOB (COCO) (-2.685); Not Reported (-3.214)
  - gold: sphere; ellipsoid; cigar; discus
- **MISS (no gold family in the top 5)** `GECCO|2020|multilayerlocaloptimanetworksfortheanalysisofadvancedlocalsearchbasedalgorithms` (Pure Math, GECCO), mapped=False
  - query: I developed Best-improvement Hill Climbing with Bit-flip, Best-improvement Hill Climbing with 1-swap, Best-improvement Hill Climbing with Multi-layer (Bit-flip + 1-swap) for Evaluating mathematical landscapes; dimension 18D; landscape Multimodal, Non-separable, rugged, combinatorial; results measured by Average shortest path to global optima (lGO). Which benchmarks should I test it on?
  - top 3: EqualBlocksOneMax (EBOM) (-4.909); Hill-valley (-5.350); CEC 2017 suite (-5.813)
  - gold: NK landscape
- **MISS (no gold family in the top 5)** `GECCO|2022|multimodalmultiobjectivemodelbasedgeneticprogrammingtofindmultiplediversehighqualitymodels` (Applied, GECCO), mapped=False
  - query: I developed MO-GP-GOMEA, SO GP-GOMEA, NSGA-II for Predicting median house value in Engineering/Manufacturing; dimension 13D; landscape Multimodal, Separable, noisy; results measured by Hypervolume (HV), diversified error (D), and error (E). Which benchmarks should I test it on?
  - top 3: Benchmark II (-9.100); binval (-9.303); Benchmark I (-9.546)
  - gold: Boston housing; Concrete Compressive Strength
- **MISS (no gold family in the top 5)** `GECCO|2021|interactiveevolutionarymultipleobjectiveoptimizationalgorithmusingafastcalculationofholisticacceptabilities` (Pure Math, GECCO), mapped=True
  - query: I developed iMOEA-HA, EMOSOR, IEMO/D for Evaluating mathematical landscapes; dimension Variable (22D to 28D); landscape complex; results measured by Average Relative Score Difference (ARSD). Which benchmarks should I test it on?
  - top 3: Not Reported (-2.557); CEC 2017 suite (-5.583); 23 classical benchmark functions (unimodal, multimodal, fixed-dimension multimodal) (-5.591)
  - gold: WFG
- **MISS (no gold family in the top 5)** `GECCO|2024|runtimephylogeneticanalysisenablesextremesubsamplingfortestbasedproblems` (Pure Math, GECCO), mapped=False
  - query: I developed Down-sampling without estimation (DS), Down-sampling with phylogeny-based estimation (DS-EST), Individualized Random Sampling (IRS) for my problem; dimension 100 training cases; results measured by Problem-solving success rate (number of successful replicates out of 50). Which benchmarks should I test it on?
  - top 3: task series (-6.359); CELLPOSE dataset (-6.868); Benchmark I (-7.017)
  - gold: Median; Smallest; Fizz Buzz; Grade; Small Or Large
