import json
import pandas as pd

entities = {e['entity_id']: e for e in json.load(open('problem_entities.json', encoding='utf-8'))}
master = pd.read_csv('papers_master_with_embeddings_ref.csv')
emap = pd.read_csv('paper_to_entity_map_final.csv')

candidates = ['E00376', 'E00435', 'E00822', 'E00857', 'E00912', 'E00916', 'E00940', 'E00491']

for eid in candidates:
    e = entities[eid]
    print(f"--- {eid} ---")
    print(f"  canonical_name: {e['canonical_name']}")
    print(f"  category: {e['category']}")
    print(f"  n_supporting_papers: {e['n_supporting_papers']}, n_member_rows: {e['n_member_rows']}")
    print(f"  base_description: {e['base_description']}")
    print(f"  aliases.benchmark_names: {e['aliases']['benchmark_names']}")
    mrows = emap[emap['entity_id']==eid]['paper_id']
    sub = master[master['paper_id'].isin(mrows)][['Problem_Context','Dataset_Name']].drop_duplicates()
    print(f"  Problem_Context/Dataset_Name seen: {sub.to_dict('records')}")
    print()
