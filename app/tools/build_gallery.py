"""
Precompute the gallery: run the product system v2.3 = blend 0.5 (live.recommend, the same path as the local app) on the six fixed
development queries in app/demo_inputs.json and save the unedited output to app/gallery.json, with the gold families
from queries_v2 and a hit/miss label (hit = a gold family in the top 5). Nothing is swapped or edited.

Refuses to run if app/tools/check_demo_inputs.py fails. Needs the live environment (FROZEN_ENV.txt + streamlit).

Usage: python app/tools/build_gallery.py
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'app'))


def main():
    r = subprocess.run([sys.executable, str(ROOT / 'app/tools/check_demo_inputs.py')], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print('check_demo_inputs.py failed: gallery not built.')
        return 1
    import core
    import live
    d = json.loads((ROOT / 'app/demo_inputs.json').read_text(encoding='utf-8'))
    items = []
    for g in d['gallery']:
        res = live.recommend(g['query_text'], write=False)          # the gallery never writes to the store
        gold = [x.strip() for x in g['gold_families'].split(';') if x.strip()]
        top5 = [f['family_id'] for f in res['families']]
        items.append({**g, 'result': res, 'gold_ids': gold, 'hit': any(x in top5 for x in gold),
                      'gold_ranks': {x: (top5.index(x) + 1 if x in top5 else None) for x in gold}})
        print(f"{g['query_id']}: {'HIT ' if items[-1]['hit'] else 'MISS'} top5 {[f['family_name'] for f in res['families']]} "
              f"| gold {g['gold_family_names']}")
    out = {'_about': 'Precomputed, unedited output of the product system v2.3 = blend 0.5 (recommend_v23.py, local tag '
                     'retrieval-v2.3-blend) on six fixed queries of the development set queries_v2. Not the independent '
                     'test. Built by app/tools/build_gallery.py.',
           'label': 'development set; lambda was selected on it', 'system': 'v2.3 = blend 0.5', 'rule': d['gallery_rule'],
           'system_hash': items[0]['result']['system_hash'], 'built': core.now_iso(), 'items': items}
    (ROOT / 'app/gallery.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"hits {sum(i['hit'] for i in items)} / {len(items)}; wrote app/gallery.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
