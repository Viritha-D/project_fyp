import os
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')
os.environ.setdefault('TRANSFORMERS_VERBOSITY', 'error')
import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)

from part7_live_pipeline import map_user_description, diagnose_candidate_reach, ENTITIES
import json

q = ("you must visit 4 cities (A,B,C,D) starting and ending at city A. based on the travel costs "
     "below, what is the absolute cheapest route that visits every city exactly once?")

r = map_user_description(q)
print(json.dumps(r, indent=2, ensure_ascii=False))
print()

tsp_entities = [eid for eid, e in ENTITIES.items() if 'travel' in e['canonical_name'].lower()
                and 'salesman' in e['canonical_name'].lower()]
print('TSP-named entities currently in corpus:', tsp_entities)
for eid in tsp_entities:
    print(f'  {eid}: "{ENTITIES[eid]["canonical_name"]}" | base_description: "{ENTITIES[eid]["base_description"]}"')
print()

for eid in tsp_entities:
    print(f'=== diagnostic vs {eid} ===')
    diagnose_candidate_reach(q, eid, top_k=20)
    print()
