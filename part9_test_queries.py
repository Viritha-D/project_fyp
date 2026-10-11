"""
Part 9 - Held-out evaluation query set.

20 hand-written queries (paraphrased, never copy-pasted from entity descriptions),
each tagged with the expected target entity/outcome. Run these through the full
Part 7 + Part 8 pipeline in your own environment and compare actual vs expected.

IMPORTANT: expected_entity_id values were assigned by checking against the real
knowledge base content, but your team should spot-check a handful before trusting
results wholesale -- this is a much lighter check than Part 4's independent
labeling requirement, since "did retrieval find the known entity" is objectively
checkable, not a subjective judgment call.
"""

TEST_QUERIES = [
    # ---- EASY: distinctive, well-evidenced entities. Should map confidently and correctly. ----
    {
        'id': 'easy_1',
        'query': "I want to test my algorithm on a highly multimodal, rugged landscape with many local minima and oscillating structure",
        'expected_entity_id': 'E00126',
        'expected_name': 'Rastrigin',
        'difficulty': 'easy',
        'note': 'Paraphrases Rastrigin\'s known properties without naming it',
    },
    {
        'id': 'easy_2',
        'query': "I need a strategy for battery charge equalization using a series-parallel switched capacitor balancing circuit",
        'expected_entity_id': 'E00612',
        'expected_name': 'Series-Parallel Switched Capacitor (SPSC) Active Charge Balancing',
        'difficulty': 'easy',
        'note': 'Same query used in the live pipeline test earlier -- should still work post-fix',
    },
    {
        'id': 'easy_3',
        'query': "simple unimodal sphere-shaped objective function, convex, single global optimum",
        'expected_entity_id': 'E00516',
        'expected_name': 'Sphere function',
        'difficulty': 'easy',
        'note': 'Sphere is the textbook simplest benchmark -- should be an unambiguous match',
    },
    {
        'id': 'easy_4',
        'query': "a bi-objective test problem with a convex Pareto front, commonly used to benchmark evolutionary multi-objective algorithms",
        'expected_entity_id': 'E00065',
        'expected_name': 'ZDT1',
        'difficulty': 'easy',
        'note': 'ZDT1 specifically has a convex Pareto front (distinguishing it from ZDT2/ZDT3)',
    },
    {
        'id': 'easy_5',
        'query': "IEEE CEC 2017 numerical optimization competition suite with unimodal, multimodal, hybrid, and composition functions",
        'expected_entity_id': 'E00200',
        'expected_name': 'CEC 2017 benchmark test suite',
        'difficulty': 'easy',
        'note': 'Tests whether the deterministic CEC name-blocking from Part 4 carries through to retrieval',
    },
    {
        'id': 'easy_6',
        'query': "narrow curved valley function, non-separable, classic banana-shaped optimization test case",
        'expected_entity_id': 'E00125',
        'expected_name': 'Rosenbrock',
        'difficulty': 'easy',
        'note': 'Rosenbrock is famous specifically for its curved valley shape',
    },
    {
        'id': 'easy_7',
        'query': "maximize the number of 1-bits in a binary string using an evolutionary algorithm",
        'expected_entity_id': 'E00760',
        'expected_name': 'Onemax',
        'difficulty': 'easy',
        'note': 'OneMax is a foundational discrete/combinatorial EA benchmark',
    },
    {
        'id': 'easy_8',
        'query': "three-objective scalable test problem used to evaluate many-objective evolutionary algorithms",
        'expected_entity_id': 'E00070',
        'expected_name': 'DTLZ1',
        'difficulty': 'easy',
        'note': 'DTLZ suite is specifically designed for scalable many-objective testing',
    },

    # ---- HARD: near-miss cases, testing whether the system distinguishes similar entities ----
    {
        'id': 'hard_1',
        'query': "multi-objective test problem that is deceptive and considered one of the harder problems in its benchmark family to approximate",
        'expected_entity_id': 'E00068',
        'expected_name': 'ZDT4',
        'difficulty': 'hard',
        'note': 'Must distinguish ZDT4 specifically from ZDT1/2/3/6 -- only ZDT4 is known as the hard-to-approximate one',
    },
    {
        'id': 'hard_2',
        'query': "CEC benchmark suite with only 10 functions, real-parameter single-objective bound-constrained optimization, from a recent competition year",
        'expected_entity_id': None,  # ambiguous by design -- could plausibly be CEC 2021 OR CEC 2022
        'expected_name': 'AMBIGUOUS (CEC 2021 or CEC 2022 both plausible)',
        'difficulty': 'hard',
        'note': 'Deliberately underspecified year -- a good result here is a low margin / correctly flagged uncertainty, not a wrong confident answer',
    },
    {
        'id': 'hard_3',
        'query': "a non-convex, disconnected Pareto front multi-objective problem in the same well-known bi-objective test family as ZDT1",
        'expected_entity_id': 'E00067',
        'expected_name': 'ZDT3',
        'difficulty': 'hard',
        'note': 'ZDT3 specifically has a disconnected Pareto front, distinguishing it from ZDT1 (convex) and ZDT2 (non-convex but connected)',
    },
    {
        'id': 'hard_4',
        'query': "single-objective real-parameter optimization suite from 2013 focused specifically on niching and multimodal optimization",
        'expected_entity_id': None,  # tests whether the system distinguishes standard CEC2013 from the CEC2013 Niching sub-suite
        'expected_name': 'AMBIGUOUS: could match CEC-2013 Real Parameter Optimization OR the separate CEC2013 Niching Benchmark Suite',
        'difficulty': 'hard',
        'note': 'Tests the suite-vs-different-suite distinction found during Part 4 validation (F8 Niching suite vs standard CEC2013)',
    },
    {
        'id': 'hard_5',
        'query': "maximize the number of leading consecutive 1-bits in a binary string, a discrete optimization landscape known for being deceptive for hill-climbers",
        'expected_entity_id': 'E00761',
        'expected_name': 'LeadingOnes',
        'difficulty': 'hard',
        'note': 'Must distinguish from OneMax (easy_7) -- similar surface description, different landscape properties',
    },
    {
        'id': 'hard_6',
        'query': "battery cell balancing approach that reports equalization time as its main performance measure",
        'expected_entity_id': 'E00612',
        'expected_name': 'Series-Parallel Switched Capacitor (SPSC) Active Charge Balancing',
        'difficulty': 'hard',
        'note': 'Tests whether the Part 6 metric-normalization fix (Equalization time family) surfaces coherent strategy comparison, not just correct entity match',
    },

    # ---- OUT-OF-SCOPE: genuinely unrelated to the knowledge base. Should correctly report no match. ----
    {
        'id': 'oos_1',
        'query': "what's a good recipe for pasta carbonara",
        'expected_entity_id': None,
        'expected_name': 'NO MATCH EXPECTED',
        'difficulty': 'out_of_scope',
        'note': 'Same query already tested manually -- confirmed working (margin 0.009)',
    },
    {
        'id': 'oos_2',
        'query': "recommend a good science fiction movie to watch this weekend",
        'expected_entity_id': None,
        'expected_name': 'NO MATCH EXPECTED',
        'difficulty': 'out_of_scope',
        'note': None,
    },
    {
        'id': 'oos_3',
        'query': "how do I file my income tax return this year",
        'expected_entity_id': None,
        'expected_name': 'NO MATCH EXPECTED',
        'difficulty': 'out_of_scope',
        'note': None,
    },
    {
        'id': 'oos_4',
        'query': "plan a 5-day vacation itinerary for a trip to Japan",
        'expected_entity_id': None,
        'expected_name': 'NO MATCH EXPECTED',
        'difficulty': 'out_of_scope',
        'note': None,
    },
    {
        'id': 'oos_5',
        'query': "explain the plot of Romeo and Juliet",
        'expected_entity_id': None,
        'expected_name': 'NO MATCH EXPECTED',
        'difficulty': 'out_of_scope',
        'note': 'Tests a query that is coherent, grammatical, and even academic-sounding, unlike the more obviously silly oos_1/oos_2',
    },
    {
        'id': 'oos_6',
        'query': "I want to optimize my daily gym workout split for muscle growth",
        'expected_entity_id': None,
        'expected_name': 'NO MATCH EXPECTED',
        'difficulty': 'out_of_scope',
        'note': 'Deliberately tricky: uses the word "optimize" naturally, testing whether that alone causes a false positive match',
    },
]

if __name__ == '__main__':
    import json
    print(f'Total test queries: {len(TEST_QUERIES)}')
    for d in ['easy', 'hard', 'out_of_scope']:
        print(f'  {d}: {sum(1 for q in TEST_QUERIES if q["difficulty"]==d)}')
    with open('test_queries.json', 'w') as f:
        json.dump(TEST_QUERIES, f, indent=2)
    print('\nSaved to test_queries.json')
