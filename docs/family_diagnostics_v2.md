# v2 entity fragmentation diagnostics

3199 entities, 11342 records. n_papers = distinct paper_key (paper_index.csv, after the approved merges).

## a. Entities by n_papers

| n_papers | entities | share of entities | records | share of records |
|---|---|---|---|---|
| 1 | 2946 | 92.1% | 8354 | 73.7% |
| 2 | 164 | 5.1% | 1064 | 9.4% |
| 3-5 | 59 | 1.8% | 556 | 4.9% |
| 6-10 | 15 | 0.5% | 429 | 3.8% |
| 11+ | 15 | 0.5% | 939 | 8.3% |

Records in entities with >= 2 papers: 2988 (26.3%).

## b. 40 random single-paper entities (seed 0)

| entity | canonical_name | Category | venue | aliases (up to 3) |
|---|---|---|---|---|
| E00112 | Ordered Clustered Traveling Salesman Problem (OCTSP) - swiss42 instance (20,21 clusters) | Applied | CEC | Ordered Clustered Traveling Salesman Problem (OCTSP) - swiss42 instance (20,21 clusters) |
| E01449 | CIFAR-10 with WRN-16-8 | Applied | GECCO | CIFAR-10 with WRN-16-8 |
| E00259 | CF1-CF10 | Pure Math | CEC | CF1-CF10 |
| E03078 | Lombard Effect Analysis | Applied | PReMI | Lombard Effect Analysis |
| E00941 | 3-bit Multiply | Pure Math | FOGA | 3-bit Multiply |
| E02150 | Colon Cancer Classification | Applied | GECCO | Colon Cancer Classification |
| E01714 | RA-MDS English Dataset | Applied | GECCO | RA-MDS English Dataset |
| E01976 | Sigmoid regression task (Amplitude Encoding) | Applied | GECCO | Sigmoid regression task (Amplitude Encoding) |
| E00621 | Speed Reducer Design Problem | Applied | CEC | Speed Reducer Design Problem |
| E00037 | MSTSP10 | Applied | CEC | MSTSP10 |
| E00595 | 500W Transformerless Photovoltaic Inverter Simulation | Applied | CEC | 500W Transformerless Photovoltaic Inverter Simulation |
| E02592 | Movable-Antenna-and-RIS-aided System Optimization (Task 2: Energy Efficiency Maximization) | Applied | GECCO | Movable-Antenna-and-RIS-aided System Optimization (Task 2: Energy Efficiency Maximization) |
| E01429 | Substitution Cipher | Pure Math | GECCO | Substitution Cipher |
| E03089 | Image Scene Classification | Applied | PReMI | Image Scene Classification |
| E00125 | Schwefel's Problem 2.21 (f6) | Pure Math | CEC | Schwefel's Problem 2.21 (f6) |
| E00029 | MSTSP2 | Applied | CEC | MSTSP2 |
| E01684 | Quantile Forecasting of S&P 500 Futures | Applied | GECCO | Quantile Forecasting of S&P 500 Futures |
| E00989 | ADS Path Planner Collision Avoidance (Two-Stage Approach) | Applied | GECCO | ADS Path Planner Collision Avoidance (Two-Stage Approach) |
| E01895 | Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Equinox | Applied | GECCO | Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Equinox |
| E02790 | f6 | Pure Math | GECCO | f6 |
| E01521 | sensorless | Applied | GECCO | sensorless |
| E00975 | Rebound library energy optimisation | Applied | GECCO | Rebound library energy optimisation |
| E00744 | VRPTW | Applied | CEC | VRPTW |
| E00998 | Ant-v2 | Applied | GECCO | Ant-v2 |
| E01925 | elevators | Applied | GECCO | elevators |
| E00644 | Shifted Rotated Rastrigin | Pure Math | CEC | Shifted Rotated Rastrigin |
| E02512 | Sunshade Design Optimization | Applied | GECCO | Sunshade Design Optimization |
| E02633 | Mass-Luminosity Relation Discovery | Applied | GECCO | Mass-Luminosity Relation Discovery |
| E02072 | Average Symbol Error Rate (SER) Minimization in RIS-assisted MIMO | Applied | GECCO | Average Symbol Error Rate (SER) Minimization in RIS-assisted MIMO |
| E01030 | Wind turbine design | Applied | GECCO | Wind turbine design |
| E01855 | ImageNet subset selection | Applied | GECCO | ImageNet subset selection |
| E03143 | Headline estimation in handwritten words | Applied | PReMI | Headline estimation in handwritten words |
| E01872 | Hyper-parameter Optimization of SVM-RBF for Software Bug Prediction on Mylyn | Applied | GECCO | Hyper-parameter Optimization of SVM-RBF for Software Bug Prediction on Mylyn |
| E00140 | Autonomous Vehicle Coordinated Driving on Simulated Roads | Applied | CEC | Autonomous Vehicle Coordinated Driving on Simulated Roads |
| E01480 | ali535 | Pure Math | GECCO | ali535 |
| E02763 | Unrelated Parallel Machines Scheduling Problem with Precedence and Resource Constraints (UPMSP-PR) | Applied | GECCO | Unrelated Parallel Machines Scheduling Problem with Precedence and Resource Constraints (UPMSP-PR) |
| E00866 | Depth Restricted (1,2)-Minimum Spanning Tree Problem (DR-(1,2)-MSTP) | Pure Math | FOGA | Depth Restricted (1,2)-Minimum Spanning Tree Problem (DR-(1,2)-MSTP) |
| E02068 | Madelon Feature Selection | Applied | GECCO | Madelon Feature Selection |
| E00413 | NILS Task 1 | Pure Math | CEC | NILS Task 1 |
| E00351 | RWMOP14 | Applied | CEC | RWMOP14 |

## c. Entities that look like instances or variants

| criterion | Applied | Pure Math | total |
|---|---|---|---|
| name ends in digits | 270 | 530 | 800 |
| contains "instance" | 40 | 11 | 51 |
| parameters in parentheses, e.g. (m=3) | 3 | 17 | 20 |
| starts with a library prefix + number (tai12, bayg29, bal8, ...) | 9 | 22 | 31 |
| **any of the above** | 307 | 557 | 864 (27.0%) |

Of the single-paper entities, 797 of 2946 match at least one criterion. Library-prefix list used: tai, bayg, bays, bal, nug, chr, esc, had, kra, lipa, rou, scr, sko, ste, tho, wil, bur, els, att, berlin, burma, ch, eil, fri, gr, kroa, krob, kroc, krod, kroe, lin, pr, rat, st, ulysses, pcb, rd, ts, tsp, gil, a, d, u.

## d. Dataset_Name / Source_Platform per entity

Entity-level: "present" if any member row has a real value; else "Custom Simulated Data" if any row says so; else "not reported" (Not Reported or N/A-style).

**Dataset_Name**

| Category | Custom Simulated Data | not reported | present |
|---|---|---|---|
| Applied | 150 | 234 | 1381 |
| Pure Math | 15 | 1183 | 236 |

**Source_Platform**

| Category | Custom Simulated Data | not reported | present |
|---|---|---|---|
| Applied | 3 | 1083 | 679 |
| Pure Math | 5 | 1307 | 122 |

## e. Audit candidates (entity_dedup_candidates_v2.csv)

2645 same-Category pairs with cosine >= 0.95; 358 near-synonym candidates (not numbered/named-instance variants, name word overlap >= 0.6), 33 isolated 1:1 pairs. Paper counts below are paper_key counts.

Combined paper counts across all 358 candidates: {2: 358}; distinct entities involved: 168. Every candidate pairs two single-paper entities, so the "40 largest" below are ties, ordered by similarity.

**40 largest by combined paper count**

| similarity | Category | entity A | papers | entity B | papers | overlap |
|---|---|---|---|---|---|---|
| 1.000 | Applied | E01902 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Mylyn | 1 | E01907 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Mylyn | 1 | 0.62 |
| 1.000 | Applied | E01903 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse PDE UI | 1 | E01908 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01901 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Lucene | 1 | E01906 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Lucene | 1 | 0.62 |
| 1.000 | Applied | E01900 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Equinox | 1 | E01905 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Equinox | 1 | 0.62 |
| 1.000 | Applied | E01899 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse JDT Core | 1 | E01904 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.67 |
| 1.000 | Applied | E01898 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse PDE UI | 1 | E01908 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.63 |
| 1.000 | Applied | E01898 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse PDE UI | 1 | E01903 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.63 |
| 1.000 | Applied | E01894 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse JDT Core | 1 | E01904 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.63 |
| 1.000 | Applied | E01894 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse JDT Core | 1 | E01899 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.63 |
| 1.000 | Applied | E01893 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse PDE UI | 1 | E01903 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01893 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse PDE UI | 1 | E01908 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01893 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse PDE UI | 1 | E01898 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.63 |
| 1.000 | Applied | E01892 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Mylyn | 1 | E01902 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Mylyn | 1 | 0.62 |
| 1.000 | Applied | E01892 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Mylyn | 1 | E01907 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Mylyn | 1 | 0.62 |
| 1.000 | Applied | E01891 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Lucene | 1 | E01901 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Lucene | 1 | 0.62 |
| 1.000 | Applied | E01891 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Lucene | 1 | E01906 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Lucene | 1 | 0.62 |
| 1.000 | Applied | E01890 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Equinox | 1 | E01905 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Equinox | 1 | 0.62 |
| 1.000 | Applied | E01890 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Equinox | 1 | E01900 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Equinox | 1 | 0.62 |
| 1.000 | Applied | E01889 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse JDT Core | 1 | E01904 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.67 |
| 1.000 | Applied | E01889 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse JDT Core | 1 | E01899 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.67 |
| 1.000 | Applied | E01888 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse PDE UI | 1 | E01908 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01889 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse JDT Core | 1 | E01894 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.63 |
| 1.000 | Applied | E01888 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse PDE UI | 1 | E01898 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.63 |
| 1.000 | Applied | E01888 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse PDE UI | 1 | E01903 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01888 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse PDE UI | 1 | E01893 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01887 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Mylyn | 1 | E01902 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Mylyn | 1 | 0.62 |
| 1.000 | Applied | E01887 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Mylyn | 1 | E01907 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Mylyn | 1 | 0.62 |
| 1.000 | Applied | E01887 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Mylyn | 1 | E01892 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Mylyn | 1 | 0.62 |
| 1.000 | Applied | E01886 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Lucene | 1 | E01901 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Lucene | 1 | 0.62 |
| 1.000 | Applied | E01886 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Lucene | 1 | E01906 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Lucene | 1 | 0.62 |
| 1.000 | Applied | E01886 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Lucene | 1 | E01891 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Lucene | 1 | 0.62 |
| 1.000 | Applied | E01885 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Equinox | 1 | E01905 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Equinox | 1 | 0.62 |
| 1.000 | Applied | E01885 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Equinox | 1 | E01900 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Equinox | 1 | 0.62 |
| 1.000 | Applied | E01885 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Equinox | 1 | E01890 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Equinox | 1 | 0.62 |
| 1.000 | Applied | E01884 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse JDT Core | 1 | E01904 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.67 |
| 1.000 | Applied | E01884 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse JDT Core | 1 | E01899 Hyper-parameter Optimization of Random Forest (RF) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.67 |
| 1.000 | Applied | E01884 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse JDT Core | 1 | E01889 Hyper-parameter Optimization of Decision Tree (CART) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.67 |
| 1.000 | Applied | E01884 Hyper-parameter Optimization of Naive Bayes (NB) for Software Bug Prediction on Eclipse JDT Core | 1 | E01894 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse JDT Core | 1 | 0.63 |
| 1.000 | Applied | E01883 Hyper-parameter Optimization of KNN (Minkowski Metric) for Software Bug Prediction on Eclipse PDE UI | 1 | E01908 Hyper-parameter Optimization of Adaptive Boosting (AdaBoost) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.67 |
| 1.000 | Applied | E01883 Hyper-parameter Optimization of KNN (Minkowski Metric) for Software Bug Prediction on Eclipse PDE UI | 1 | E01898 Hyper-parameter Optimization of Linear Discriminate Analysis (LDA) for Software Bug Prediction on Eclipse PDE UI | 1 | 0.63 |

**The isolated 1:1 pairs**

| similarity | Category | entity A | papers | entity B | papers | overlap |
|---|---|---|---|---|---|---|
| 1.000 | Applied | E00569 Traceability recovery between NVD and ExploitDB | 1 | E00570 Traceability recovery between NVD and Openwall | 1 | 0.71 |
| 1.000 | Applied | E00520 Power structure optimization model for carbon peak (Scenario 1: High imported power) | 1 | E00521 Power structure optimization model for carbon peak (Scenario 2: High nuclear capacity) | 1 | 0.64 |
| 1.000 | Applied | E00555 ECU Fingerprinting Classification (M1 - Step Response Features) | 1 | E00556 ECU Fingerprinting Classification (M2 - Step Response + Spectral Analysis Features) | 1 | 0.60 |
| 1.000 | Applied | E02930 Matrix Factorization (MMMF/PMF) with K-means clustering | 1 | E02931 Matrix Factorization (MMMF/PMF) with Spectral clustering | 1 | 0.67 |
| 0.993 | Applied | E01941 Emergency Medical Dispatch (EMD) on EGL Graph | 1 | E01942 Emergency Medical Dispatch (EMD) on EGL-G Graph | 1 | 0.88 |
| 0.992 | Applied | E00746 Restricted Container Relocation Problem | 1 | E00747 Unrestricted Container Relocation Problem | 1 | 0.60 |
| 0.991 | Pure Math | E00455 Hinton & Nowlan needle-in-a-haystack (fixed-length) | 1 | E00456 Hinton & Nowlan needle-in-a-haystack (variable-length) | 1 | 0.78 |
| 0.991 | Applied | E00007 Red Wine Quality Prediction | 1 | E00008 White Wine Quality Prediction | 1 | 0.60 |
| 0.982 | Applied | E01389 UAV-based ad-hoc wireless mesh network deployment (Two-hop) | 1 | E01390 UAV-based ad-hoc wireless mesh network deployment (One-hop) | 1 | 0.82 |
| 0.980 | Applied | E02590 Movable-Antenna-and-RIS-aided System Optimization (Task 0: Sum-Rate Maximization) | 1 | E02591 Movable-Antenna-and-RIS-aided System Optimization (Task 1: Min-Rate Maximization) | 1 | 0.71 |
| 0.975 | Applied | E00989 ADS Path Planner Collision Avoidance (Two-Stage Approach) | 1 | E00990 ADS Path Planner Collision Avoidance (Single-Stage Approach) | 1 | 0.78 |
| 0.973 | Applied | E01968 Single NAND gate design in granular metamaterial | 1 | E01969 Polycomputational NAND gate design in granular metamaterial | 1 | 0.75 |
| 0.972 | Pure Math | E02208 Symmetric Triangle Function (n=16, m=1, s=4) | 1 | E02209 Triangle Function (n=16, m=1, s=8) | 1 | 0.70 |
| 0.971 | Applied | E01033 NGAFID Engine Parameter Prediction | 1 | E01034 NGAFID Non-Engine Parameter Prediction | 1 | 0.80 |
| 0.970 | Applied | E01149 Perth wave scenario (49-buoy) | 1 | E01151 Sydney wave scenario (49-buoy) | 1 | 0.67 |
| 0.968 | Applied | E01945 Single-Sensor Robot Swarm Model | 1 | E01946 Two-Sensor Robot Swarm Model | 1 | 0.67 |
| 0.968 | Applied | E01150 Perth wave scenario (100-buoy) | 1 | E01152 Sydney wave scenario (100-buoy) | 1 | 0.67 |
| 0.968 | Applied | E00004 Energy Efficiency (Cooling Load) Prediction | 1 | E00005 Energy Efficiency (Heating Load) Prediction | 1 | 0.67 |
| 0.966 | Applied | E01966 Three-Beams | 1 | E01967 Three-Beams + Structure | 1 | 0.67 |
| 0.964 | Applied | E01964 Two-Beams | 1 | E01965 Two-Beams + Structure | 1 | 0.67 |
| 0.964 | Applied | E02471 Travelling Thief Problem (TTP) | 1 | E02875 Traveling Thief Problem (TTP) | 1 | 0.60 |
| 0.963 | Applied | E02955 Scene Multi-label Classification | 1 | E02956 Image Multi-label Classification | 1 | 0.60 |
| 0.963 | Applied | E01782 Three-option collective perceptual discrimination task | 1 | E01783 Two-option collective perceptual discrimination task | 1 | 0.71 |
| 0.962 | Applied | E02699 Exact-match text-to-image retrieval on MIMIC | 1 | E02701 Class-match text-to-image retrieval on MIMIC | 1 | 0.78 |
| 0.961 | Applied | E02353 Multi-Skill Resource-Constrained Project Scheduling Problem (MS-RCPSP) - iMOPSE d36 instances | 1 | E02354 Multi-Skill Resource-Constrained Project Scheduling Problem (MS-RCPSP) - Large-scale instances | 1 | 0.71 |
| 0.961 | Pure Math | E01861 NCA Morphogenesis (Square Target Shape) | 1 | E01862 NCA Morphogenesis (Up-scaled Square Target Shape) | 1 | 0.71 |
| 0.960 | Pure Math | E02327 Simplex Pareto Front (Archiving Task) | 1 | E02328 Inverted Simplex Pareto Front (Archiving Task) | 1 | 0.83 |
| 0.959 | Pure Math | E01223 Sharp Ridge (BBOB F13) | 1 | E02818 BBOB F13 (Sharp Ridge) | 1 | 1.00 |
| 0.958 | Applied | E00475 Vehicle aerodynamic drag optimization | 1 | E00476 Vehicle aerodynamic lift optimization | 1 | 0.60 |
| 0.956 | Pure Math | E00839 DTLZ1 with a Constraint on f3 | 1 | E00840 Inverted DTLZ1 with a Constraint on f3 | 1 | 0.86 |
| 0.955 | Pure Math | E02743 CPLEX-CORLAT-REG | 1 | E02745 CPLEX-CORLAT-REG-RCW | 1 | 0.75 |
| 0.952 | Applied | E02698 Exact-match text-to-image retrieval on ENTRep | 1 | E02700 Class-match text-to-image retrieval on ENTRep | 1 | 0.78 |
| 0.952 | Pure Math | E02210 2-range Asymmetric Triangle Function (n=16, m=(2,1), s=(2,4)) | 1 | E02212 2-range Asymmetric Incomplete Triangle Function (n=14, m=(2,1), s=(2,4)) | 1 | 0.77 |

