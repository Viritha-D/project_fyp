"""
Score a written query set with the frozen retrieval models (tag retrieval-v2.1-frozen).

Input: a CSV (lines starting with '#' are ignored) with columns query_id, query_text, gold_families (family ids
separated by ';'), and optionally gold_family_names and notes. Gold families must be chosen before anyone sees
system output.

Systems (published index, all papers): popularity, bm25_only, dense_only, full_v2 (Part B, hybrid.py) and
paper_knn, stacked (v2.1 deployment model retrieval_v2/v21_model.json via recommend_v21.rank_batch).
Metrics: hit@1/3/5, recall@5, MRR, 95% bootstrap intervals over queries (1,000 resamples, seed 42).
Group = text of `notes` before the first ';' with any parenthetical qualifier removed.
Confidence tiers of the stacked ranker use the frozen cut-offs in v21_model.json.

Writes results_<stem>.csv and report_<stem>.md next to the input file.

Usage: python retrieval_v2/evaluation/score_human_queries.py <queries.csv> [<queries.csv> ...]
"""

import io
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import evaluate as ev  # noqa: E402
import evaluate_v21 as e21  # noqa: E402
import hybrid  # noqa: E402
import recommend_v21 as r21  # noqa: E402
import v21  # noqa: E402

SYSTEMS = ['popularity', 'bm25_only', 'dense_only', 'full_v2', 'paper_knn', 'stacked']


def read_queries(p):
    text = ''.join(l for l in Path(p).read_text(encoding='utf-8').splitlines(keepends=True) if not l.startswith('#'))
    q = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    need = {'query_id', 'query_text', 'gold_families'}
    assert need <= set(q.columns), f'missing columns: {need - set(q.columns)}'
    q = q[q['query_text'].str.strip() != ''].reset_index(drop=True)
    assert q['query_id'].is_unique, 'query_id must be unique'
    if 'notes' not in q:
        q['notes'] = ''
    return q


def group_of(notes):
    g = re.sub(r'\([^)]*\)', '', str(notes).split(';')[0]).strip()
    return re.sub(r'\s+', ' ', g) or '(no notes)'


def excluded_families():
    e2f = pd.read_csv(hybrid.path(hybrid.CONFIG['families']['entity_to_family']), dtype=str, keep_default_na=False)
    ex = v21.excluded_entities()
    return {f for f, g in e2f.groupby('family_id') if set(g['entity_id']) <= ex}


def score(src):
    Q = read_queries(src)
    idx = hybrid.Index.from_config()
    fam_ids, exfam = set(idx.fam.values()), excluded_families()
    golds = []
    for _, r in Q.iterrows():
        g = {f.strip() for f in r['gold_families'].split(';') if f.strip()}
        bad = g - fam_ids
        assert g and not bad, f'{r.query_id}: unknown or empty gold family ids {sorted(bad) or "(none given)"}'
        assert g - exfam, f'{r.query_id}: only excluded gold families'
        golds.append(g)
    queries = Q['query_text'].tolist()
    partb = ev.run_systems(idx, queries, golds)
    st = r21.rank_batch(queries)
    clean = r21._load()['clean']
    rows = []
    for i, (q, g) in enumerate(zip(Q.itertuples(), golds)):
        base = {'paper_key': q.query_id, 'query_id': q.query_id, 'group': group_of(q.notes),
                'gold': ';'.join(sorted(g))}
        for s in partb[i * 4:(i + 1) * 4]:
            rows.append({**base, 'system': 'full_v2' if s['system'] == 'full' else s['system'],
                         **{m: s[m] for m in ev.METRICS}, 'top5': s['top5']})
        r = st[i]
        knn = r['knn_order'][:10]
        rows.append({**base, 'system': 'paper_knn', **ev.per_query(knn, g), 'top5': ';'.join(knn[:5])})
        order = r['order']
        ranks = [order.index(f) + 1 for f in g if f in order]
        rows.append({**base, 'system': 'stacked', **ev.per_query(order[:10], g), 'top5': ';'.join(order[:5]),
                     'top1_prob': r['top1_prob'], 'tier': r['tier'],
                     'gold_in_candidates': any(f in r['cands'] for f in g),
                     'best_gold_rank': min(ranks) if ranks else None,
                     'gold_all_lt2_papers': all(clean.fam_papers.get(f, 0) < 2 for f in g),
                     'gold_any_lt2_papers': any(clean.fam_papers.get(f, 0) < 2 for f in g)})
    R = pd.DataFrame(rows)
    R.drop(columns='paper_key').to_csv(src.with_name(f'results_{src.stem}.csv'), index=False)
    return Q, R


def tiers(R):
    x = R[R.system == 'stacked']
    lines = ['| tier | n | mean predicted p(top-1 gold) | hit@1 |', '|---|---|---|---|']
    for t in ('low', 'medium', 'high'):
        s = x[x.tier == t]
        lines.append(f'| {t} | {len(s)} | {s.top1_prob.mean() if len(s) else float("nan"):.3f} | {ev.fmt(ev.boot(s["hit@1"]))} |')
    return '\n'.join(lines)


def primary(R):
    lines = ['| comparison | d hit@5 | d MRR |', '|---|---|---|']
    for ref in ('popularity', 'full_v2'):
        lines.append(f'| stacked - {ref} | {ev.fmt(e21.paired(R, "stacked", ref, "hit@5"))} | '
                     f'{ev.fmt(e21.paired(R, "stacked", ref, "mrr"))} |')
    return '\n'.join(lines)


def report(src, Q, R):
    sizes = R[R.system == 'stacked']['group'].value_counts()
    lines = [f'# Query set `{src.name}`: {len(Q)} queries', '',
             'Frozen models (tag retrieval-v2.1-frozen). Means with 95% bootstrap intervals over queries.', '',
             '## Overall', '', e21.table(R, systems=SYSTEMS), '',
             '## Primary comparisons (paired bootstrap, stacked minus reference)', '', primary(R), '',
             '## By group', '', 'Group sizes: ' + ', '.join(f'{g} {n}' for g, n in sizes.items()), '',
             e21.table(R, 'group', systems=SYSTEMS), '',
             '## Stacked confidence tiers (frozen cut-offs)', '', tiers(R), '']
    src.with_name(f'report_{src.stem}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for p in sys.argv[1:]:
        src = Path(p)
        Q, R = score(src)
        report(src, Q, R)
    return 0


if __name__ == '__main__':
    sys.exit(main())
