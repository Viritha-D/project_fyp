# Validation of independent query sets t1, t2 (no scoring)

Produced by `intake_validate_t.py`. Sources for gold checks: families_v5.json, entity_to_family_v5.csv, families_browse.csv (browse names equal families_v5 names for all families: checked). Excluded families: F02124 (Not Reported; Not Reported), F00334 (Evolutionary Algorithm; extraction_artifact_suspect). Nothing was corrected.

## Per-set validation

| set | rows | valid | invalid | invalid share | (a) id missing | (b) excluded | (c) name mismatch / count | distinct gold families (valid ids) | of which in queries_v2 gold | of which < 2 papers | words per query mean / median / min / max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| t1 | 20 | 20 | 0 | 0% | 0 | 0 | 0 | 39 | 1 | 25 | 24.0 / 24 / 15 / 41 |
| t2 | 20 | 0 | 20 | 100% | 0 | 0 | 20 | 43 | 2 | 39 | 29.1 / 30 / 22 / 35 |

Reference, queries_v2: words per query 22.5 / 22 / 10 / 35.

## Invalid rows (every failing id; correct nothing)

### t1: 0 invalid of 20

| query | id as written | name as written | stored name for that id | similarity | n_papers | ids whose stored name equals the written name (information only) |
|---|---|---|---|---|---|---|

### t2: 20 invalid of 20

| query | id as written | name as written | stored name for that id | similarity | n_papers | ids whose stored name equals the written name (information only) |
|---|---|---|---|---|---|---|
| t2:Q01 | f00312 | Plateau | Hyperparameter optimization of multi-layer perceptron | 0.2 | 1 | - |
| t2:Q01 | f00784 | Royal Road | gmp | 0.0 | 1 | - |
| t2:Q02 | f00142 | Rastrigin | Flexibility management of home appliances to support DSO requests (MINLP) | 0.122 | 1 | F00054 |
| t2:Q02 | f00821 | CEC 2013 Niching Benchmark Suite | array_search_n | 0.174 | 1 | - |
| t2:Q03 | f00488 | Needle-in-a-Haystack | Deceptive Leading Blocks | 0.318 | 2 | - |
| t2:Q03 | f00502 | Long Path Problem | k-FeedbackVertexSet in tournaments | 0.078 | 1 | - |
| t2:Q04 | f00045 | DTLZ2 | Rotated High Conditioned Elliptic Function (f2) | 0.115 | 1 | - |
| t2:Q04 | f00046 | DTLZ7 | Rotated Bent Cigar Function (f3) | 0.054 | 1 | - |
| t2:Q04 | f00052 | WFG2 | Energy Efficient Virtual Machine Consolidation | 0.04 | 1 | - |
| t2:Q05 | f00021 | Rotated High Conditioned Elliptic Function | Yoga | 0.087 | 1 | - |
| t2:Q05 | f00024 | Rotated Bent Cigar | musk | 0.0 | 2 | - |
| t2:Q05 | f00108 | Rosenbrock | shifted rotated {...} s function | 0.238 | 1 | F00053 |
| t2:Q06 | f00743 | Generalized Dynamic OneMax | Tecator | 0.182 | 1 | - |
| t2:Q06 | f00744 | Dynamic Bit Matching | Lethal Dose 50 | 0.118 | 1 | - |
| t2:Q07 | f00189 | Deceptive Leading Blocks | Vehicle aerodynamic lift optimization | 0.262 | 1 | F00488 |
| t2:Q07 | f00501 | Order-k Deceptive Functions | k-VertexCover | 0.25 | 1 | - |
| t2:Q08 | f01412 | Electric Bus Fleet Charging Scheduling | Hearing Loss Detection | 0.333 | 1 | - |
| t2:Q08 | f01485 | EV Charging Station Placement | mtsp | 0.121 | 1 | - |
| t2:Q09 | f00088 | Solomon VRPTW Benchmark | hybrid dielectric resonator antenna design | 0.246 | 1 | - |
| t2:Q09 | f00872 | Li & Lim PDPTW Instances | Michalewicz | 0.229 | 1 | - |
| t2:Q09 | f01104 | Capacitated Vehicle Routing Problem (CVRP) | Deterministic Flipping Challenge (DFC) | 0.375 | 1 | - |
| t2:Q10 | f01633 | Automatic Generation Control (AGC) Multi-Area Power System | Direction Finding Array Design | 0.295 | 1 | - |
| t2:Q10 | f01920 | Microgrid Frequency Regulation | Disease-Symptom Classification | 0.267 | 1 | - |
| t2:Q11 | f01874 | RAE2822 Transonic Airfoil Shape Optimization | Online Bin Packing (OBP) | 0.206 | 1 | - |
| t2:Q12 | f00032 | Bi-level optimization of bidding strategies in local energy markets (LEM) | ZDT | 0.079 | 20 | F00141 |
| t2:Q12 | f00033 | Flexibility management of home appliances to support DSO requests (MINLP) | DTLZ | 0.078 | 45 | F00142 |
| t2:Q13 | f00418 | Brandimarte Flexible Job Shop | MWSN Routing Optimization | 0.148 | 1 | - |
| t2:Q13 | f00931 | Hurink Flexible Job Shop with Setup Times | concave-bil | 0.115 | 1 | - |
| t2:Q14 | f00214 | 4-bar truss problem | Xin-She Yang function | 0.15 | 1 | - |
| t2:Q14 | f01642 | 10-bar Planar Truss Weight Minimization | MO-Hopper | 0.083 | 1 | - |
| t2:Q15 | f00371 | StarCraft RTS AI Behavior Tree Synthesis | Multi-microgrid scheduling optimization | 0.253 | 1 | - |
| t2:Q15 | f01890 | MicroRTS Skirmish AI | NIST BSSR1 Multimodal Biometrics Dataset | 0.133 | 1 | - |
| t2:Q16 | f00720 | DNA Sequence Design for Storage | 37-bit Multiplexer and 11-bit Even-parity | 0.167 | 1 | - |
| t2:Q16 | f01691 | GC-Content Constrained Code Generation | vertex coloring paths | 0.373 | 1 | - |
| t2:Q17 | f00814 | Reversible Circuit Synthesis (RevLib) | Planar Arm Inverse Kinematics | 0.364 | 1 | - |
| t2:Q17 | f01438 | Quantum Adder Circuit Minimization | Cervical Cancer Clustering | 0.333 | 1 | - |
| t2:Q18 | f00006 | Symbolic Regression for Rheology Data | Red Wine Quality Prediction | 0.219 | 1 | - |
| t2:Q18 | f01524 | Feynman Symbolic Regression Database | ICU Length of Stay Prediction | 0.246 | 1 | - |
| t2:Q19 | f00673 | Synthesizer Sound Matching Benchmark | ARCoating | 0.311 | 1 | - |
| t2:Q19 | f01955 | FM Acoustic Timbre Reconstruction | UMN dataset | 0.227 | 1 | - |
| t2:Q20 | f01180 | Auxetic Metamaterial Origami Pattern Design | 197_cpu_act (DM4) | 0.2 | 1 | - |
| t2:Q20 | f01944 | Miura-Ori Mechanical Tessellation | Paragraph Vector training | 0.379 | 1 | - |

## Query similarity (dense cosine, all-mpnet-base-v2, query text only)

Identical texts (normalised) within or across t1, t2, queries_v2: 0.

| set | against | queries with best cosine > 0.8 | >= 0.95 | max cosine |
|---|---|---|---|---|
| t1 | queries_v2 | 0 | 0 | 0.634 |
| t1 | t2 | 0 | 0 | 0.611 |
| t2 | queries_v2 | 0 | 0 | 0.633 |
| t2 | t1 | 0 | 0 | 0.611 |

Within-set best cosine (other query of the same set):
- t1: max 0.521; pairs > 0.8: 0
- t2: max 0.587; pairs > 0.8: 0

Flags (best cosine > 0.8):

- none

The 5 highest best-matches per set and comparison (top match shown):

**t1 vs queries_v2**

- t1:Q07 ↔ queries_v2:Q40, cosine 0.634: "food delivery platform, assigning orders to riders online as orders keep coming in, minimising delivery time. " ↔ "electric delivery vans that have to stop at charging stations, customers have time windows. benchmarks for tha"
- t1:Q04 ↔ queries_v2:Q06, cosine 0.526: "evolving boolean functions with good crypto properties (high nonlinearity, balanced) for stream ciphers, 8 inp" ↔ "evolving boolean programs / classifier systems on tasks where address bits select one data bit, or where the o"
- t1:Q08 ↔ queries_v2:Q39, cosine 0.488: "using a GA to break a substitution cipher, scoring candidate keys by letter frequencies. is there any benchmar" ↔ "need benchmarks for my GA asap, paper deadline is friday. what do people use??"
- t1:Q17 ↔ queries_v2:Q09, cosine 0.481: "studying whether crossover helps on functions where fitness only depends on how long the prefix of ones is. wa" ↔ "looking for functions with big flat plateaus where fitness only changes in steps, so small moves dont change a"
- t1:Q18 ↔ queries_v2:Q03, cosine 0.473: "traffic signal timing for a few intersections with an EA, minimise average waiting time from a simulator. what" ↔ "i have a fitness function from a simulator that takes ~2 min per eval. what should i even test on first"

**t1 vs t2**

- t1:Q13 ↔ t2:Q17, cosine 0.611: "evolving small digital circuits from xor / nand style gates with cartesian GP. which benchmark circuits are co" ↔ "Synthesizing quantum logic circuits using Cartesian Genetic Programming to implement Toffoli and reversible ar"
- t1:Q05 ↔ t2:Q15, cosine 0.610: "evolving decks and agents for a collectible card game arena, fitness is win rate against fixed bots. what do o" ↔ "Using genetic programming to evolve modular behavioral trees for non-player characters in a real-time strategy"
- t1:Q17 ↔ t2:Q07, cosine 0.575: "studying whether crossover helps on functions where fitness only depends on how long the prefix of ones is. wa" ↔ "Proving runtime bounds for genetic algorithms utilizing uniform vs two-point crossover on functions with stron"
- t1:Q09 ↔ t2:Q03, cosine 0.534: "evolving combinatorial test suites where every pair of parameter values has to appear at least once, smallest " ↔ "We are proving the approximation ratio of randomized local search versus a (1+1) evolutionary algorithm on pse"
- t1:Q06 ↔ t2:Q01, cosine 0.523: "analysing an EDA on linear functions with exponentially decreasing weights, like each bit is worth a power of " ↔ "I am mathematically analyzing the runtime of a (1+lambda) EA with self-adjusting mutation rates on strictly mo"

**t2 vs queries_v2**

- t2:Q14 ↔ queries_v2:Q10, cosine 0.633: "Applying genetic algorithms to structural topology optimization for additive manufacturing, trying to minimize" ↔ "structural optimisation with two objectives, min weight and min displacement for truss structures. which test "
- t2:Q02 ↔ queries_v2:Q25, cosine 0.528: "Investigating population diversity maintenance and stagnation prevention in multimodal optimization using nich" ↔ "made a new grey wolf style optimizer and my supervisor wants the usual classic test functions, the smooth bowl"
- t2:Q04 ↔ queries_v2:Q04, cosine 0.527: "Studying the performance of multi-objective evolutionary algorithms (NSGA-II vs MOEA/D) when scaling from 2 to" ↔ "my MOEA is for dynamic problems, the pareto front moves every 10 generations or so. need standard dynamic mult"
- t2:Q08 ↔ queries_v2:Q40, cosine 0.521: "We developed an adaptive memetic algorithm to optimize charging station allocation and charging schedules for " ↔ "electric delivery vans that have to stop at charging stations, customers have time windows. benchmarks for tha"
- t2:Q03 ↔ queries_v2:Q06, cosine 0.519: "We are proving the approximation ratio of randomized local search versus a (1+1) evolutionary algorithm on pse" ↔ "evolving boolean programs / classifier systems on tasks where address bits select one data bit, or where the o"

**t2 vs t1**

- t2:Q17 ↔ t1:Q13, cosine 0.611: "Synthesizing quantum logic circuits using Cartesian Genetic Programming to implement Toffoli and reversible ar" ↔ "evolving small digital circuits from xor / nand style gates with cartesian GP. which benchmark circuits are co"
- t2:Q15 ↔ t1:Q05, cosine 0.610: "Using genetic programming to evolve modular behavioral trees for non-player characters in a real-time strategy" ↔ "evolving decks and agents for a collectible card game arena, fitness is win rate against fixed bots. what do o"
- t2:Q07 ↔ t1:Q17, cosine 0.575: "Proving runtime bounds for genetic algorithms utilizing uniform vs two-point crossover on functions with stron" ↔ "studying whether crossover helps on functions where fitness only depends on how long the prefix of ones is. wa"
- t2:Q03 ↔ t1:Q09, cosine 0.534: "We are proving the approximation ratio of randomized local search versus a (1+1) evolutionary algorithm on pse" ↔ "evolving combinatorial test suites where every pair of parameter values has to appear at least once, smallest "
- t2:Q06 ↔ t1:Q09, cosine 0.525: "Conducting drift analysis on an estimation of distribution algorithm (compact GA) on dynamic fitness environme" ↔ "evolving combinatorial test suites where every pair of parameter values has to appear at least once, smallest "

