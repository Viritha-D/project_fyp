# Demo outputs: recommend_v21.py

Models frozen at tag `retrieval-v2.1-frozen`. Each block is the unedited standard output of the command shown (default k = 5).

## I built a new differential evolution variant for 30-dimensional single-objective problems with many local optima.

```
$ python retrieval_v2/recommend_v21.py "I built a new differential evolution variant for 30-dimensional single-objective problems with many local optima."
Query: I built a new differential evolution variant for 30-dimensional single-objective problems with many local optima.
Confidence tier: high (ranker score for the top family 0.235; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 4 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. BBOB (COCO)  [suite_series]  ranker score 0.235
   best-matching members: BBOB benchmark suite (24 single-objective, noiseless, continuous black-box problems) (E02401, similarity 0.46); Black Box Optimization Benchmarking (BBOB) suite (E02297, similarity 0.37); 55 bi-objective BBOB problems (E01731, similarity 0.36)
   match signals: cross-encoder -6.40, kNN vote 2.08
   evidence: 35 papers; venues {'CEC': 1, 'GECCO': 29, 'FOGA': 3, 'PPSN': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The BBOB (COCO) family groups 59 entities (Pure Math), used in 35 papers (176 records) at CEC (1), GECCO (29), FOGA (3) and PPSN (2), 2018-2026. Typical dimensions 5D (43); 2D, 5D, 10D (27); 10D (15), reported landscape: Multimodal, Non-separable, noiseless, single-objective, separable. Results are reported as Median target precision; Spearman rank correlation coefficient; Single run fixed-budget target precision; commonly compared algorithms: Differential Evolution (DE), BIPOP-CMA-ES, CMA-ES, CMA-ES-CSA, HCMA. Caveats: some records come from PPSN files whose paper titles are not per-paper.

2. rastrigin  [stem_group]  ranker score 0.119
   best-matching members: Rastrigin (E00132, similarity 0.26); Rastrigin (F6) (E01767, similarity 0.15); 6-D Rastrigin (E01537, similarity 0.14)
   match signals: cross-encoder -4.21, kNN vote 0.94
   evidence: 27 papers; venues {'CEC': 6, 'GECCO': 14, 'FOGA': 5, 'PPSN': 1, 'PReMI': 1}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The rastrigin family groups 4 entities (Pure Math), used in 27 papers (74 records) at CEC (6), GECCO (14), FOGA (5), PPSN (1) and PReMI (1), 2015-2026. Typical dimensions 20D, 40D, 80D (11); 2D (9); 6D (9), reported landscape: Multimodal, Separable, rugged, highly multimodal, local optima. Results are reported as Best fitness value achieved; AUC of QD-score, Global Performance, Global Reliability, Precision, Coverage; Average standard deviation of FEM_0.01; commonly compared algorithms: CMA-ES, (100/100_I, 200)-σSA-ES, (400/400_I, 800)-σSA-ES, (𝜇/𝜇_I, 𝜆)-𝜎SA-ES with Rescaled Mutations, AELM-DE. Caveats: some records come from PPSN files whose paper titles are not per-paper.

3. DTLZ  [suite_series]  ranker score 0.110
   best-matching members: DTLZ Suite (DTLZ1-DTLZ3) (E02088, similarity 0.47); DTLZ2 (10-Objective) (E01687, similarity 0.45); DTLZ2 (5-Objective) (E01686, similarity 0.45)
   match signals: cross-encoder -9.08, kNN vote 2.83
   evidence: 45 papers; venues {'CEC': 8, 'GECCO': 34, 'FOGA': 1, 'PPSN': 1, 'PReMI': 1}; signals ['n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The DTLZ family groups 35 entities (Pure Math), used in 45 papers (548 records) at CEC (8), GECCO (34), FOGA (1), PPSN (1) and PReMI (1), 2016-2026. Typical dimensions 10D (68); Variable (57); Variable (2-10 objectives) (40), reported landscape: Multimodal, Non-separable, degenerate Pareto front, Quadrant-shaped Pareto front, dominance resistant solutions. Results are reported as Inverted Generational Distance (IGD); Mean runtime (Inner Optimization Cost); Average ranking for SPD, IGD, IGD+; commonly compared algorithms: NSGA-II, NSGA-III, MOEA/D, AGE-MOEA, Interactive ParEGO. Caveats: some records come from PPSN files whose paper titles are not per-paper.

4. CEC 2017 suite  [suite_series]  ranker score 0.086
   best-matching members: CEC'17 benchmark optimization problems (E03125, similarity 0.43); CEC 2017 benchmark test suite (E00206, similarity 0.39); CEC'2017 benchmark suite (F1-F30) (E02279, similarity 0.20)
   match signals: cross-encoder -9.91, kNN vote 3.63
   evidence: 44 papers; venues {'CEC': 35, 'GECCO': 6, 'PPSN': 1, 'PReMI': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The CEC 2017 suite family groups 36 entities (Pure Math), used in 44 papers (357 records) at CEC (35), GECCO (6), PPSN (1) and PReMI (2), 2020-2025. Typical dimensions 30D (116); 50D (82); 100D (78), reported landscape: Multimodal, Non-separable, unimodal, hybrid, composition. Results are reported as Best fitness value achieved (mean and standard deviation); Best, worst, median, and average error values; standard deviations; ECDF curves; Area Under Curve (AUC); Average rank; commonly compared algorithms: DE, Differential Evolution (DE), CMA-ES, GA, GLPSO. Caveats: some records come from PPSN files whose paper titles are not per-paper.

5. CEC 2021 suite  [suite_series]  ranker score 0.070
   best-matching members: CEC 2021 Single-Objective Bound-Constrained Numerical Optimization (E00356, similarity 0.48); CEC 2021 Bias, Shift (110) (E00501, similarity 0.07); CEC 2021 Bias (100) (E00498, similarity 0.06)
   match signals: cross-encoder -6.11, kNN vote 1.02
   evidence: 13 papers; venues {'CEC': 13}; signals ['library_cue', 'n_papers>=2', 'standard_suite_name']
   note:     The CEC 2021 suite family groups 8 entities (Pure Math), used in 13 papers (110 records) at CEC (13), 2021-2024. Typical dimensions 20D (47); 10D (39); 10D, 20D (14), reported landscape: Multimodal, Non-separable, rotated, shifted, biased. Results are reported as Best fitness value achieved; Best, worst, median, and average error values; standard deviations; ECDF curves; Area Under Curve (AUC); Score (Score1 + Score2); commonly compared algorithms: APGSK-IMODE, DEDMNA, MadDE, NL-SHADE-RSP, SOMA-CLP. Rows cite CEC 2021 (6 papers).
```

## My multi-objective evolutionary algorithm handles 3 objectives with a concave Pareto front.

```
$ python retrieval_v2/recommend_v21.py "My multi-objective evolutionary algorithm handles 3 objectives with a concave Pareto front."
Query: My multi-objective evolutionary algorithm handles 3 objectives with a concave Pareto front.
Confidence tier: high (ranker score for the top family 0.624; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 4 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. DTLZ  [suite_series]  ranker score 0.624
   best-matching members: DTLZ2 (E00075, similarity 0.56); DTLZ Suite (DTLZ1-DTLZ3) (E02088, similarity 0.57); DTLZ3 (E00076, similarity 0.51)
   match signals: cross-encoder 1.66, kNN vote 8.28
   evidence: 45 papers; venues {'CEC': 8, 'GECCO': 34, 'FOGA': 1, 'PPSN': 1, 'PReMI': 1}; signals ['n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The DTLZ family groups 35 entities (Pure Math), used in 45 papers (548 records) at CEC (8), GECCO (34), FOGA (1), PPSN (1) and PReMI (1), 2016-2026. Typical dimensions 10D (68); Variable (57); Variable (2-10 objectives) (40), reported landscape: Multimodal, Non-separable, degenerate Pareto front, Quadrant-shaped Pareto front, dominance resistant solutions. Results are reported as Inverted Generational Distance (IGD); Mean runtime (Inner Optimization Cost); Average ranking for SPD, IGD, IGD+; commonly compared algorithms: NSGA-II, NSGA-III, MOEA/D, AGE-MOEA, Interactive ParEGO. Caveats: some records come from PPSN files whose paper titles are not per-paper.

2. ZDT  [suite_series]  ranker score 0.405
   best-matching members: ZDT2 (E00067, similarity 0.49); ZDT1 (E00066, similarity 0.49); ZDT4 (E00069, similarity 0.45)
   match signals: cross-encoder -0.61, kNN vote 3.20
   evidence: 20 papers; venues {'CEC': 6, 'GECCO': 12, 'PPSN': 1, 'PReMI': 1}; signals ['n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The ZDT family groups 11 entities (Pure Math), used in 20 papers (175 records) at CEC (6), GECCO (12), PPSN (1) and PReMI (1), 2016-2025. Typical dimensions 30D (77); 8D (21); 20D (15), reported landscape: Multimodal, Non-separable, monotonically transformed, conflicting objectives, complex. Results are reported as Inverted Generational Distance (IGD); Best fitness value achieved (GD, Spread, IGD, HV, RT); IGD, HV; commonly compared algorithms: NSGA-II, CPS-MOEA, MOEA/D-EGO, NSGA-III, Adaptable (BO) - Biased Samples. Caveats: some records come from PPSN files whose paper titles are not per-paper.

3. WFG  [suite_series]  ranker score 0.344
   best-matching members: WFG2 (E00220, similarity 0.41); WFG9 (E01194, similarity 0.47); WFG1 (E00219, similarity 0.45)
   match signals: cross-encoder -1.21, kNN vote 1.98
   evidence: 15 papers; venues {'CEC': 2, 'GECCO': 12, 'FOGA': 1}; signals ['n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The WFG family groups 14 entities (Pure Math), used in 15 papers (174 records) at CEC (2), GECCO (12) and FOGA (1), 2017-2026. Typical dimensions Variable (2-10 objectives) (32); Variable (2-6 objectives) (28); 9D (24), reported landscape: Multimodal, Non-separable, disconnected Pareto front, concave Pareto front, degenerate. Results are reported as Average ranking for SPD, IGD, IGD+; Mean IGD value; Mean Hypervolume (HV) and Mean Spread; commonly compared algorithms: NSGA-III, MOEA/D, ParEGO, AGE-MOEA, AGE-MOEA-II.

4. CEC 2017 suite  [suite_series]  ranker score 0.077
   best-matching members: CEC 2017 benchmark test suite (E00206, similarity 0.42); CEC'17 benchmark optimization problems (E03125, similarity 0.42); CEC2017 F13 (Hybrid Function 3) (E00448, similarity 0.26)
   match signals: cross-encoder -9.31, kNN vote 1.40
   evidence: 44 papers; venues {'CEC': 35, 'GECCO': 6, 'PPSN': 1, 'PReMI': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The CEC 2017 suite family groups 36 entities (Pure Math), used in 44 papers (357 records) at CEC (35), GECCO (6), PPSN (1) and PReMI (2), 2020-2025. Typical dimensions 30D (116); 50D (82); 100D (78), reported landscape: Multimodal, Non-separable, unimodal, hybrid, composition. Results are reported as Best fitness value achieved (mean and standard deviation); Best, worst, median, and average error values; standard deviations; ECDF curves; Area Under Curve (AUC); Average rank; commonly compared algorithms: DE, Differential Evolution (DE), CMA-ES, GA, GLPSO. Caveats: some records come from PPSN files whose paper titles are not per-paper.

5. hypervolume subset selection on {...} pareto fronts  [template_grid]  ranker score 0.069
   best-matching members: Hypervolume Subset Selection on Concave Pareto Fronts (E02384, similarity 0.53); Hypervolume Subset Selection on Convex Pareto Fronts (E02382, similarity 0.50); Hypervolume Subset Selection on Linear Pareto Fronts (E02383, similarity 0.47)
   match signals: cross-encoder -1.80, kNN vote 0.53
   evidence: 1 papers; venues {'GECCO': 1}; signals ['custom_data_only', 'single_paper']
   note:     The hypervolume subset selection on {...} pareto fronts family groups 3 entities (Pure Math), used in 1 paper (24 records) at GECCO (1), 2025. Typical dimensions 7D (12); 9D (12), reported landscape: convex Pareto front, linear Pareto front, concave Pareto front. Results are reported as CPU time [ms] for selecting a subset of points; commonly compared algorithms: gHSSInc/DecLazyQHV_adapt, gHSSInc/DecLazyQHV_best, gHSSInc/DecLazyQHV_std, gHSSInc/DecLazyQHV_upd. Caveats: it is supported by a single paper.
```

## I am testing a genetic algorithm for the traveling salesman problem on instances with a few hundred cities.

```
$ python retrieval_v2/recommend_v21.py "I am testing a genetic algorithm for the traveling salesman problem on instances with a few hundred cities."
Query: I am testing a genetic algorithm for the traveling salesman problem on instances with a few hundred cities.
Confidence tier: high (ranker score for the top family 0.269; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 4 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. traveling salesman  [stem_group]  ranker score 0.269
   best-matching members: Traveling Salesman Problem (TSP100) (E02876, similarity 0.51); Travelling Salesman Problem (TSP) (E02352, similarity 0.45); Travelling Salesman Problem (bays29) (E02853, similarity 0.45)
   match signals: cross-encoder -0.86, kNN vote 3.56
   evidence: 8 papers; venues {'CEC': 2, 'GECCO': 3, 'FOGA': 1, 'PPSN': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The traveling salesman family groups 5 entities (Pure Math), used in 8 papers (17 records) at CEC (2), GECCO (3), FOGA (1) and PPSN (2), 2016-2025. Typical dimensions Variable (8); 14 to 23 nodes (2); 10D, 15D, 20D, 25D (2), reported landscape: Multimodal, Non-separable, NP-hard, discrete, nonconvex. Results are reported as Percentage above Best Known solution cost (% BK average); Average/standard deviation/best fitness value; Optimality gap (%); commonly compared algorithms: EAX, Ensembles Collaborative (E. Colla), Ensembles Competitive (E. Comp), EoH, Genetic Programming (GP). Caveats: some records come from PPSN files whose paper titles are not per-paper.

2. ordered clustered traveling salesman  [stem_group]  ranker score 0.108
   best-matching members: Ordered Clustered Traveling Salesman Problem (OCTSP) - swiss42 instance (20,21 clusters) (E00112, similarity 0.47); Ordered Clustered Traveling Salesman Problem (OCTSP) - burma14 instance (E00090, similarity 0.47); Ordered Clustered Traveling Salesman Problem (OCTSP) - ulysses16 instance (E00091, similarity 0.47)
   match signals: cross-encoder 1.96, kNN vote 0.47
   evidence: 1 papers; venues {'CEC': 1}; signals ['library_cue', 'single_paper']
   note:     The ordered clustered traveling salesman family groups 27 entities (Applied), used in 1 paper (108 records) at CEC (1), 2020. Typical dimensions 42D (24); 29D (16); 48D (12), reported landscape: Multimodal, Non-separable. Results are reported as Best fitness value achieved (Best), Average fitness value achieved (Avg), Percentage Error (E%), Relative Error (RE%); commonly compared algorithms: Hybrid Genetic Algorithm (HGA), Improved Adaptive Genetic Simulated Annealing Algorithm (IAGSAA), Lexisearch Algorithm (LSA), Standard Genetic Algorithm (SGA). Caveats: it is supported by a single paper.

3. Traveling Salesman Problem  [single]  ranker score 0.086
   best-matching members: Traveling Salesman Problem (E00396, similarity 0.41)
   match signals: cross-encoder -1.87, kNN vote 2.53
   evidence: 5 papers; venues {'CEC': 1, 'GECCO': 2, 'FOGA': 1, 'PPSN': 1}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The Traveling Salesman Problem family groups 1 entity (Applied), used in 5 papers (14 records) at CEC (1), GECCO (2), FOGA (1) and PPSN (1), 2018-2024. Typical dimensions 280 to 2392 cities (6); Variable (4); 51 to 3795 cities (3), reported landscape: Multimodal, Non-separable, combinatorial, NP-hard, rugged. Results are reported as Average relative error (%); Tour length (Best, Worst, Mean); Relative Percentage Deviation (RPD), Best fitness value achieved, Convergence speed, Found optimal solution for 72% of instances; commonly compared algorithms: Adaptive Sequence-Based Selection Hyper-Heuristic (Adaptive-SSHH), BRKGA (tuned by iRace, with local search), BRKGA (tuned by iRace, without local search), BRKGA-QL (Biased Random-Key Genetic Algorithm with Q-Learning), Edge Assembly Crossover (EAX). Caveats: some records come from PPSN files whose paper titles are not per-paper.

4. TSPLIB  [suite_series]  ranker score 0.074
   best-matching members: Traveling Salesperson Problem (TSPlib) (E00889, similarity 0.34); TSPlib (eil51, eil76, eil101) (E01015, similarity 0.28); TSPLIB (E01629, similarity 0.24)
   match signals: cross-encoder -2.89, kNN vote 0.94
   evidence: 9 papers; venues {'GECCO': 8, 'FOGA': 1}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The TSPLIB family groups 21 entities (mixed: Applied 7, Pure Math 14), used in 9 papers (57 records) at GECCO (8) and FOGA (1), 2020-2026. Typical dimensions Variable (6); Variable (29 to 1000 customers) (6); Variable (51 to 442 vertices) (4), reported landscape: Multimodal, Non-separable, combinatorial, NP-hard, discrete. Results are reported as Recombination time and offspring cost; gtype (diversity score); Entropy (diversity) and best tour length; commonly compared algorithms: EAX, (mu + lambda)-EA with biased diversity mutation (BD), (mu + lambda)-EA with biased quality mutation (BQ), (mu + lambda)-EA with uniform edge mutation, 2-OPT. Rows cite TSPLIB (9 papers).

5. DTLZ  [suite_series]  ranker score 0.036
   best-matching members: DTLZ4 (E00077, similarity 0.23); DTLZ Suite (DTLZ1-DTLZ3) (E02088, similarity 0.22); DTLZ3 (E00076, similarity 0.20)
   match signals: cross-encoder -11.30, kNN vote 0.82
   evidence: 45 papers; venues {'CEC': 8, 'GECCO': 34, 'FOGA': 1, 'PPSN': 1, 'PReMI': 1}; signals ['n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The DTLZ family groups 35 entities (Pure Math), used in 45 papers (548 records) at CEC (8), GECCO (34), FOGA (1), PPSN (1) and PReMI (1), 2016-2026. Typical dimensions 10D (68); Variable (57); Variable (2-10 objectives) (40), reported landscape: Multimodal, Non-separable, degenerate Pareto front, Quadrant-shaped Pareto front, dominance resistant solutions. Results are reported as Inverted Generational Distance (IGD); Mean runtime (Inner Optimization Cost); Average ranking for SPD, IGD, IGD+; commonly compared algorithms: NSGA-II, NSGA-III, MOEA/D, AGE-MOEA, Interactive ParEGO. Caveats: some records come from PPSN files whose paper titles are not per-paper.
```

## I want to evaluate a feature selection method for high-dimensional gene expression data.

```
$ python retrieval_v2/recommend_v21.py "I want to evaluate a feature selection method for high-dimensional gene expression data."
Query: I want to evaluate a feature selection method for high-dimensional gene expression data.
Confidence tier: high (ranker score for the top family 0.201; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 4 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. Feature Selection  [single]  ranker score 0.201
   best-matching members: Feature Selection (E00522, similarity 0.64)
   match signals: cross-encoder 0.25, kNN vote 2.35
   evidence: 4 papers; venues {'CEC': 3, 'PReMI': 1}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The Feature Selection family groups 1 entity (Applied), used in 4 papers (12 records) at CEC (3) and PReMI (1), 2021-2024. Typical dimensions Variable (6); 10 features (5), reported landscape: high-dimensional search space, high-dimensional, interacting features. Results are reported as Average classification accuracy; Mean accuracy and execution time; Classification accuracy and computation time; commonly compared algorithms: CHC Genetic Algorithm, FIX (DE-FSPM with fixed sampling fraction), INC (DE-FSPM with incremental sampling fraction), Opposition-Based Jellyfish Search (OJS), SAGA (Surrogate-Assisted Genetic Algorithm). Rows cite UCI (2 papers).

2. eeg feature selection  [stem_group]  ranker score 0.160
   best-matching members: EEG Feature Selection (E01104, similarity 0.56); EEG Feature Selection (k-NN Classifier) (E01953, similarity 0.54); EEG Feature Selection (SVM Classifier) (E01952, similarity 0.54)
   match signals: cross-encoder 0.81, kNN vote 0.84
   evidence: 2 papers; venues {'GECCO': 2}; signals ['n_papers>=2']
   note:     The eeg feature selection family groups 3 entities (Applied), used in 2 papers (3 records) at GECCO (2), 2020-2023. Typical dimensions 19 channels (2); 42 channels (1), reported landscape: high-dimensional, multiobjective. Results are reported as Classification Accuracy and Feature Reduction; Average accuracy of 93.46%, sensitivity of 92.0%, specificity of 92.6%; Average accuracy of 91.66%, sensitivity of 89.4%, specificity of 93.5%; commonly compared algorithms: Hierarchical NSGA-II, NSGA-II.

3. High-dimensional feature selection  [single]  ranker score 0.124
   best-matching members: High-dimensional feature selection (E00669, similarity 0.68)
   match signals: cross-encoder 0.58, kNN vote 0.62
   evidence: 1 papers; venues {'CEC': 1}; signals ['single_paper']
   note:     The High-dimensional feature selection family groups 1 entity (Applied), used in 1 paper (7 records) at CEC (1), 2023. Typical dimensions Variable (7), reported landscape: high-dimensional, large search space. Results are reported as Average classification accuracy; Average classification accuracy and average number of selected features; commonly compared algorithms: BBPSO, BBPSO-ACJ-BDFF, BPSO, HFS-C-P, ISBPSO. Caveats: it is supported by a single paper.

4. Madelon Feature Selection  [single]  ranker score 0.034
   best-matching members: Madelon Feature Selection (E02068, similarity 0.60)
   match signals: cross-encoder -1.70, kNN vote 0.60
   evidence: 1 papers; venues {'GECCO': 1}; signals ['library_cue', 'single_paper']
   note:     The Madelon Feature Selection family groups 1 entity (Applied), used in 1 paper (4 records) at GECCO (1), 2024. Typical dimensions 500D (4). Results are reported as Mean accuracy of SVM on the test set: 88.99%; Mean accuracy of SVM on the test set: 70.19%; Mean accuracy of SVM on the test set: 85.32%; commonly compared algorithms: Deluge Genetic Algorithm (DGA), FSSR, Particle Swarm Optimization (PSO), Wrapper-filter ant colony optimization feature selection (WFACOFS). Caveats: it is supported by a single paper; most landscape and dimension fields are not reported.

5. Breast Cancer Feature Selection  [single]  ranker score 0.026
   best-matching members: Breast Cancer Feature Selection (E02066, similarity 0.59)
   match signals: cross-encoder -3.10, kNN vote 0.60
   evidence: 1 papers; venues {'GECCO': 1}; signals ['library_cue', 'single_paper']
   note:     The Breast Cancer Feature Selection family groups 1 entity (Applied), used in 1 paper (4 records) at GECCO (1), 2024. Typical dimensions 30D (4). Results are reported as Mean accuracy of SVM on the test set: 95.54%; Mean accuracy of SVM on the test set: 92.34%; Mean accuracy of SVM on the test set: 90.87%; commonly compared algorithms: Deluge Genetic Algorithm (DGA), FSSR, Particle Swarm Optimization (PSO), Wrapper-filter ant colony optimization feature selection (WFACOFS). Caveats: it is supported by a single paper; most landscape and dimension fields are not reported.
```

## My evolutionary algorithm tunes hyper-parameters of tree-based models for software defect prediction.

```
$ python retrieval_v2/recommend_v21.py "My evolutionary algorithm tunes hyper-parameters of tree-based models for software defect prediction."
Query: My evolutionary algorithm tunes hyper-parameters of tree-based models for software defect prediction.
Confidence tier: high (ranker score for the top family 0.138; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 4 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. hyper parameter optimization of {...} for software bug prediction on {...}  [template_grid]  ranker score 0.138
   best-matching members: Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse JDT Core (E01884, similarity 0.66); Hyper-parameter Optimization of SVM-RBF for Software Bug Prediction on Eclipse JDT Core (E01869, similarity 0.66); Hyper-parameter Optimization of SVM-RBF for Software Bug Prediction on Equinox (E01870, similarity 0.66)
   match signals: cross-encoder 0.06, kNN vote 0.66
   evidence: 1 papers; venues {'GECCO': 1}; signals ['single_paper']
   note:     The hyper parameter optimization of {...} for software bug prediction on {...} family groups 40 entities (Applied), used in 1 paper (80 records) at GECCO (1), 2023. Typical dimensions 2D (50); 1D (30). Results are reported as Accuracy; AUC; commonly compared algorithms: Artificial Immune Network (opt-aiNet). Caveats: it is supported by a single paper; most landscape and dimension fields are not reported.

2. sphere  [stem_group]  ranker score 0.017
   best-matching members: Sphere function (E00573, similarity 0.19); Sphere (F1) (E01559, similarity 0.12); Sphere function (fsphere) (E02846, similarity 0.10)
   match signals: cross-encoder -11.32, kNN vote 1.29
   evidence: 32 papers; venues {'CEC': 3, 'GECCO': 16, 'FOGA': 8, 'PPSN': 3, 'PReMI': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The sphere family groups 4 entities (Pure Math), used in 32 papers (88 records) at CEC (3), GECCO (16), FOGA (8), PPSN (3) and PReMI (2), 2015-2026. Typical dimensions Variable (13); 30D (11); 20D, 40D, 80D (8), reported landscape: Unimodal, Separable, smooth, convex, quadratic. Results are reported as Best fitness value achieved; SP1; Number of iterations to reach target threshold of 10^-14; commonly compared algorithms: CMA-ES, MAP-Elites, Particle Swarm Optimization (PSO), (1+1)-ES with 1/s success rule, (1+1)-ES with exponential resamplings. Caveats: some records come from PPSN files whose paper titles are not per-paper.

3. rastrigin  [stem_group]  ranker score 0.016
   best-matching members: Rastrigin (E00132, similarity 0.17); Rastrigin function (visualized as Mount Everest) (E00154, similarity 0.04); Rastrigin (F6) (E01767, similarity 0.04)
   match signals: cross-encoder -11.30, kNN vote 0.81
   evidence: 27 papers; venues {'CEC': 6, 'GECCO': 14, 'FOGA': 5, 'PPSN': 1, 'PReMI': 1}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The rastrigin family groups 4 entities (Pure Math), used in 27 papers (74 records) at CEC (6), GECCO (14), FOGA (5), PPSN (1) and PReMI (1), 2015-2026. Typical dimensions 20D, 40D, 80D (11); 2D (9); 6D (9), reported landscape: Multimodal, Separable, rugged, highly multimodal, local optima. Results are reported as Best fitness value achieved; AUC of QD-score, Global Performance, Global Reliability, Precision, Coverage; Average standard deviation of FEM_0.01; commonly compared algorithms: CMA-ES, (100/100_I, 200)-σSA-ES, (400/400_I, 800)-σSA-ES, (𝜇/𝜇_I, 𝜆)-𝜎SA-ES with Rescaled Mutations, AELM-DE. Caveats: some records come from PPSN files whose paper titles are not per-paper.

4. mnist  [stem_group]  ranker score 0.011
   best-matching members: mnist-2-6 (E01520, similarity 0.37); mnist-1-5 (E01519, similarity 0.36); MNIST (Class-incremental) (E02049, similarity 0.26)
   match signals: cross-encoder -10.53, kNN vote 1.11
   evidence: 6 papers; venues {'CEC': 1, 'GECCO': 5}; signals ['n_papers>=2', 'multiple_venues']
   note:     The mnist family groups 5 entities (Applied), used in 6 papers (16 records) at CEC (1) and GECCO (5), 2020-2024. Typical dimensions Variable (5); 784D (3); 28x28 grey-scale pixels (2), reported landscape: Multimodal, Non-separable, rugged, complex, mode collapse. Results are reported as Classification Accuracy; FID Score; Accuracy and Stability; commonly compared algorithms: COEGAN, COEGAN+NSGC, COEGAN+NSLC, EvoDSS, Lipi-SSL.

5. rosenbrock  [stem_group]  ranker score 0.010
   best-matching members: Rosenbrock (f8) (E01562, similarity 0.11); Rosenbrock function (frosen) (E02850, similarity 0.11); Rosenbrock (E00131, similarity 0.10)
   match signals: cross-encoder -11.12, kNN vote 0.81
   evidence: 21 papers; venues {'CEC': 5, 'GECCO': 12, 'FOGA': 2, 'PPSN': 2}; signals ['n_papers>=2', 'multiple_venues']
   note:     The rosenbrock family groups 6 entities (Pure Math), used in 21 papers (52 records) at CEC (5), GECCO (12), FOGA (2) and PPSN (2), 2015-2026. Typical dimensions 100D (7); 2D (5); 100D, 200D, 300D (5), reported landscape: Unimodal, Non-separable, valley, rotated, expensive. Results are reported as Total execution time and Best fitness value achieved; Best fitness value achieved; Mean fitness value achieved; commonly compared algorithms: (mu/mu_w, lambda)-MSR-CMA-ES with Adaptive Augmented Lagrangian, AELM-DE, ALBSO, BSO, BSO-AL. Caveats: some records come from PPSN files whose paper titles are not per-paper.
```

## I need benchmarks for a runtime analysis of a (1+1) EA on pseudo-Boolean functions.

```
$ python retrieval_v2/recommend_v21.py "I need benchmarks for a runtime analysis of a (1+1) EA on pseudo-Boolean functions."
Query: I need benchmarks for a runtime analysis of a (1+1) EA on pseudo-Boolean functions.
Confidence tier: LOW EVIDENCE (ranker score for the top family 0.060; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 10 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. CEC 2017 suite  [suite_series]  ranker score 0.060
   best-matching members: CEC'17 benchmark optimization problems (E03125, similarity 0.42); CEC'2017 benchmark function suit (E00538, similarity 0.41); CEC'2017 benchmark suite (F1-F30) (E02279, similarity 0.34)
   match signals: cross-encoder -6.92, kNN vote 4.78
   evidence: 44 papers; venues {'CEC': 35, 'GECCO': 6, 'PPSN': 1, 'PReMI': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The CEC 2017 suite family groups 36 entities (Pure Math), used in 44 papers (357 records) at CEC (35), GECCO (6), PPSN (1) and PReMI (2), 2020-2025. Typical dimensions 30D (116); 50D (82); 100D (78), reported landscape: Multimodal, Non-separable, unimodal, hybrid, composition. Results are reported as Best fitness value achieved (mean and standard deviation); Best, worst, median, and average error values; standard deviations; ECDF curves; Area Under Curve (AUC); Average rank; commonly compared algorithms: DE, Differential Evolution (DE), CMA-ES, GA, GLPSO. Caveats: some records come from PPSN files whose paper titles are not per-paper.

2. BBOB (COCO)  [suite_series]  ranker score 0.059
   best-matching members: Black Box Optimization Benchmarking (BBOB) suite (E02297, similarity 0.44); BBOB benchmark suite (24 single-objective, noiseless, continuous black-box problems) (E02401, similarity 0.36); COCO benchmark suite (with affine recombinations) (E02186, similarity 0.29)
   match signals: cross-encoder -6.67, kNN vote 3.49
   evidence: 35 papers; venues {'CEC': 1, 'GECCO': 29, 'FOGA': 3, 'PPSN': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The BBOB (COCO) family groups 59 entities (Pure Math), used in 35 papers (176 records) at CEC (1), GECCO (29), FOGA (3) and PPSN (2), 2018-2026. Typical dimensions 5D (43); 2D, 5D, 10D (27); 10D (15), reported landscape: Multimodal, Non-separable, noiseless, single-objective, separable. Results are reported as Median target precision; Spearman rank correlation coefficient; Single run fixed-budget target precision; commonly compared algorithms: Differential Evolution (DE), BIPOP-CMA-ES, CMA-ES, CMA-ES-CSA, HCMA. Caveats: some records come from PPSN files whose paper titles are not per-paper.

3. cryptographic boolean  [stem_group]  ranker score 0.046
   best-matching members: Cryptographic Boolean Functions (Fitness 1) (E02057, similarity 0.54); Cryptographic Boolean Functions (Fitness 2) (E02058, similarity 0.53)
   match signals: cross-encoder -5.56, kNN vote 0.54
   evidence: 1 papers; venues {'GECCO': 1}; signals ['single_paper']
   note:     The cryptographic boolean family groups 2 entities (Pure Math), used in 1 paper (8 records) at GECCO (1), 2024. Typical dimensions 4 to 16 inputs (8). Results are reported as Best fitness value achieved; commonly compared algorithms: Genetic Algorithm (Bitstring Encoding), Genetic Programming (Tree-Based Encoding), Memetic Genetic Algorithm (Bitstring Encoding with Local Search), Memetic Genetic Programming (Tree-Based Encoding with Local Search). Caveats: it is supported by a single paper; most landscape and dimension fields are not reported.

4. CEC 2014 suite  [suite_series]  ranker score 0.032
   best-matching members: CEC2014 benchmark functions (E00118, similarity 0.34); CEC'14 benchmark suite (E00703, similarity 0.22)
   match signals: cross-encoder -5.85, kNN vote 3.52
   evidence: 16 papers; venues {'CEC': 10, 'GECCO': 2, 'PReMI': 4}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The CEC 2014 suite family groups 2 entities (Pure Math), used in 16 papers (59 records) at CEC (10), GECCO (2) and PReMI (4), 2020-2025. Typical dimensions 50D (15); 10D (14); 30D (9), reported landscape: Multimodal, Non-separable, hybrid, composition, rotated. Results are reported as Best fitness value achieved (average over 35 runs); Mean Friedman rank; Best fitness value; commonly compared algorithms: CMA-ES, Differential Evolution (DE), ESWSA, LESWSA, AGWO-D. Rows cite CEC 2014 (4 papers).

5. CEC 2005 suite  [suite_series]  ranker score 0.030
   best-matching members: CEC2005 benchmark functions (E02893, similarity 0.51); CEC'05 (E00477, similarity 0.02)
   match signals: cross-encoder -5.04, kNN vote 1.68
   evidence: 5 papers; venues {'CEC': 2, 'PReMI': 3}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The CEC 2005 suite family groups 2 entities (Pure Math), used in 5 papers (9 records) at CEC (2) and PReMI (3), 2021. Typical dimensions 10D (2); 30D (1); 50D (1), reported landscape: Multimodal, diverse characteristics. Results are reported as mean error; graph-theoretic measures and EA dynamics; graph theoretic measures; commonly compared algorithms: DE/best/1/bin, DE/rand/1/bin, FFQ-HIDMS-PSO, GA-HIDMS-PSO. Rows cite CEC 2005 (1 paper).
```

## A neuroevolution method for continuous control tasks in simulation.

```
$ python retrieval_v2/recommend_v21.py "A neuroevolution method for continuous control tasks in simulation."
Query: A neuroevolution method for continuous control tasks in simulation.
Confidence tier: LOW EVIDENCE (ranker score for the top family 0.042; tier cut-offs 0.072 / 0.137)
What this tier means: in similar cases in our tests, about 1 in 10 times the top family was one that papers actually used. Treat the list as suggestions to check, not as an answer.

1. OpenAI Gym tasks  [single]  ranker score 0.042
   best-matching members: OpenAI Gym tasks (E01454, similarity 0.53)
   match signals: cross-encoder -4.19, kNN vote 0.53
   evidence: 1 papers; venues {'GECCO': 1}; signals ['library_cue', 'single_paper']
   note:     The OpenAI Gym tasks family groups 1 entity (Applied), used in 1 paper (1 records) at GECCO (1), 2021. Results are reported as Score (reward); commonly compared algorithms: Neurogenetic Programming (Instant Scrum). Caveats: it is supported by a single paper; most landscape and dimension fields are not reported. Rows cite OpenAI Gym (1 paper).

2. Walker2d  [single]  ranker score 0.035
   best-matching members: Walker2d (E01624, similarity 0.36)
   match signals: cross-encoder -3.89, kNN vote 1.43
   evidence: 3 papers; venues {'GECCO': 3}; signals ['library_cue', 'n_papers>=2']
   note:     The Walker2d family groups 1 entity (Applied), used in 3 papers (9 records) at GECCO (3), 2022-2026. Typical dimensions 5702 (5); 17D state, 6D action (3); 11590 (1), reported landscape: Multimodal, Non-separable, high-dimensional, rugged, complex dynamics. Results are reported as MOQD-score; Average score over 100 runs; QD-Score: ~1.5e6, Coverage: ~60%, Max Fitness: ~5000; commonly compared algorithms: PGA-ME, MOME, MOME-PGX, NSGA-II, PS-LM-MA-ES. Rows cite OpenAI Gym (1 paper).

3. sphere  [stem_group]  ranker score 0.026
   best-matching members: Sphere function (E00573, similarity 0.23); Sphere (F1) (E01559, similarity 0.11); 3D-sphere (3D-ball-Viablab-81ppa) (E01989, similarity 0.10)
   match signals: cross-encoder -10.41, kNN vote 2.02
   evidence: 32 papers; venues {'CEC': 3, 'GECCO': 16, 'FOGA': 8, 'PPSN': 3, 'PReMI': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues']
   note:     The sphere family groups 4 entities (Pure Math), used in 32 papers (88 records) at CEC (3), GECCO (16), FOGA (8), PPSN (3) and PReMI (2), 2015-2026. Typical dimensions Variable (13); 30D (11); 20D, 40D, 80D (8), reported landscape: Unimodal, Separable, smooth, convex, quadratic. Results are reported as Best fitness value achieved; SP1; Number of iterations to reach target threshold of 10^-14; commonly compared algorithms: CMA-ES, MAP-Elites, Particle Swarm Optimization (PSO), (1+1)-ES with 1/s success rule, (1+1)-ES with exponential resamplings. Caveats: some records come from PPSN files whose paper titles are not per-paper.

4. hopper v  [stem_group]  ranker score 0.026
   best-matching members: Hopper-v3 (E01994, similarity 0.35); Hopper-v2 (E01963, similarity 0.30)
   match signals: cross-encoder -6.44, kNN vote 0.82
   evidence: 3 papers; venues {'GECCO': 3}; signals ['n_papers>=2']
   note:     The hopper v family groups 2 entities (Pure Math), used in 3 papers (8 records) at GECCO (3), 2023. Typical dimensions 11D state space, 3D action space (4), reported landscape: Multimodal, Non-separable, continuous state space, continuous action space, bi-objective. Results are reported as Mean return (3810.11); Mean return (3441.77); Mean return (2993.39); commonly compared algorithms: DARC, MOPDERL, PDERL, PGMORL, PhEDARC.

5. BBOB (COCO)  [suite_series]  ranker score 0.023
   best-matching members: NN-imitated BBOB Suite (E00931, similarity 0.28); BBOB benchmark suite (24 single-objective, noiseless, continuous black-box problems) (E02401, similarity 0.28); BBOB F8 (Rosenbrock Original) (E02813, similarity 0.26)
   match signals: cross-encoder -11.19, kNN vote 0.92
   evidence: 35 papers; venues {'CEC': 1, 'GECCO': 29, 'FOGA': 3, 'PPSN': 2}; signals ['library_cue', 'n_papers>=2', 'multiple_venues', 'standard_suite_name']
   note:     The BBOB (COCO) family groups 59 entities (Pure Math), used in 35 papers (176 records) at CEC (1), GECCO (29), FOGA (3) and PPSN (2), 2018-2026. Typical dimensions 5D (43); 2D, 5D, 10D (27); 10D (15), reported landscape: Multimodal, Non-separable, noiseless, single-objective, separable. Results are reported as Median target precision; Spearman rank correlation coefficient; Single run fixed-budget target precision; commonly compared algorithms: Differential Evolution (DE), BIPOP-CMA-ES, CMA-ES, CMA-ES-CSA, HCMA. Caveats: some records come from PPSN files whose paper titles are not per-paper.
```

