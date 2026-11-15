"""
Retrieval v2, Part B: five-fold automatic evaluation (no authored test set).

1. Papers (paper_key, after the approved merges) are split into 5 folds, stratified by Category x
   Conference (strata with < 5 papers pooled as 'rare'), seed 42.
2. Per fold, the index is rebuilt from the TRAINING rows only with
   `v2_entities_pipeline.py --hold-out` (entity descriptions, entity embeddings; BM25 is built from those
   descriptions; family n_papers from the training rows). Builds are cached in folds_cache/.
3. One query per held-out paper, from that paper's own fields in a fixed template, with every token of its
   Benchmark_Name / Dataset_Name / Evaluation_Dataset values and of its entities' aliases masked out (field
   values only; the template words and a few stop words are never masked). Gold = the v5 families of the
   paper's records; only gold families present in the fold's index can be found ("seen"); a query with no
   seen gold family is excluded from scoring and counted as unseen.
4. Systems: full pipeline, BM25 only, dense only, popularity. Metrics: hit@1/3/5, recall@5 (seen gold),
   MRR of the first gold family (top 10), unmapped rate and margin-gate accuracy (full pipeline), with 95%
   bootstrap intervals over papers, overall and by Category, Conference and gold evidence.
Nothing is tuned on these results.

Usage: python retrieval_v2/evaluation/evaluate.py [--folds 5] [--rebuild]
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import hybrid  # noqa: E402

ROOT, C = hybrid.ROOT, hybrid.CONFIG
CACHE = HERE / 'folds_cache'
MISSING = {'', 'Not Reported', 'N/A (Pure Math problem)', 'None / Pure Synthetic'}
STOP = {'a', 'an', 'the', 'of', 'for', 'and', 'or', 'in', 'on', 'with', 'to', 'by', 'from', 'as', 'at', 'is', 'via'}
SEED = 42
SYSTEMS = ['popularity', 'bm25_only', 'dense_only', 'full']
METRICS = ['hit@1', 'hit@3', 'hit@5', 'recall@5', 'mrr']


# ---------------------------------------------------------------- data
def load():
    d = pd.read_csv(hybrid.path(C['entities']['master']), dtype=str, keep_default_na=False)
    m = pd.read_csv(hybrid.path(C['entities']['map']), dtype=str, keep_default_na=False)
    e2f = pd.read_csv(hybrid.path(C['families']['entity_to_family']), dtype=str, keep_default_na=False)
    assert m['paper_id'].tolist() == d['Paper_ID'].tolist()
    rows = d.assign(entity_id=m['entity_id'].values, paper_key=m['paper_key'].values)
    rows['family_id'] = rows['entity_id'].map(dict(zip(e2f.entity_id, e2f.family_id)))
    assert rows['family_id'].notna().all()
    ents = json.loads(hybrid.path(C['entities']['descriptions']).read_text(encoding='utf-8'))
    aliases = {e['entity_id']: e['aliases']['benchmark_names'] for e in ents}
    fams = {f['family_id']: f for f in json.loads(hybrid.path(C['families']['families']).read_text(encoding='utf-8'))}
    return rows, aliases, fams


def make_folds(rows, k):
    from sklearn.model_selection import StratifiedKFold
    p = rows.groupby('paper_key').agg(Category=('Category', lambda s: s.value_counts().index[0]),
                                      Conference=('Conference', 'first')).reset_index()
    p['stratum'] = p['Category'] + '|' + p['Conference']
    small = p['stratum'].value_counts()
    p.loc[p['stratum'].map(small) < k, 'stratum'] = 'rare'
    p['fold'] = -1
    for i, (_, test) in enumerate(StratifiedKFold(k, shuffle=True, random_state=SEED).split(p, p['stratum'])):
        p.loc[test, 'fold'] = i
    assert (p['fold'] >= 0).all()
    return p


def fold_index(fold, held_keys, rows, rebuild):
    out = CACHE / f'fold{fold}'
    out.mkdir(parents=True, exist_ok=True)
    keys_file = out / 'heldout_paper_keys.txt'
    text = '\n'.join(sorted(held_keys)) + '\n'
    digest = hashlib.sha256(text.encode()).hexdigest()
    stamp = out / 'build.sha256'
    if rebuild or not stamp.exists() or stamp.read_text().strip() != digest or not (out / 'entity_embeddings.npy').exists():
        keys_file.write_text(text, encoding='utf-8')
        r = subprocess.run([sys.executable, str(ROOT / 'v2_entities_pipeline.py'), '--hold-out', str(keys_file),
                            '--out-dir', str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        print('   ' + [l for l in r.stdout.splitlines() if l.startswith('[hold-out]')][0], flush=True)
        stamp.write_text(digest)
    train = rows[~rows['paper_key'].isin(held_keys)]
    return hybrid.Index.from_holdout(out, train), train


# ---------------------------------------------------------------- queries
def real(values):
    return [v.strip() for v in values if v.strip() and v.strip() not in MISSING]


def most_common(values, k=1):
    return [v for v, _ in Counter(real(values)).most_common(k)]


def mask(text, masked):
    out = re.sub(r'[A-Za-z0-9]+', lambda t: '' if t.group(0).lower() in masked else t.group(0), text)
    out = re.sub(r'\(\s*[,;/\- ]*\)', '', out)
    out = re.sub(r'\s+([,;:)])', r'\1', re.sub(r'\s{2,}', ' ', out)).strip(' ,;:-/')
    return out if re.search(r'[A-Za-z0-9]', out) else ''


def build_query(g, aliases):
    masked = set()
    for col in ('Benchmark_Name', 'Dataset_Name', 'Evaluation_Dataset'):
        for v in real(g[col]):
            masked |= set(re.findall(r'[a-z0-9]+', v.lower()))
    for e in g['entity_id'].unique():
        for a in aliases[e]:
            masked |= set(re.findall(r'[a-z0-9]+', a.lower()))
    masked -= STOP
    f = lambda vals: [x for x in (mask(v, masked) for v in vals) if x]
    alg = f(most_common(g['Algorithm_Name'], 3))
    ctx = f(most_common(g['Problem_Context']))
    ind = f(most_common(g.loc[g['Category'] == 'Applied', 'Industry']))
    dim = f(most_common(g['Dimensionality']))
    land = f(most_common(g['Modality']) + most_common(g['Separability']) +
             [t for t, _ in Counter(t.strip() for v in real(g['Landscape_Characteristics'])
                                    for t in v.split(';') if t.strip()).most_common(3)])
    met = f(most_common(g['Performance_Metric']))
    q = f"I developed {', '.join(alg) if alg else 'an algorithm'} for {ctx[0] if ctx else 'my problem'}"
    if ind:
        q += f' in {ind[0]}'
    if dim:
        q += f'; dimension {dim[0]}'
    if land:
        q += f"; landscape {', '.join(land)}"
    if met:
        q += f'; results measured by {met[0]}'
    return q + '. Which benchmarks should I test it on?'


# ---------------------------------------------------------------- metrics
def per_query(ranked_ids, gold):
    top = ranked_ids[:10]
    hit = lambda k: float(any(f in gold for f in top[:k]))
    rr = next((1.0 / (i + 1) for i, f in enumerate(top) if f in gold), 0.0)
    return {'hit@1': hit(1), 'hit@3': hit(3), 'hit@5': hit(5),
            'recall@5': len(set(top[:5]) & gold) / len(gold), 'mrr': rr}


def boot(values, n=1000, seed=SEED):
    v = np.asarray(values, dtype=float)
    if len(v) == 0:
        return float('nan'), float('nan'), float('nan')
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), (n, len(v)))].mean(axis=1)
    return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def fmt(t):
    m, lo, hi = t
    return '-' if np.isnan(m) else f'{m:.3f} [{lo:.3f}, {hi:.3f}]'


def table(R, by=None, systems=SYSTEMS):
    """Markdown table of METRICS (+ unmapped for full) with bootstrap CIs, optionally per group."""
    lines = []
    groups = [('all', R)] if by is None else [(str(k), g) for k, g in R.groupby(by)]
    head = '| group | system | n | ' + ' | '.join(METRICS) + ' | unmapped |'
    lines += [head, '|' + '---|' * (len(METRICS) + 4)]
    for name, g in groups:
        for s in systems:
            x = g[g['system'] == s]
            if x.empty:
                continue
            unm = fmt(boot(1 - x['mapped'].astype(float))) if s == 'full' else ''
            lines.append(f'| {name} | {s} | {len(x)} | ' + ' | '.join(fmt(boot(x[mm])) for mm in METRICS) + f' | {unm} |')
    return '\n'.join(lines)


def gate_report(R):
    x = R[R['system'] == 'full'].copy()
    out = ['| subset | n | hit@1 |', '|---|---|---|']
    for lab, sub in [('mapped (margin >= threshold or one family)', x[x['mapped']]), ('not mapped', x[~x['mapped']])]:
        out.append(f'| {lab} | {len(sub)} | {fmt(boot(sub["hit@1"]))} |')
    has = x[x['margin'].notna()].copy()
    if len(has) >= 5:
        has['margin_bin'] = pd.qcut(has['margin'], 5, duplicates='drop')
        out += ['', '| margin quintile | n | hit@1 |', '|---|---|---|']
        for b, sub in has.groupby('margin_bin', observed=True):
            out.append(f'| {b} | {len(sub)} | {fmt(boot(sub["hit@1"]))} |')
        from scipy.stats import spearmanr  # noqa
        rho = spearmanr(has['margin'], has['hit@1']).correlation if has['hit@1'].nunique() > 1 else float('nan')
        out.append(f'\nSpearman correlation of margin and hit@1 (queries with a margin): {rho:.3f}')
    one = x[x['margin'].isna()]
    out.append(f'Queries whose shortlist held one family only (no margin, counted as mapped): {len(one)}, '
               f'hit@1 {fmt(boot(one["hit@1"]))}')
    q = has['margin'].quantile([0, .1, .25, .5, .75, .9, 1]).round(3).to_dict() if len(has) else {}
    out.append(f'Margin distribution (full pipeline): {q}; share >= {C["retrieval"]["margin_threshold"]}: '
               f'{(has["margin"] >= C["retrieval"]["margin_threshold"]).mean():.3f}')
    return '\n'.join(out)


# ---------------------------------------------------------------- run
def run_systems(idx, queries, golds):
    qv = hybrid.encode_queries(queries)
    full = idx.rank_full(queries, qv)
    pop = [f['family_id'] for f in idx.rank_popularity()[:10]]
    res = []
    for i, (q, g) in enumerate(zip(queries, golds)):
        ranked = {'popularity': pop,
                  'bm25_only': [f['family_id'] for f in idx.rank_bm25_only(q)][:10],
                  'dense_only': [f['family_id'] for f in idx.rank_dense_only(qv[i])][:10],
                  'full': [f['family_id'] for f in full[i]['families']][:10]}
        for s, ids in ranked.items():
            res.append({'system': s, **per_query(ids, g), 'top5': ';'.join(ids[:5]),
                        'mapped': full[i]['mapped'] if s == 'full' else True,
                        'margin': full[i]['margin'] if s == 'full' else None,
                        'top3_scores': ';'.join(f"{f['score']:.3f}" for f in full[i]['families'][:3]) if s == 'full' else ''})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--folds', type=int, default=5)
    ap.add_argument('--rebuild', action='store_true')
    a = ap.parse_args()
    rows, aliases, fams = load()
    papers = make_folds(rows, a.folds)
    papers.to_csv(HERE / 'folds.csv', index=False)
    print(f'{len(papers)} papers in {a.folds} folds: {papers.fold.value_counts().sort_index().tolist()}')
    by_paper = {k: g for k, g in rows.groupby('paper_key')}
    qrows, results = [], []
    for fold in range(a.folds):
        held = set(papers.loc[papers.fold == fold, 'paper_key'])
        print(f'fold {fold}: {len(held)} held-out papers', flush=True)
        idx, train = fold_index(fold, held, rows, a.rebuild)
        seen_fams = set(idx.fam.values())
        fam_train_papers = idx.fam_papers
        qs, gs, meta = [], [], []
        for pk in sorted(held):
            g = by_paper[pk]
            gold = set(g['family_id'])
            seen = gold & seen_fams
            q = build_query(g, aliases)
            info = papers.set_index('paper_key').loc[pk]
            rec = {'paper_key': pk, 'fold': fold, 'Category': info['Category'], 'Conference': info['Conference'],
                   'query': q, 'gold_families': ';'.join(sorted(gold)), 'seen_gold': ';'.join(sorted(seen)),
                   'unseen': not seen,
                   'gold_evidence': ('gold family >= 2 training papers'
                                     if any(fam_train_papers.get(f, 0) >= 2 for f in seen) else 'gold families < 2 training papers')}
            qrows.append(rec)
            if seen:
                qs.append(q)
                gs.append(seen)
                meta.append(rec)
        for rec, r in zip([m for m in meta for _ in SYSTEMS], run_systems(idx, qs, gs)):
            results.append({**{k: rec[k] for k in ('paper_key', 'fold', 'Category', 'Conference', 'gold_evidence', 'seen_gold')}, **r})
        print(f'   scored {len(qs)} queries; unseen {len(held) - len(qs)}', flush=True)

    Q, R = pd.DataFrame(qrows), pd.DataFrame(results)
    Q.to_csv(HERE / 'queries_auto.csv', index=False)
    R.to_csv(HERE / 'results_auto.csv', index=False)
    write_report(Q, R, fams)


def write_report(Q, R, fams):
    name = lambda f: fams[f]['family_name'] if f in fams else f
    n_unseen = int(Q['unseen'].sum())
    full = R[R['system'] == 'full']
    pop = R[R['system'] == 'popularity']
    beats = {mm: full[mm].mean() > pop[mm].mean() for mm in METRICS}
    lines = ['# Retrieval v2: five-fold automatic evaluation', '',
             f'Papers: {len(Q)}; scored queries: {len(full)}; **unseen** (no gold family in the fold index, excluded): '
             f'**{n_unseen}** ({n_unseen / len(Q):.1%}).', '',
             'Values are means with 95% bootstrap intervals over papers (1,000 resamples). hit@k: a gold family in the '
             'top k; recall@5: share of the (seen) gold families in the top 5; MRR: first gold family within the top 10.', '',
             '## Overall', '', table(R), '']
    if not all(beats.values()):
        lines += [f'**The full pipeline does not beat the popularity baseline on: '
                  f'{", ".join(mm for mm, b in beats.items() if not b)}.**', '']
    else:
        lines += ['The full pipeline beats the popularity baseline on every metric (point estimates).', '']
    lines += ['## By Category', '', table(R, 'Category'), '', '## By Conference', '', table(R, 'Conference'), '',
              '## By gold evidence', '', table(R, 'gold_evidence'), '', '## Margin gate (full pipeline)', '', gate_report(R), '']
    # examples
    F = full.merge(Q[['paper_key', 'query']], on='paper_key')
    hits, misses = F[F['hit@1'] == 1].sample(5, random_state=SEED), F[F['hit@5'] == 0].sample(5, random_state=SEED)
    lines += ['## Examples (full pipeline)', '']
    for lab, ex in (('HIT (gold family ranked 1st)', hits), ('MISS (no gold family in the top 5)', misses)):
        for _, r in ex.iterrows():
            top = r['top5'].split(';')[:3]
            sc = r['top3_scores'].split(';')
            lines += [f'- **{lab}** `{r.paper_key}` ({r.Category}, {r.Conference}), mapped={r.mapped}',
                      f'  - query: {r.query}',
                      '  - top 3: ' + '; '.join(f'{name(f)} ({s})' for f, s in zip(top, sc)),
                      '  - gold: ' + '; '.join(name(f) for f in r.seen_gold.split(';'))]
    (HERE / 'report_auto.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    sys.exit(main())
