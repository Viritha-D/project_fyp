# Validation of query sets t3 and t4 (no scoring)

Produced by `intake_validate_t34.py` under amendment 3. No retrieval, ranking or scoring was run. Gold checks use families_v5.json only (names resolved with resolve_gold_names.py for t3). Nothing was repaired.

## Per-set validation

| set | form | rows | valid | invalid | invalid share | status (25% rule) | distinct gold families (valid) | of which < 2 papers | also in queries_v2 gold | also in t1 gold | words per query mean / median / min / max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| t3 | names-only | 20 | 20 | 0 | 0% | **accepted** | 43 | 30 | 5 | 9 | 35.8 / 36 / 29 / 41 |
| t4 | ids + names | 20 | 20 | 0 | 0% | **accepted** | 42 | 29 | 12 | 5 | 29.1 / 30 / 21 / 36 |

"distinct gold families (valid)" counts the families of names or ids that pass their own checks (matched names for t3, existing ids with a matching name for t4), whether or not the whole query is valid.

## t3: resolution of every written name

| query | name as written | result | family (id) | n_papers | candidates |
|---|---|---|---|---|---|
| Q01 | OneMax | match | OneMax (F00445) | 32 |  |
| Q01 | LeadingOnes | match | LeadingOnes (F00455) | 18 |  |
| Q02 | Multimodal Optimization Problems | match | Multimodal Optimization Problems (F00145) | 1 |  |
| Q02 | Dynamic Multimodal Optimization Problems (DMMOPs) | match | Dynamic Multimodal Optimization Problems (DMMOPs) (F00152) | 1 |  |
| Q03 | DeJong F4 (Quartic Function with Noise) | match | DeJong F4 (Quartic Function with Noise) (F00797) | 1 |  |
| Q03 | Noisy Rastrigin with LED | match | Noisy Rastrigin with LED (F01571) | 1 |  |
| Q03 | YANOISYBBOB | match | YANOISYBBOB (F00672) | 1 |  |
| Q04 | CEC 2010 suite | match | CEC 2010 suite (F00608) | 2 |  |
| Q04 | BBOB (COCO) | match | BBOB (COCO) (F00434) | 35 |  |
| Q05 | NK landscape | match | NK landscape (F00299) | 14 |  |
| Q05 | Best-of-Traps (BoT) | match | Best-of-Traps (BoT) (F01070) | 1 |  |
| Q05 | Trap | match | Trap (F00500) | 4 |  |
| Q06 | BBOB (COCO) | match | BBOB (COCO) (F00434) | 35 |  |
| Q06 | CEC 2017 suite | match | CEC 2017 suite (F00090) | 44 |  |
| Q07 | CEC 2013 suite | match | CEC 2013 suite (F00135) | 22 |  |
| Q07 | CEC 2014 suite | match | CEC 2014 suite (F00042) | 16 |  |
| Q08 | Traffic Signal Timing Optimization (TSTO) | match | Traffic Signal Timing Optimization (TSTO) (F01309) | 1 |  |
| Q08 | Traffic Light Scheduling Problem (TLSP) | match | Traffic Light Scheduling Problem (TLSP) (F00861) | 1 |  |
| Q09 | Cloud Task Scheduling | match | Cloud Task Scheduling (F00426) | 1 |  |
| Q10 | Traveling Salesman Problem with Drone Launch Station Location (TSP-DLSL) | match | Traveling Salesman Problem with Drone Launch Station Location (TSP-DLSL) (F01650) | 1 |  |
| Q10 | Drone scheduling for ship emission monitoring | match | Drone scheduling for ship emission monitoring (F00173) | 1 |  |
| Q10 | uav path planning | match | uav path planning (F00096) | 3 |  |
| Q11 | Water Distribution Network Optimization (SN200, SN300, SN400, SN500, MN200, MN300, MN400, MN500, Balerma) | match | Water Distribution Network Optimization (SN200, SN300, SN400, SN500, MN200, MN300, MN400, MN500, Balerma) (F00636) | 1 |  |
| Q11 | Modena Water Distribution Network | match | Modena Water Distribution Network (F00637) | 1 |  |
| Q12 | Wireless Sensor Network Energy Optimization | match | Wireless Sensor Network Energy Optimization (F02130) | 1 |  |
| Q12 | WSN deployment problem | match | WSN deployment problem (F00305) | 1 |  |
| Q12 | MWSN Routing Optimization | match | MWSN Routing Optimization (F00418) | 1 |  |
| Q13 | curriculum based course timetabling | match | curriculum based course timetabling (F00102) | 2 |  |
| Q13 | Conference Scheduling Problem (CoSP) | match | Conference Scheduling Problem (CoSP) (F01527) | 1 |  |
| Q14 | Organic solar cell thin-film fabrication optimization | match | Organic solar cell thin-film fabrication optimization (F00210) | 1 |  |
| Q14 | Photovoltaic potential estimation in Bangu neighborhood | match | Photovoltaic potential estimation in Bangu neighborhood (F00211) | 1 |  |
| Q15 | Music mood estimation via Twin Gaussian Processes | match | Music mood estimation via Twin Gaussian Processes (F01941) | 1 |  |
| Q16 | nca morphogenesis | match | nca morphogenesis (F01221) | 1 |  |
| Q16 | Car structure design problem | match | Car structure design problem (F00605) | 1 |  |
| Q17 | voxel based soft robot locomotion | match | voxel based soft robot locomotion (F00679) | 2 |  |
| Q17 | Brittle star robot locomotion | match | Brittle star robot locomotion (F01765) | 1 |  |
| Q17 | Six-Legged Locomotion | match | Six-Legged Locomotion (F00685) | 1 |  |
| Q18 | Texture | match | Texture (F00708) | 1 |  |
| Q18 | Texture Image Segmentation | match | Texture Image Segmentation (F01887) | 1 |  |
| Q19 | Board Game Design | match | Board Game Design (F01247) | 1 |  |
| Q19 | GVGAI games | match | GVGAI games (F00028) | 1 |  |
| Q19 | Game Content Generation Problems | match | Game Content Generation Problems (F00147) | 1 |  |
| Q20 | 3D Single Container Loading Problem (SCLP) | match | 3D Single Container Loading Problem (SCLP) (F01777) | 1 |  |
| Q20 | pressure vessel design | match | pressure vessel design (F00427) | 2 |  |

(For "no match", the candidates are the closest names by string similarity, information only, never used. For "ambiguous", they are every family with that exact name.)

## t4: rule (a)-(c) for every gold id

| query | id as written | name as written | stored name for that id | result | n_papers | ids whose stored name equals the written name (information only) |
|---|---|---|---|---|---|---|
| Q01 | F00329 | CEC 2011 suite | CEC 2011 suite | name matches id | 2 | F00329 |
| Q01 | F00136 | RWMOP (CEC 2021 real-world MOPs) | RWMOP (CEC 2021 real-world MOPs) | name matches id | 1 | F00136 |
| Q01 | F01055 | Tanabe and Ishibuchi Real-World Suite | Tanabe and Ishibuchi Real-World Suite | name matches id | 1 | F01055 |
| Q02 | F01396 | MW | MW | name matches id | 2 | F01396 |
| Q02 | F00293 | DASCMOP | DASCMOP | name matches id | 5 | F00293 |
| Q02 | F00112 | CF1-CF10 | CF1-CF10 | name matches id | 1 | F00112 |
| Q03 | F00036 | CEC 2006 suite | CEC 2006 suite | name matches id | 3 | F00036 |
| Q03 | F00054 | rastrigin | rastrigin | name matches id | 27 | F00054 |
| Q03 | F00499 | TSPLIB | TSPLIB | name matches id | 9 | F00499 |
| Q04 | F00329 | CEC 2011 suite | CEC 2011 suite | name matches id | 2 | F00329 |
| Q04 | F00043 | CEC 2020 suite | CEC 2020 suite | name matches id | 5 | F00043 |
| Q04 | F00427 | pressure vessel design | pressure vessel design | name matches id | 2 | F00427 |
| Q05 | F00434 | BBOB (COCO) | BBOB (COCO) | name matches id | 35 | F00434 |
| Q05 | F00090 | CEC 2017 suite | CEC 2017 suite | name matches id | 44 | F00090 |
| Q06 | F00672 | YANOISYBBOB | YANOISYBBOB | name matches id | 1 | F00672 |
| Q06 | F00293 | DASCMOP | DASCMOP | name matches id | 5 | F00293 |
| Q06 | F00151 | Optimal Power Flow (OPF) Problems under double-sided uncertainties | Optimal Power Flow (OPF) Problems under double-sided uncertainties | name matches id | 1 | F00151 |
| Q07 | F00329 | CEC 2011 suite | CEC 2011 suite | name matches id | 2 | F00329 |
| Q07 | F00136 | RWMOP (CEC 2021 real-world MOPs) | RWMOP (CEC 2021 real-world MOPs) | name matches id | 1 | F00136 |
| Q07 | F00043 | CEC 2020 suite | CEC 2020 suite | name matches id | 5 | F00043 |
| Q08 | F00425 | 3COL (Graph Coloring Problem) | 3COL (Graph Coloring Problem) | name matches id | 1 | F00425 |
| Q08 | F00550 | bin packing | bin packing | name matches id | 1 | F00550 |
| Q09 | F01777 | 3D Single Container Loading Problem (SCLP) | 3D Single Container Loading Problem (SCLP) | name matches id | 1 | F01777 |
| Q09 | F00550 | bin packing | bin packing | name matches id | 1 | F00550 |
| Q10 | F01309 | Traffic Signal Timing Optimization (TSTO) | Traffic Signal Timing Optimization (TSTO) | name matches id | 1 | F01309 |
| Q10 | F00861 | Traffic Light Scheduling Problem (TLSP) | Traffic Light Scheduling Problem (TLSP) | name matches id | 1 | F00861 |
| Q10 | F00327 | Network Signal Setting Design (NSSD) for two interacting junctions | Network Signal Setting Design (NSSD) for two interacting junctions | name matches id | 1 | F00327 |
| Q11 | F01661 | Demand-Balanced Railway Route Design | Demand-Balanced Railway Route Design | name matches id | 1 | F01661 |
| Q12 | F00185 | Day-ahead energy resource scheduling | Day-ahead energy resource scheduling | name matches id | 1 | F00185 |
| Q12 | F00370 | Microgrid environmental protection and economic dispatch model | Microgrid environmental protection and economic dispatch model | name matches id | 1 | F00370 |
| Q12 | F00151 | Optimal Power Flow (OPF) Problems under double-sided uncertainties | Optimal Power Flow (OPF) Problems under double-sided uncertainties | name matches id | 1 | F00151 |
| Q13 | F01053 | Capacitated Vehicle Routing Problem | Capacitated Vehicle Routing Problem | name matches id | 2 | F01053 |
| Q13 | F00034 | Vehicle Routing Problem with Cross-Docking (VRPCD) | Vehicle Routing Problem with Cross-Docking (VRPCD) | name matches id | 1 | F00034 |
| Q14 | F01245 | Wind Farm Layout and Cable Connection Layout Optimization | Wind Farm Layout and Cable Connection Layout Optimization | name matches id | 1 | F01245 |
| Q14 | F00371 | Multi-microgrid scheduling optimization | Multi-microgrid scheduling optimization | name matches id | 1 | F00371 |
| Q14 | F00373 | Energy consumption prediction and scheduling | Energy consumption prediction and scheduling | name matches id | 1 | F00373 |
| Q15 | F01935 | Handwritten digit classification | Handwritten digit classification | name matches id | 1 | F01935 |
| Q15 | F00059 | MNIST Handwritten Digit Recognition | MNIST Handwritten Digit Recognition | name matches id | 1 | F00059 |
| Q16 | F01863 | Symbolic Regression | Symbolic Regression | name matches id | 1 | F01863 |
| Q16 | F01940 | Spatio-temporal prediction | Spatio-temporal prediction | name matches id | 2 | F01940 |
| Q17 | F01319 | Steel Plates Faults (SPF) | Steel Plates Faults (SPF) | name matches id | 1 | F01319 |
| Q17 | F00305 | WSN deployment problem | WSN deployment problem | name matches id | 1 | F00305 |
| Q18 | F00272 | 3D Multi-Objective Path Planning (MOPP) | 3D Multi-Objective Path Planning (MOPP) | name matches id | 1 | F00272 |
| Q18 | F01258 | Path Planning | Path Planning | name matches id | 1 | F01258 |
| Q18 | F00096 | uav path planning | uav path planning | name matches id | 3 | F00096 |
| Q19 | F00188 | Vehicle aerodynamic drag optimization | Vehicle aerodynamic drag optimization | name matches id | 1 | F00188 |
| Q20 | F00636 | Water Distribution Network Optimization (SN200, SN300, SN400, SN500, MN200, MN300, MN400, MN500, Balerma) | Water Distribution Network Optimization (SN200, SN300, SN400, SN500, MN200, MN300, MN400, MN500, Balerma) | name matches id | 1 | F00636 |
| Q20 | F00637 | Modena Water Distribution Network | Modena Water Distribution Network | name matches id | 1 | F00637 |
| Q20 | F00392 | Chesapeake Bay Watershed Optimization | Chesapeake Bay Watershed Optimization | name matches id | 1 | F00392 |

## Invalid queries

**t3: 0 invalid** (none)

**t4: 0 invalid** (none)

## t4 names through resolve_gold_names.py (information only; does not decide validity)

20 queries: 20 resolve fully by name, and 20 of these resolve to exactly the ids written in the file.


## Query similarity (dense cosine, all-mpnet-base-v2, query text only)

Identical texts (normalised) across t3, t4, t1, queries_v2: 0.

| set | against | best cosine >= 0.8 (flag) | >= 0.95 (duplicate) | max |
|---|---|---|---|---|
| t3 | queries_v2 | 0 | 0 | 0.527 |
| t3 | t1 | 0 | 0 | 0.688 |
| t3 | t4 | 0 | 0 | 0.519 |
| t4 | queries_v2 | 0 | 0 | 0.667 |
| t4 | t1 | 0 | 0 | 0.569 |
| t4 | t3 | 0 | 0 | 0.519 |

Within-set maximum cosine: t3 0.607, t4 0.791.

Flags (>= 0.8):

- none

Highest best-match per comparison:

- t3:Q13 ↔ queries_v2:Q46, 0.527: "I am developing a scheduling system that assigns doctors and nurses to different hospital shifts. Th" ↔ "project scheduling where tasks need workers with specific skills and resources are limited, minimise"
- t3:Q08 ↔ t1:Q18, 0.688: "I want to develop an optimization algorithm that automatically determines traffic signal timings at " ↔ "traffic signal timing for a few intersections with an EA, minimise average waiting time from a simul"
- t3:Q08 ↔ t4:Q10, 0.519: "I want to develop an optimization algorithm that automatically determines traffic signal timings at " ↔ "I need to find the weights and threshold values of a neural network for traffic signal control using"
- t4:Q14 ↔ queries_v2:Q32, 0.667: "Engineering optimisation with energy efficiency and operational cost as objectives, for solar panel " ↔ "wind farm design: maximise energy but also minimise cable cost, plus layout constraints for the turb"
- t4:Q13 ↔ t1:Q07, 0.569: "designing a supply chain for perishable products where warehouse locations, retailer inventory level" ↔ "food delivery platform, assigning orders to riders online as orders keep coming in, minimising deliv"
- t4:Q10 ↔ t3:Q08, 0.519: "I need to find the weights and threshold values of a neural network for traffic signal control using" ↔ "I want to develop an optimization algorithm that automatically determines traffic signal timings at "

## Corpus closeness (descriptive; amendment 3 s. 5)

Each query's maximum cosine with the matching_text of all 11,342 paper rows (frozen `paper_embeddings.npy`). Queries embedded with all-mpnet-base-v2 in this session (sentence-transformers 6.2.0, torch 2.15.0+cpu).

| set | n | min | 25% | median | 75% | 90% | max | mean | share >= 0.7 | share >= 0.8 |
|---|---|---|---|---|---|---|---|---|---|---|
| queries_v2 | 55 | 0.389 | 0.483 | 0.537 | 0.615 | 0.649 | 0.713 | 0.545 | 0.04 | 0.00 |
| t1 | 20 | 0.402 | 0.463 | 0.550 | 0.589 | 0.619 | 0.689 | 0.528 | 0.00 | 0.00 |
| t3 | 20 | 0.423 | 0.493 | 0.558 | 0.583 | 0.612 | 0.661 | 0.541 | 0.00 | 0.00 |
| t4 | 20 | 0.390 | 0.498 | 0.519 | 0.538 | 0.581 | 0.643 | 0.517 | 0.00 | 0.00 |
