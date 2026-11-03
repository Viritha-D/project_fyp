"""
Score a human-written query set with the same metrics as the automatic evaluation.

Input: a CSV like human_queries_template.csv (lines starting with '#' are ignored) with columns
query_id, query_text, gold_families (family ids separated by ';'), notes. Gold families must be chosen
before anyone sees system output.
Runs the full pipeline and the three baselines on the published index (config.json), writes
results_human.csv and report_human.md next to the input file.

Usage: python retrieval_v2/evaluation/score_human_queries.py <queries.csv>
"""

import io
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import evaluate as ev  # noqa: E402
import hybrid  # noqa: E402


def read_queries(p):
    text = ''.join(l for l in Path(p).read_text(encoding='utf-8').splitlines(keepends=True) if not l.startswith('#'))
    q = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    need = {'query_id', 'query_text', 'gold_families'}
    assert need <= set(q.columns), f'missing columns: {need - set(q.columns)}'
    q = q[q['query_text'].str.strip() != '']
    assert q['query_id'].is_unique, 'query_id must be unique'
    return q


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1])
    Q = read_queries(src)
    idx = hybrid.Index.from_config()
    fam_ids = set(idx.fam.values())
    golds = []
    for _, r in Q.iterrows():
        g = {f.strip() for f in r['gold_families'].split(';') if f.strip()}
        bad = g - fam_ids
        assert g and not bad, f'{r.query_id}: unknown or empty gold family ids {sorted(bad) or "(none given)"}'
        golds.append(g)
    res = ev.run_systems(idx, Q['query_text'].tolist(), golds)
    R = pd.DataFrame([{'query_id': qid, 'Category': 'all', **r}
                      for qid, r in zip([q for q in Q['query_id'] for _ in ev.SYSTEMS], res)])
    R.to_csv(src.with_name('results_human.csv'), index=False)
    lines = [f'# Retrieval v2: human-phrased queries ({len(Q)} queries from {src.name})', '',
             ev.table(R), '', '## Margin gate (full pipeline)', '', ev.gate_report(R), '']
    src.with_name('report_human.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
