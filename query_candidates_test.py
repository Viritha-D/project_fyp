import os
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')
os.environ.setdefault('TRANSFORMERS_VERBOSITY', 'error')
import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)

from part7_live_pipeline import map_user_description

candidates = [
    "minimize a rugged multimodal function with many local minima and oscillating structure",
    "I need a strategy for battery charge equalization using a switched capacitor balancing circuit",
    "simple unimodal convex objective function with a single global optimum",
    "IEEE CEC 2017 numerical optimization competition suite with unimodal and multimodal functions",
    "find the shortest route visiting a set of cities exactly once and returning to the start",
    "planning efficient delivery routes for online food orders in a city",
    "planning where to place RFID readers in a network to maximize coverage",
    "maximize the number of consecutive 1-bits from the start of a binary string",
    "tuning hyperparameters of a restricted boltzmann machine neural network",
    "scheduling jobs on a factory floor with dynamic arrivals and flexible machines",
    "hyperparameter tuning for a temperature parameter in a machine learning model",
    "what's the best way to bake a chocolate cake",  # nonsense / out-of-scope
    "recommend a good movie to watch this weekend",  # nonsense / out-of-scope
]

for q in candidates:
    r = map_user_description(q)
    if r.get('mapped'):
        top = r['results'][0]
        print(f"MAPPED   margin={r['margin']:.2f}  n_papers={top['n_supporting_papers']:<3}  "
              f"-> {top['canonical_name']}")
    else:
        top = r['results'][0]['canonical_name'] if r.get('results') else 'n/a'
        print(f"UNMAPPED margin={r.get('margin')}  (closest seen: {top})")
    print(f"  query: \"{q}\"")
    print()
