# Demo audit (audit only; nothing fixed)

Date: 2026-11-14. Branch `claude/magical-pascal-uxsxvk` at 112cdb6.

- **App:** `app/streamlit_app.py`. The live product system is v2.3 = blend 0.5 (`retrieval_v2/recommend_v23.py`, sha256
  `48a52c29…a3fe`).
- **How it was driven.** Every result below was measured in this session:
  - the real Streamlit script, run with Streamlit's test runner (`streamlit.testing.v1.AppTest`);
  - in a **clean virtualenv** built from the app's install instructions: CPU torch 2.15.0, then
    `app/requirements-live.txt`.
- **Where.** A temporary Linux cloud container (4 cores), not the user's computer.
- **Selection numbers.** The demo's reliability panel shows numbers from RESULTS.md. Those for the blend on the
  independent test are selection numbers, because the blend was chosen after seeing the test.

## A. Live mode on five new descriptions

**The inputs are new.** None appears in the gallery or in any query set. Their highest dense cosine (all-mpnet-base-v2)
against all 141 texts in the gallery, queries_v2 and t1–t4 is 0.614 (M1 vs queries_v2:Q04), and there is no exact
match.

**Seconds.** "Seconds" is the time from clicking Recommend to the rendered answer, inside one app process:

- A1 came first, so its 6.99 s includes loading the models and index in that process.
- The later answers took 0.67–1.00 s.
- Process cold-start times are in part C.

**What each answer shows.** Every answer shows a confidence label: the evidence tier, labelled "experimental, not
validated on the independent test". Every card shows:

- the family name;
- its member benchmark names;
- a data-only note;
- one or two source papers (title, conference, year).

### A1 (applied): 6.99 s; confidence label: **low**, shown as "experimental, not validated on the independent test"

> We schedule maintenance crews for a regional electricity grid with a genetic algorithm, assigning technicians to outage repairs while minimising restoration time and overtime cost.

| # | family | benchmark names shown (members) | note | source (closest evidence papers) |
|---|---|---|---|---|
| 1 | Hyperparameter optimization of neural network | Hyperparameter optimization of neural network | 1 paper (3 records), 2021; Pure Math 0% / Applied 100%. / Problem context: Hyperparameter optimization for neural network binary classification / Dimensionality: 200 features / **single paper only** | Hyperparameter Optimization: Comparing Genetic Algorithm against Grid Search and Bayesian Optimization (CEC 2021) |
| 2 | Periodic vehicle routing problem with maintenance scheduling | Periodic vehicle routing problem with maintenance scheduling | 1 paper (2 records), 2021; Pure Math 0% / Applied 100%. / Problem context: Wastewater systems planned maintenance scheduling and vehicle routing / Landscape: multi-objective; constrained / **single paper only** | Wastewater systems planned maintenance scheduling using multi-objective optimisation (GECCO 2021) |
| 3 | Transmission Expansion Planning | Transmission Expansion Planning | 1 paper (1 records), 2023; Pure Math 0% / Applied 100%. / Problem context: Power system investment planning / **single paper only** | A New Generation Cost Analysis Method of High Renewable Penetration Power Grid (CEC 2023) |
| 4 | Microgrid environmental protection and economic dispatch model | Microgrid environmental protection and economic dispatch model | 1 paper (1 records), 2023; Pure Math 0% / Applied 100%. / Problem context: Microgrid optimal scheduling / **single paper only** | Optimal Scheduling of Microgrid Based on Multi-objective Particle Swarm Optimization Algorithm (CEC 2023) |
| 5 | Average of the Weekly Minimum Night Flow (AWM) prediction | Average of the Weekly Minimum Night Flow (AWM) prediction | 1 paper (1 records), 2023; Pure Math 0% / Applied 100%. / Problem context: Prediction of Leakage in Water Distribution Networks / Dimensionality: Variable / **single paper only** | Multi-Objective Multi-Gene Genetic Programming for the Prediction of Leakage in Water Distribution Networks (GECCO 2023) |

### A2 (applied): 1.0 s; confidence label: **low**, shown as "experimental, not validated on the independent test"

> Our evolutionary algorithm plans irrigation for farms with limited water, deciding the daily water allocation per field to maximise crop yield under uncertain rainfall.

| # | family | benchmark names shown (members) | note | source (closest evidence papers) |
|---|---|---|---|---|
| 1 | pressure vessel design | pressure vessel design | 2 papers (7 records), 2022–2024; Pure Math 0% / Applied 100%. / Problem context: pressure vessel design; Pressure Vessel Design | Elephant Swarm Water Search Algorithm (LESWSA) (PReMI 2022); Enhancing population diversity based dandelion Optimizer for solving global optimization problems (CEC 2024) |
| 2 | compression string design | compression string design | 1 paper (6 records), 2022; Pure Math 0% / Applied 100%. / Problem context: compression string design / **single paper only** | Elephant Swarm Water Search Algorithm (LESWSA) (PReMI 2022) |
| 3 | Flower target | Flower target | 1 paper (1 records), 2021; Pure Math 0% / Applied 100%. / Problem context: HIFU Treatment Planning / Dimensionality: 24D (6 sonications) / 80D (20 sonications) / **single paper only** | Distributed Evolutionary Design of HIFU Treatment Plans (GECCO 2021) |
| 4 | Average of the Weekly Minimum Night Flow (AWM) prediction | Average of the Weekly Minimum Night Flow (AWM) prediction | 1 paper (1 records), 2023; Pure Math 0% / Applied 100%. / Problem context: Prediction of Leakage in Water Distribution Networks / Dimensionality: Variable / **single paper only** | Multi-Objective Multi-Gene Genetic Programming for the Prediction of Leakage in Water Distribution Networks (GECCO 2023) |
| 5 | Water Distribution Network Optimization (SN200, SN300, SN400, SN500, MN200, MN300, MN400, MN500, Balerma) | Water Distribution Network Optimization (SN200, SN300, SN400, SN500, MN200, MN300, MN400, MN500, Balerma) | 1 paper (6 records), 2020; Pure Math 0% / Applied 100%. / Problem context: Water Distribution Network Optimization / Landscape: constrained; discrete space / Dimensionality: Variable (226 to 546 pipes) / Modality: Multimodal / **single paper only** | A Memetic Level-based Learning Swarm Optimizer for Large-scale Water Distribution Network Optimization (GECCO 2020) |

### M1 (multi-objective): 0.88 s; confidence label: **high**, shown as "experimental, not validated on the independent test"

> I am designing an evolutionary algorithm for problems with four conflicting objectives where the Pareto front is disconnected into isolated segments, and I need test problems with known fronts.

| # | family | benchmark names shown (members) | note | source (closest evidence papers) |
|---|---|---|---|---|
| 1 | ZDT | ZDT3; ZDT and DTLZ (Multimodal group: ZDT3, ZDT4, ZDT6, DTLZ1); ZDT1; ZDT2; ZDT4 | 20 papers (175 records), 2016–2025; Pure Math 100% / Applied 0%. / Problem context: Evaluating mathematical landscapes; Evaluating mathematical landscapes and multi-objective sorting / Landscape: monotonically transformed; conflicting objectives / Dimensionality: 30D; 8D / Modality: Multimodal; Unimodal / Separability: Non-separable | How to Make Multi-Objective Evolutionary Algorithms Invariant to Monotonically Increasing Transformation of Objective Functions (GECCO 2024); A Meta-Learning-Based Surrogate-Assisted Evolutionary Algorithm for Expensive Multi-Objective Optimization Problems (CEC 2024) |
| 2 | DTLZ | DTLZ7; DTLZ Suite (DTLZ1-DTLZ3); DTLZ1 with Constraints on f1 and f2; DTLZ1; DTLZ2 | 45 papers (548 records), 2016–2026; Pure Math 100% / Applied 0%. / Problem context: Evaluating mathematical landscapes; Evaluating mathematical landscapes and multi-objective sorting / Landscape: degenerate Pareto front; Quadrant-shaped Pareto front / Dimensionality: 10D; Variable / Modality: Multimodal; Unimodal / Separability: Non-separable; Separable | Many-Objective Evolutionary Optimization using Density Peaks Scoring Selection Strategy (GECCO 2024); Hypervolume Subset Selection for Triangular and Inverted Triangular Pareto Fronts of Three-Objective Problems (FOGA 2017) |
| 3 | hypervolume subset selection on {...} pareto fronts | Hypervolume Subset Selection on Linear Pareto Fronts; Hypervolume Subset Selection on Concave Pareto Fronts; Hypervolume Subset Selection on Convex Pareto Fronts | 1 paper (24 records), 2025; Pure Math 100% / Applied 0%. / Problem context: Hypervolume Subset Selection / Landscape: convex Pareto front; linear Pareto front / Dimensionality: 7D; 9D / **single paper only** | Lazy Hypervolume Subset Selection Algorithm with Contributions Update (GECCO 2025) |
| 4 | Newly Formulated Simple Test Problem | Newly Formulated Simple Test Problem | 1 paper (4 records), 2020; Pure Math 100% / Applied 0%. / Problem context: Evaluating mathematical landscapes / Landscape: no distance function; linear triangular Pareto front / Dimensionality: Variable / **single paper only** | Effects of Dominance Resistant Solutions on the Performance of Evolutionary Multi-Objective and Many-Objective Algorithms (GECCO 2020) |
| 5 | 19 dynamic multi-objective test problems | 19 dynamic multi-objective test problems | 1 paper (6 records), 2024; Pure Math 100% / Applied 0%. / Problem context: Evaluating mathematical landscapes / Landscape: dynamic; time-varying / **single paper only** | A Dynamic Preference-driven Evolutionary Algorithm for Solving Dynamic Multi-objective Problems (GECCO 2024) |

### C1 (constrained): 0.8 s; confidence label: **high**, shown as "experimental, not validated on the independent test"

> A differential evolution variant with a new constraint handling method for real-valued problems that have many equality and inequality constraints and a very small feasible region.

| # | family | benchmark names shown (members) | note | source (closest evidence papers) |
|---|---|---|---|---|
| 1 | Stackelberg duopoly | Stackelberg duopoly | 1 paper (1 records), 2022; Pure Math 0% / Applied 100%. / Problem context: Stackelberg duopoly problem / **single paper only** | A multitasking surrogate-assisted differential evolution method for solving bi-level optimization problems (CEC 2022) |
| 2 | DTLZ | DTLZ1 with a Constraint on f3; DTLZ1 with Constraints on f1 and f2; DTLZ3; DTLZ1; DTLZ2 | 45 papers (548 records), 2016–2026; Pure Math 100% / Applied 0%. / Problem context: Evaluating mathematical landscapes; Evaluating mathematical landscapes and multi-objective sorting / Landscape: degenerate Pareto front; Quadrant-shaped Pareto front / Dimensionality: 10D; Variable / Modality: Multimodal; Unimodal / Separability: Non-separable; Separable | Hypervolume Subset Selection for Triangular and Inverted Triangular Pareto Fronts of Three-Objective Problems (FOGA 2017); A Competitive Swarm Algorithm Based on Tri-Competitive Criterion for Constrained Multiobjective Optimization (GECCO 2024) |
| 3 | RWMOP (CEC 2021 real-world MOPs) | RWMOP10; RWMOP09; RWMOP24; RWMOP15; RWMOP16 | 1 paper (175 records), 2021; Pure Math 0% / Applied 100%. / Problem context: Process Synthesis Problem; Spring Design / Landscape: degenerate PF; non-linear solution space / Dimensionality: 3D; 4D / Modality: Multimodal / Separability: Non-separable / **single paper only** | A New Arithmetic Optimization Algorithm for Solving Real-World Multiobjective CEC-2021 Constrained Optimization Problems: Diversity Analysis and Validations (CEC 2021) |
| 4 | CEC 2011 suite | CEC'11 suite ELD problem; IEEE CEC 2011 Suite | 2 papers (2 records), 2021–2023; Pure Math 50% / Applied 50%. / Problem context: Evaluating mathematical landscapes; static economic load dispatch (ELD) problem / Landscape: high-dimensional; multimodal / Modality: Multimodal | Grammatical Evolution based Parameter Configuration of Ensemble Differential Evolution (PReMI 2021); Chaotic Mapping Genetic Algorithm with Multiple Strategies (CEC 2023) |
| 5 | MLNN Training | MLNN Training | 1 paper (6 records), 2021; Pure Math 0% / Applied 100%. / Problem context: Multi-layer neural network (MLNN) training / Dimensionality: 105; 43 / **single paper only** | Differential Evolution-based Neural Network Training Incorporating a Centroid-based Strategy and Dynamic Opposition-based Learning (CEC 2021) |

### O1 (out of scope): 0.67 s; confidence label: **low**, shown as "experimental, not validated on the independent test"

> Please give me a recipe for chocolate chip cookies that stay soft for several days and use brown butter and sea salt.

| # | family | benchmark names shown (members) | note | source (closest evidence papers) |
|---|---|---|---|---|
| 1 | Days Between | Days Between | 1 paper (1 records), 2020; Pure Math 100% / Applied 0%. / Problem context: Program Synthesis / **single paper only** | Code Building Genetic Programming (GECCO 2020) |
| 2 | Salt-and-Pepper Noise Removal | Salt-and-Pepper Noise Removal | 1 paper (1 records), 2020; Pure Math 0% / Applied 100%. / Problem context: Image Filtering / Noise Elimination (Salt-and-Pepper noise) / Landscape: rugged / Dimensionality: 2D (e.g., 200x200 pixels) / Modality: Multimodal / **single paper only** | Evolution of Cellular Automata with Conditionally Matching Rules for Image Filtering (CEC 2020) |
| 3 | dc dc buck converter design | DC-DC Buck Converter Design Problem; DC-DC buck converter design | 2 papers (6 records), 2019–2023; Pure Math 0% / Applied 100%. / Problem context: Optimal design of a DC-DC buck converter to minimize overall losses; Optimal design of DC-DC buck converter | A Soft Computing Approach for Optimal Design of a DC-DC Buck Converter (PReMI 2019); Fast Convergence to Near Optimal Solution for Job Shop Scheduling Using Cat Swarm Optimization (PReMI 2023) |
| 4 | Land Use Land Cover Classification | Land Use Land Cover Classification | 1 paper (1 records), 2021; Pure Math 0% / Applied 100%. / Problem context: Land Use Land Cover (LULC) Classification and Imbalance Handling / **single paper only** | Spatial-SMOTE (PReMI 2021) |
| 5 | vsr locomotion | VSR Locomotion (Heterogeneous representation); VSR Locomotion (Homogeneous representation) | 1 paper (10 records), 2021; Pure Math 0% / Applied 100%. / Problem context: Voxel-based Soft Robots (VSRs) morphology and controller co-optimization for locomotion / Dimensionality: 1150D; 70D / **single paper only** | Biodiversity in Evolved Voxel-based Soft Robots (GECCO 2021) |

Observations (descriptive):

- **O1 (out of scope, a cookie recipe):** the system still returns five families, with tier "low" and the Applied banner.
  There is no out-of-scope message.
- **C1 (constrained):** the top family is "Stackelberg duopoly" (1 paper), yet the tier is **high**. None of the
  constrained suites present in the data (CEC 2006 suite, DASCMOP, MW) is in the top 5.
- **A1 / A2 (applied):** 5 of 5 and 4 of 5 families have a single paper ("single paper only" caution shown); tier
  "low"; Applied banner shown.
- **M1 (multi-objective):** ZDT and DTLZ at ranks 1–2; tier "high".

## B. Pass / fail

| # | check | result | evidence |
|---|---|---|---|
| 1 | Empty or very short input gives a clear message | **PASS** | Empty: "Please describe your algorithm or problem." "TSP heuristic": "Please add a little more: the problem type (e.g. continuous, combinatorial, multi-objective), the representation (e.g. real vector, permutation, bit string, tree) or the objective." "123 !!! ### ???": "Please describe the problem in words." The same in both modes. |
| 2 | Each answer shows family name, benchmark names inside it, a note and a source | **PASS** | All 25 cards (5 answers × 5) render a heading, a "Members:" line, note lines and "Closest evidence papers:" (title, conference, year). Sources have no link or DOI. |
| 3 | The answer shows which version produced it and the hash | **FAIL** | The answer area shows neither. "v2.3" appears there only inside the tier sentence ("calibrated … not for v2.3"), and no hash appears. The version and sha256 appear only in the page footer ("Product system v2.3 (blend 0.5): retrieval_v2/recommend_v23.py sha256 …") and in the CSV / Markdown downloads (`system_hash`). |
| 4 | Nothing in the UI claims accuracy beyond the reliability-panel numbers | **PASS** | A scan of every rendered text in both modes found no claim of accuracy. Matches: "%" only in data shares (Pure Math / Applied); "validated" only as "not validated"; "guarantees" refers to the free tier's resources; "reliable" only in the panel title. |
| 5 | Tier badges say experimental | **PASS** | Every card caption: "Evidence tier for this list: … (experimental, not validated on the independent test)"; the tier line says the same. No hit@1 on the badges. |
| 6 | Cloud mode is labelled "precomputed examples" and does not pretend to be live | **PASS (wording differs)** | Precomputed mode shows "This hosted demo shows **precomputed** outputs of the frozen system (below). Live retrieval runs locally with run_demo.sh.", a "Gallery: precomputed outputs" heading, and footer "Mode: precomputed". Clicking Recommend gives "Live retrieval is not available in the hosted demo … see the precomputed examples below." and runs no retrieval. The exact phrase "precomputed examples" appears only in that warning, not as the label. |
| 7 | No file the app reads is a Git LFS pointer | **PASS on this branch; latent risk** | Every file opened (31 in live mode, 7 in precomputed mode, logged with a Python audit hook) begins with real content; none is an LFS pointer. This branch has no `.gitattributes`. **But `main` has `*.csv filter=lfs`.** Live mode reads `papers_master_with_matching_text_v2.csv`, `paper_to_entity_map_v2.csv`, `entity_to_family_v5.csv` and the query CSVs, so they could become LFS pointers if this branch is merged into or deployed from `main`. Precomputed mode reads no CSV. |

## C. Footprint (clean virtualenv, measured)

| quantity | measured |
|---|---|
| pip install size | site-packages **1,767 MB** (whole venv 1,790 MB; empty venv 13 MB). Largest: torch 809 MB, pyarrow 170 MB, transformers 120 MB, scipy 109 MB, pandas 81 MB, sympy 74 MB. 74 packages. Install took 52 s with a warm pip cache. **Correction:** the ~0.96 GB I reported earlier for the app venv was measured before the install finished; the app venv also measures 1,772 MB. |
| frozen pins | every pin in `FROZEN_ENV.txt` is present with the same version (the clean venv adds only Streamlit's own dependencies) |
| peak RAM at the first answer | **1,491 MB** with an empty model cache; **1,391 / 1,396 MB** with a warm cache (process `ru_maxrss`, one `live.recommend` call plus one more). This is above the 1.27 GB in app/README.md, which was measured without the app's note builder and test-query guard. |
| cold start to first answer | **15.5 s** with an empty model cache (includes a 507 MB model download); **9.1 s** and **6.6 s** with a warm cache (new process each time; disk cache not cleared). The next answer took 0.66–0.72 s. |
| model files (Hugging Face) | all-mpnet-base-v2 @ e8c3b32e…: model.safetensors **437.97 MB** + tokenizer 0.47 MB + vocab 0.23 MB; ms-marco-MiniLM-L-6-v2 @ 233902d2…: model.safetensors **90.87 MB** + tokenizer 0.71 MB + vocab 0.23 MB. The download was 507 MB on disk. |
| index and tables (repository files opened) | paper_embeddings.npy 34.84 MB; papers_master_with_matching_text_v2.csv 10.37 MB; entity_embeddings_v2.npy 9.83 MB; entity_notes_v2.json 5.65 MB; family_notes_v5.json 4.96 MB; problem_entities_enriched_v2.json 3.64 MB; paper_to_entity_map_v2.csv 3.23 MB; families_v5.json 1.60 MB; entity_to_family_v5.csv 0.41 MB; plus 18 small files (configs, code, query CSVs for the guard). Repository total: 27 files, **74.7 MB**. |
| total loaded data | about **604 MB** on disk: 529 MB of model weights plus about 75 MB of repository data |

The model weights are memory-mapped by safetensors, so they were measured from the downloaded cache rather than from
the open-file log.

## D. Gaps, most important first (none fixed in this step)

| # | gap | evidence | importance |
|---|---|---|---|
| 1 | Out-of-scope input is answered as if in scope | O1 (cookie recipe) returns 5 benchmark families; the only signal is tier "low" | high |
| 2 | The tier can read "high" on a poor list | C1: top family "Stackelberg duopoly" (1 paper), tier high; the tiers are unvalidated, but they are still shown prominently | high |
| 3 | `main` stores `*.csv` in Git LFS | live mode reads 3 data CSVs plus query CSVs; a merge into or deployment from `main` could serve LFS pointers | high (latent) |
| 4 | The answer itself does not show the version and hash (B3) | only the page footer and the downloads carry them | medium |
| 5 | The constrained query misses the constrained suites in the data | C1 top 5 has none of CEC 2006 suite, DASCMOP, MW | medium |
| 6 | Applied answers are mostly single-paper families | A1 5/5, A2 4/5 single-paper (caution shown) | medium |
| 7 | The live footprint exceeds the hosted floor | 1.77 GB install, 1.39–1.49 GB peak RAM, 529 MB model download, 6.6–15.5 s cold start; the hosted app is precomputed only | medium (known) |
| 8 | README numbers are out of date | app/README.md says peak RSS ≈ 1.27 GB; measured 1.39–1.49 GB | low |
| 9 | The label wording differs from "precomputed examples" (B6) | the label says "precomputed outputs" | low |
| 10 | Sources have no link or DOI | evidence papers show title, conference and year only | low |
| 11 | Tier text repeats on every card | the tier line plus 5 identical captions per answer | low |
