import os
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')
os.environ.setdefault('TRANSFORMERS_VERBOSITY', 'error')
import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)

from part7_live_pipeline import map_user_description, diagnose_candidate_reach
import json

q = "How should your algorithm handle a route that has excellent delivery timing but runs out of battery (-5%) mid-way?"
r = map_user_description(q)
print(json.dumps(r, indent=2, ensure_ascii=False))
print()
print('=== diagnostic vs E00000 (Online Meal Delivery Problem) ===')
diagnose_candidate_reach(q, 'E00000', top_k=20)
print()
print('=== diagnostic vs E00612 (SPSC battery) ===')
diagnose_candidate_reach(q, 'E00612', top_k=20)
