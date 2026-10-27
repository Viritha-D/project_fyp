# Audit report: master_dataset_clean.csv

Input: `master_dataset_clean.csv`, 11342 rows x 29 columns, read with every column as text. The input is not modified; `papers_master_v2.csv` is a byte-identical frozen copy.

Checks passed: 11,342 rows; 29 columns in the expected order; Paper_ID unique and never empty.

## Rows by Conference x Year

| Conference | 2000 | 2004 | 2006 | 2008 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CEC | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 265 | 1213 | 1429 | 204 | 389 | 175 | 0 | 0 | 3675 |
| FOGA | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 170 | 0 | 76 | 0 | 73 | 0 | 51 | 0 | 97 | 0 | 0 | 0 | 467 |
| GECCO | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1205 | 614 | 588 | 697 | 914 | 1470 | 962 | 6450 |
| PPSN | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 22 | 0 | 15 | 0 | 14 | 0 | 28 | 0 | 13 | 0 | 0 | 92 |
| PReMI | 1 | 3 | 1 | 2 | 9 | 11 | 10 | 7 | 24 | 33 | 33 | 118 | 9 | 25 | 16 | 53 | 25 | 267 | 11 | 0 | 0 | 658 |
| Total | 1 | 3 | 1 | 2 | 9 | 11 | 10 | 7 | 24 | 203 | 55 | 194 | 24 | 363 | 2448 | 2147 | 845 | 1450 | 1113 | 1470 | 962 | 11342 |

## Papers by Conference x Year

Paper = distinct `paper_key` (Conference|Year|normalised title; untitled papers keyed by Source_File).

| Conference | 2000 | 2004 | 2006 | 2008 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CEC | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 54 | 92 | 67 | 97 | 59 | 0 | 0 | 378 |
| FOGA | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 17 | 0 | 13 | 0 | 15 | 0 | 10 | 0 | 14 | 0 | 0 | 0 | 69 |
| GECCO | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 149 | 97 | 79 | 89 | 114 | 96 | 126 | 750 |
| PPSN | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 5 |
| PReMI | 1 | 1 | 1 | 2 | 5 | 6 | 4 | 2 | 13 | 9 | 21 | 49 | 5 | 12 | 8 | 19 | 3 | 124 | 7 | 0 | 0 | 292 |
| Total | 1 | 1 | 1 | 2 | 5 | 6 | 4 | 2 | 13 | 26 | 22 | 62 | 6 | 36 | 212 | 218 | 150 | 324 | 181 | 96 | 126 | 1494 |

## Category counts

| Category | rows | papers |
|---|---|---|
| Pure Math | 6675 | 648 |
| Applied | 4667 | 948 |

## Blank or "Not Reported" per column

Blank = empty after trimming; "Not Reported" = exact text, case-insensitive. The `N/A (...)` column counts other `N/A`-style placeholders for information only.

| column | blank_pct | not_reported_pct | blank_or_not_reported_pct | n_a_style_pct |
|---|---|---|---|---|
| Conference | 0.0 | 0.0 | 0.0 | 0.0 |
| Paper_ID | 0.0 | 0.0 | 0.0 | 0.0 |
| Original_Paper_ID | 0.0 | 0.0 | 0.0 | 0.0 |
| Category | 0.0 | 0.0 | 0.0 | 0.0 |
| Evaluation_Dataset | 0.0 | 0.0 | 0.0 | 0.0 |
| Environment | 0.0 | 10.4 | 10.4 | 0.0 |
| Target_Landscape | 0.0 | 0.0 | 0.0 | 0.0 |
| Winning_Strategy | 0.0 | 0.2 | 0.2 | 0.0 |
| Paper_Title | 0.0 | 0.9 | 0.9 | 0.0 |
| Authors | 0.0 | 1.1 | 1.1 | 0.0 |
| Year | 0.0 | 0.0 | 0.0 | 0.0 |
| Source_File | 0.0 | 0.0 | 0.0 | 0.0 |
| GECCO_Track | 0.0 | 70.0 | 70.0 | 0.0 |
| Industry | 0.0 | 0.0 | 0.0 | 0.0 |
| Problem_Context | 0.0 | 0.0 | 0.0 | 0.0 |
| Dataset_Name | 0.0 | 1.2 | 1.2 | 52.5 |
| Source_Platform | 0.0 | 22.5 | 22.5 | 55.0 |
| Benchmark_Name | 0.0 | 0.0 | 0.0 | 0.0 |
| Dimensionality | 0.0 | 18.7 | 18.7 | 0.0 |
| Modality | 0.0 | 50.7 | 50.7 | 0.0 |
| Separability | 0.0 | 65.6 | 65.6 | 0.0 |
| Landscape_Characteristics | 0.0 | 30.7 | 30.7 | 0.0 |
| Algorithm_Name | 0.0 | 0.2 | 0.2 | 0.0 |
| Population_Size | 0.0 | 0.0 | 0.0 | 0.0 |
| Max_Evaluations_or_Generations | 0.0 | 0.0 | 0.0 | 0.0 |
| Mutation_Rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Crossover_Rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Performance_Metric | 0.0 | 0.5 | 0.5 | 0.0 |
| Is_Optimal_Found | 0.0 | 74.9 | 74.9 | 0.0 |

## Benchmark_Name variety

- unique raw values: **3374**
- unique after lowercasing and removing non-alphanumerics: **3285** (empty after normalising: 0 rows)

## Paper identity (paper_index.csv)

1494 papers. Flags: `title_under_multiple_source_files` (the same normalised title in one Conference+Year appears under more than one Source_File), `source_file_has_multiple_titles` (one Source_File within a Conference+Year carries more than one title), `untitled` (title missing). Source_File scope is Conference+Year, because generic file names repeat across years.

Conference/Year combinations with at least one flag:

| Conference | Year | papers | flagged | title_under_multiple_files | file_with_multiple_titles | untitled |
|---|---|---|---|---|---|---|
| PReMI | 2010 | 5 | 0 | 0 | 0 | 1 |
| PReMI | 2011 | 6 | 0 | 0 | 0 | 1 |
| PReMI | 2014 | 13 | 0 | 0 | 0 | 1 |
| PReMI | 2015 | 9 | 0 | 0 | 0 | 3 |
| PReMI | 2016 | 21 | 0 | 0 | 0 | 3 |
| PReMI | 2017 | 49 | 0 | 0 | 0 | 5 |
| PReMI | 2020 | 8 | 0 | 0 | 0 | 2 |
| PReMI | 2021 | 19 | 0 | 0 | 0 | 4 |
| PReMI | 2023 | 124 | 59 | 0 | 59 | 17 |
| PReMI | 2024 | 7 | 0 | 0 | 0 | 1 |

Total flagged papers: **59** of 1494; untitled: 38.

PReMI 2023: 267 rows, 67 Source_Files, 107 distinct titles, 59 flagged papers.

## PPSN: one paper or a whole proceedings per file?

PPSN: 92 rows in 5 Source_Files.

### PPSN_2016-compressed.pdf (Year 2016)

- rows: 22; distinct titles: 1; distinct Original_Paper_ID roots: 1 (Paper_001)
- distinct Authors values: 1 (Youhei Akimoto; Nikolaus Hansen)
- sample titles:
  - Online Model Selection for Restricted Covariance Matrix Adaptation
- extra evidence: distinct Problem_Context 5, Benchmark_Name 17, Algorithm_Name 11; Problem_Context values: Evaluating mathematical landscapes; Cooperative predator-prey pursuit task; Submerged Wave Energy Converters placement; Evaluating permutation benchmark problems; Asymmetric Traveling Salesman Problem (ATSP)

### PPSN_2018.pdf (Year 2018)

- rows: 15; distinct titles: 1; distinct Original_Paper_ID roots: 1 (Paper_002)
- distinct Authors values: 1 (Konstantinos Varelas; Anne Auger; Dimo Brockhoff; Nikolaus Hansen; Ouassim Ait ElHara; Yann Semet; Rami Kassa…)
- sample titles:
  - A Comparative Study of Large-Scale Variants of CMA-ES
- extra evidence: distinct Problem_Context 7, Benchmark_Name 7, Algorithm_Name 12; Problem_Context values: Evaluating mathematical landscapes; Vehicle routing / Traveling Salesman Problem; Multidimensional Knapsack Problem; Predicting Plasma Protein Binding level (PPB) in drug discovery; Predicting Toxicity (LD50) in drug discovery

### PPSN_2020-compressed.pdf (Year 2020)

- rows: 14; distinct titles: 1; distinct Original_Paper_ID roots: 1 (Paper_003)
- distinct Authors values: 1 (Thomas Bäck; Mike Preuss; André Deutz; Hao Wang; Carola Doerr; Michael Emmerich; Heike Trautmann)
- sample titles:
  - Parallel Problem Solving from Nature – PPSN XVI
- extra evidence: distinct Problem_Context 4, Benchmark_Name 12, Algorithm_Name 7; Problem_Context values: Evaluating mathematical landscapes; 2D fluid dynamics optimization to minimize maximum air flow speed; Finding an alphabet ordering that minimizes the number of Lyndon fact…; Finding an alphabet ordering that balances the length of Lyndon facto…

### PPSN_2022-compressed.pdf (Year 2022)

- rows: 28; distinct titles: 1; distinct Original_Paper_ID roots: 1 (Paper_004)
- distinct Authors values: 1 (Amir Abbasnejad; Dirk V. Arnold)
- sample titles:
  - Adaptive Function Value Warping for Surrogate Model Assisted Evolutionary Optimization
- extra evidence: distinct Problem_Context 3, Benchmark_Name 8, Algorithm_Name 15; Problem_Context values: Evaluating mathematical landscapes; Evaluating reinforcement learning control tasks via neuroevolution; Neural Architecture Search

### PPSN_24.pdf (Year 2024)

- rows: 13; distinct titles: 1; distinct Original_Paper_ID roots: 1 (Paper_005)
- distinct Authors values: 1 (Michael Affenzeller; Stephan M. Winkler; Anna V. Kononova; Heike Trautmann; Tea Tušar; Penousal Machado; Thom…)
- sample titles:
  - Parallel Problem Solving from Nature – PPSN XVIII
- extra evidence: distinct Problem_Context 3, Benchmark_Name 7, Algorithm_Name 12; Problem_Context values: Evaluating mathematical landscapes; Prediction of concrete compressive strength; Solving Traveling Thief Problem (TTP)

## Report-only checks (nothing deleted)

### Winning_Strategy != Algorithm_Name

Rows: **0** (expected 0).

### Repeated title + Benchmark_Name + Algorithm_Name + Evaluation_Dataset

Exact (raw-value) repeats: **835** extra rows beyond the first, in 464 groups (1299 rows including the first of each group). Groups where every other column (except Paper_ID / Original_Paper_ID) is also identical: **0**.

How many groups differ in each column:

| column | groups_differing |
|---|---|
| Environment | 373 |
| Dimensionality | 365 |
| Max_Evaluations_or_Generations | 175 |
| Performance_Metric | 112 |
| Population_Size | 37 |
| Is_Optimal_Found | 8 |
| Landscape_Characteristics | 7 |
| Problem_Context | 4 |
| Crossover_Rate | 3 |
| Mutation_Rate | 2 |

10 sample groups (random, seed 0):

- **Multi-Objective Fairness Approach Using Causal Bayesian Networks & Grammatical …** | Benchmark `German Credit Classification with Fairn…` | Algorithm `Grammatical Evolution (GE)` | Dataset `German Credit dataset`; 2 rows; GECCO 2025; Paper_IDs P2025_GECCO_033_Ext_01, P2025_GECCO_033_Ext_02
  - differs in **Performance_Metric**: Test Equal Opportunity Difference (EOD) / Test Accuracy
- **Targeting Evaluation, Computation and Interaction Costs in Expensive Black-Box …** | Benchmark `DTLZ2` | Algorithm `WAPE` | Dataset `DTLZ2`; 10 rows; GECCO 2025; Paper_IDs P2025_GECCO_030_Ext_15, P2025_GECCO_030_Ext_21, P2025_GECCO_030_Ext_27, P2025_GECCO_030_Ext_33, P2025_GECCO_030_Ext_39, P2025_GECCO_030_Ext_63, P2025_GECCO_030_Ext_67, P2025_GECCO_030_Ext_71, P2025_GECCO_030_Ext_75, P2025_GECCO_030_Ext_79
  - differs in **Environment**: 3 input dimensions, 2 objectives / 150 MaxFEs / 4 input dimensions, 2 objectives / 150 MaxFEs / 5 input dimensions, 2 objectives / 150 MaxFEs / 7 input dimensions, 2 objectives / 150 MaxFEs / 5 input dimensions, 3 objectives / 150 MaxFEs
  - differs in **Dimensionality**: 3 input dimensions, 2 objectives / 4 input dimensions, 2 objectives / 5 input dimensions, 2 objectives / 7 input dimensions, 2 objectives / 5 input dimensions, 3 objectives
  - differs in **Performance_Metric**: Mean runtime (Inner Optimization Cost) / Mean Opportunity Cost (OC)
- **An Approximated Domination Relationship based on Binary Classifiers for Evoluti…** | Benchmark `ZZJ1` | Algorithm `RCPS-RM-MEDA` | Dataset `ZZJ1`; 2 rows; CEC 2021; Paper_IDs P2021_CEC_095_Ext_18, P2021_CEC_095_Ext_21
  - differs in **Environment**: 10D / 10,000 MaxFEs / 30D / 10,000 MaxFEs
  - differs in **Dimensionality**: 10D / 30D
- **Decision Space Coverage of Random Walks** | Benchmark `Continuous Decision Space (Hypercube)` | Algorithm `Dissipative chaotic progress random wal…` | Dataset `Continuous Decision Space (Hypercube)`; 5 rows; CEC 2020; Paper_IDs P2020_CEC_022_Ext_06, P2020_CEC_022_Ext_12, P2020_CEC_022_Ext_18, P2020_CEC_022_Ext_24, P2020_CEC_022_Ext_30
  - differs in **Environment**: 2D / 20,000 MaxFEs / 3D / 30,000 MaxFEs / 4D / 40,000 MaxFEs / 6D / 60,000 MaxFEs / 10D / 100,000 MaxFEs
  - differs in **Dimensionality**: 2D / 3D / 4D / 6D / 10D
  - differs in **Max_Evaluations_or_Generations**: 20000 / 30000 / 40000 / 60000 / 100000
- **Hyper-parameter Optimization of Classifiers, using an Artificial Immune Network…** | Benchmark `Hyper-parameter Optimization of Linear …` | Algorithm `Artificial Immune Network (opt-aiNet)` | Dataset `Eclipse PDE UI`; 2 rows; GECCO 2023; Paper_IDs P2023_GECCO_036_Ext_59, P2023_GECCO_036_Ext_60
  - differs in **Performance_Metric**: Accuracy / AUC
- **A Surrogate-Assisted Offspring Generation Method for Expensive Multi-objective …** | Benchmark `DTLZ2` | Algorithm `SAO-MOEA` | Dataset `DTLZ2`; 3 rows; CEC 2020; Paper_IDs P2020_CEC_009_Ext_55, P2020_CEC_009_Ext_56, P2020_CEC_009_Ext_57
  - differs in **Environment**: 10D / 300 MaxFEs / 20D / 300 MaxFEs / 30D / 300 MaxFEs
  - differs in **Dimensionality**: 10D / 20D / 30D
- **NL-SHADE-RSP Algorithm with Adaptive Archive and Selective Pressure for CEC 202…** | Benchmark `CEC 2021 Rotation (001)` | Algorithm `IMODE` | Dataset `CEC 2021 Rotation (001)`; 2 rows; CEC 2021; Paper_IDs P2021_CEC_144_Ext_14, P2021_CEC_144_Ext_46
  - differs in **Environment**: 10D / 200,000 MaxFEs / 20D / 1,000,000 MaxFEs
  - differs in **Dimensionality**: 10D / 20D
  - differs in **Max_Evaluations_or_Generations**: 200000 / 1000000
- **An Arithmetic Optimization Algorithm with Dynamic State Estimation for Deadline…** | Benchmark `CyberShake workflow scheduling` | Algorithm `AOA (Arithmetic Optimization Algorithm)` | Dataset `CyberShake workflow`; 3 rows; GECCO 2025; Paper_IDs P2025_GECCO_044_Ext_16, P2025_GECCO_044_Ext_17, P2025_GECCO_044_Ext_18
  - differs in **Environment**: 50 tasks / 100 MaxFEs / 100 tasks / 100 MaxFEs / 1000 tasks / 100 MaxFEs
  - differs in **Dimensionality**: 50 tasks / 100 tasks / 1000 tasks
- **NL-SHADE-RSP Algorithm with Adaptive Archive and Selective Pressure for CEC 202…** | Benchmark `CEC 2021 Shift, Rotation (011)` | Algorithm `AGSK` | Dataset `CEC 2021 Shift, Rotation (011)`; 2 rows; CEC 2021; Paper_IDs P2021_CEC_144_Ext_27, P2021_CEC_144_Ext_59
  - differs in **Environment**: 10D / 200,000 MaxFEs / 20D / 1,000,000 MaxFEs
  - differs in **Dimensionality**: 10D / 20D
  - differs in **Max_Evaluations_or_Generations**: 200000 / 1000000
- **NL-SHADE-RSP Algorithm with Adaptive Archive and Selective Pressure for CEC 202…** | Benchmark `CEC 2021 Bias (100)` | Algorithm `NL-SHADE-RSP` | Dataset `CEC 2021 Bias (100)`; 2 rows; CEC 2021; Paper_IDs P2021_CEC_144_Ext_05, P2021_CEC_144_Ext_37
  - differs in **Environment**: 10D / 200,000 MaxFEs / 20D / 1,000,000 MaxFEs
  - differs in **Dimensionality**: 10D / 20D
  - differs in **Population_Size**: 300 / 600
  - differs in **Max_Evaluations_or_Generations**: 200000 / 1000000

### Original_Paper_ID under more than one Conference or Year

- full Original_Paper_ID: **2011** of 5903 values occur under more than one Conference or Year (1560 across conferences).
- Original_Paper_ID root (without _Ext_NN): **246** of 388 values occur under more than one Conference or Year (245 across conferences).

  Top 15 roots by rows:

| Original_Paper_ID root | conferences | years | rows |
|---|---|---|---|
| Paper_081 | CEC,GECCO,PReMI | 2018,2020,2021,2023,2024,2025,2026 | 326 |
| Paper_063 | CEC,FOGA,GECCO,PReMI | 2019,2020,2021,2022,2023,2024,2025 | 278 |
| Paper_078 | CEC,GECCO,PReMI | 2020,2021,2022,2023,2024,2025,2026 | 234 |
| Paper_054 | CEC,FOGA,GECCO,PReMI | 2019,2020,2021,2022,2023,2024,2025,2026 | 220 |
| Paper_036 | CEC,FOGA,GECCO,PReMI | 2012,2019,2020,2021,2022,2023,2024,2025,2026 | 218 |
| Paper_096 | CEC,GECCO | 2020,2021,2024,2025,2026 | 208 |
| Paper_095 | CEC,GECCO,PReMI | 2020,2021,2023,2024,2025,2026 | 198 |
| Paper_013 | CEC,FOGA,GECCO,PReMI | 2015,2020,2021,2022,2023,2024,2025,2026 | 195 |
| Paper_035 | CEC,FOGA,GECCO,PReMI | 2019,2020,2021,2022,2023,2024,2025,2026 | 193 |
| Paper_015 | CEC,FOGA,GECCO,PReMI | 2015,2020,2021,2022,2023,2024,2026 | 177 |
| Paper_092 | CEC,GECCO,PReMI | 2015,2020,2021,2023,2024,2025,2026 | 171 |
| Paper_009 | CEC,FOGA,GECCO,PReMI | 2015,2020,2021,2022,2023,2024,2025,2026 | 167 |
| Paper_030 | CEC,FOGA,GECCO,PReMI | 2017,2020,2021,2022,2023,2024,2025,2026 | 161 |
| Paper_002 | CEC,FOGA,GECCO,PPSN | 2015,2018,2020,2021,2022,2023,2024,2025 | 160 |
| Paper_005 | CEC,FOGA,GECCO,PPSN | 2015,2021,2022,2023,2024,2025,2026 | 159 |

Original_Paper_ID is a per-file extraction counter that restarts per source, so it is not a paper identifier; Paper_ID is used instead.

## Gold labels

Skipped: gold_standard_labels.csv not found (searched the repo, backups and git history). No `gold_standard_labels_remapped.csv` written.

## Frozen copy

`papers_master_v2.csv`: byte-identical to `master_dataset_clean.csv` (verified).

