"""
Part 9 - Evaluation runner. Run this in your own environment (same one Part 7/8
run in), after test_queries.json, part7_live_pipeline.py, and part8_final_output.py
are all in place.

Reports:
- Accuracy on 'easy' queries (should be near 100%)
- Behavior on 'hard' queries (correct distinction, or honest low-confidence flag
  on the two deliberately-ambiguous ones -- both count as a good outcome there)
- False-positive rate on 'out_of_scope' queries (should be 0% -- any confident
  match here is a real problem, not a minor miss)
- Calibration: does 'margin' actually track correctness? (mean margin for
  correct vs incorrect/unmapped results)
"""

import json
from part7_live_pipeline import map_user_description
from part8_final_output import assemble_final_output

with open('test_queries.json') as f:
    test_queries = json.load(f)

results = []
for tq in test_queries:
    retrieval = map_user_description(tq['query'])
    final = assemble_final_output(retrieval, query_text=tq['query'])

    actual_entity_id = final.get('matched_entity', {}).get('entity_id') if final.get('mapped') else None
    margin = retrieval.get('margin')

    if tq['difficulty'] == 'out_of_scope':
        correct = not final.get('mapped', False)  # correct = system said no match
    elif tq['expected_entity_id'] is None:
        correct = None  # deliberately ambiguous hard case -- judged manually, not auto-scored
    else:
        correct = (actual_entity_id == tq['expected_entity_id'])

    results.append({
        'id': tq['id'],
        'difficulty': tq['difficulty'],
        'query': tq['query'],
        'expected': tq.get('expected_name'),
        'actual_mapped': final.get('mapped'),
        'actual_entity': final.get('matched_entity', {}).get('canonical_name') if final.get('mapped') else final.get('top_candidate_seen'),
        'margin': margin,
        'correct': correct,
    })

# ---- Report ----
print(f"{'ID':<10} {'Difficulty':<14} {'Correct':<10} {'Margin':<8} {'Expected -> Actual'}")
print('-' * 100)
for r in results:
    correct_str = 'N/A' if r['correct'] is None else ('YES' if r['correct'] else 'NO')
    margin_str = f"{r['margin']:.3f}" if r['margin'] is not None else 'n/a'
    print(f"{r['id']:<10} {r['difficulty']:<14} {correct_str:<10} {margin_str:<8} {r['expected']} -> {r['actual_entity']}")

print()
easy_results = [r for r in results if r['difficulty'] == 'easy']
oos_results = [r for r in results if r['difficulty'] == 'out_of_scope']
hard_scored = [r for r in results if r['difficulty'] == 'hard' and r['correct'] is not None]

easy_acc = sum(r['correct'] for r in easy_results) / len(easy_results)
oos_false_positive_rate = sum(not r['correct'] for r in oos_results) / len(oos_results)
hard_acc = sum(r['correct'] for r in hard_scored) / len(hard_scored) if hard_scored else None

print(f"Easy accuracy: {easy_acc:.0%} ({sum(r['correct'] for r in easy_results)}/{len(easy_results)})")
print(f"Out-of-scope FALSE POSITIVE rate: {oos_false_positive_rate:.0%} "
      f"({sum(not r['correct'] for r in oos_results)}/{len(oos_results)}) -- should be 0%")
if hard_acc is not None:
    print(f"Hard (scorable) accuracy: {hard_acc:.0%} ({sum(r['correct'] for r in hard_scored)}/{len(hard_scored)})")

# Calibration: does margin actually separate correct from incorrect/unmapped?
correct_margins = [r['margin'] for r in results if r['correct'] and r['margin'] is not None]
incorrect_margins = [r['margin'] for r in results if r['correct'] is False and r['margin'] is not None]
if correct_margins and incorrect_margins:
    print()
    print(f"Mean margin when CORRECT: {sum(correct_margins)/len(correct_margins):.3f}")
    print(f"Mean margin when INCORRECT: {sum(incorrect_margins)/len(incorrect_margins):.3f}")
    print("(if these are close together, margin_threshold isn't actually separating good from bad matches well)")

with open('part9_eval_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print('\nFull results saved to part9_eval_results.json')
