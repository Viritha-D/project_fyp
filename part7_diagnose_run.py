from part7_live_pipeline import diagnose_candidate_reach

cases = [
    ("narrow curved valley function, non-separable, classic banana-shaped optimization test case", "E00125"),
    ("three-objective scalable test problem used to evaluate many-objective evolutionary algorithms", "E00070"),
    ("maximize the number of leading consecutive 1-bits in a binary string, a discrete optimization "
     "landscape known for being deceptive for hill-climbers", "E00761"),
]

for query, expected_id in cases:
    diagnose_candidate_reach(query, expected_id, top_k=20)
