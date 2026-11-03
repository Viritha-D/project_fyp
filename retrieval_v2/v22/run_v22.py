"""
Retrieval v2.2 experiment, as pre-registered in PREREGISTRATION_v22.md.

A. Diagnostics (demo queries; cause-(b) misses of queries_v2).  B. lambda curves of the blend on queries_v2 and
on the five-fold automatic evaluation (seeds 42, 43), the fixed selection rule, and the tier hit@1 for the chosen
lambda. The frozen v2.1 model is only read.

Outputs (retrieval_v2/v22/): report_v22.md, results_v22_queries_v2.csv, results_v22_seed42.csv,
results_v22_seed43.csv, v22_selection.json.

Usage: python retrieval_v2/v22/run_v22.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RV2 = HERE.parent
sys.path[:0] = [str(HERE), str(RV2), str(RV2 / 'evaluation')]
import blend as bl  # noqa: E402
import evaluate as ev  # noqa: E402
import evaluate_v21 as e21  # noqa: E402
import hybrid  # noqa: E402
import recommend_v21 as r21  # noqa: E402
import v21  # noqa: E402

EVAL = RV2 / 'evaluation'
GYM = ['F00431', 'F00924', 'F01314', 'F01404', 'F01522', 'F01839']
WALKER = ['F01054', 'F01298', 'F01600', 'F01601']
ONEMAX = ['F00445', 'F00455']


def metrics_rows(name, ids_list, golds, keys, extra=None):
    out = []
    for i, (ids, g, k) in enumerate(zip(ids_list, golds, keys)):
        out.append({'key': k, 'system': name, **ev.per_query(ids[:10], g), 'top5': ';'.join(ids[:5]),
                    **({} if extra is None else extra[i])})
    return out


def curve_table(R, label):
    lines = []
    for s in R['system'].unique():
        x = R[R.system == s]
        lines.append(f'| {label} | {s} | {len(x)} | ' + ' | '.join(ev.fmt(ev.boot(x[m])) for m in ev.METRICS) + ' |')
    return lines


# ---------------------------------------------------------------- automatic evaluation
def automatic(seed, rows, aliases, qtext, qvec, exclude):
    papers = e21.make_folds(rows, 5, seed)
    old = pd.read_csv(EVAL / f'results_v21_seed{seed}.csv', keep_default_na=False)
    CR = pd.read_csv(EVAL / f'candidates_v21_seed{seed}.csv', keep_default_na=False)
    stacked_list = {k: g.sort_values(['prob', 'family_id'], ascending=[False, True])['family_id'].tolist()
                    for k, g in CR.groupby('paper_key')}
    by_paper = {k: g for k, g in rows.groupby('paper_key')}
    out, checks = [], {'full_v2_top5_equal': 0, 'stacked_top5_equal': 0, 'n': 0}
    for fold in range(5):
        held = set(papers.loc[papers.fold == fold, 'paper_key'])
        idx, train = e21.fold_index(seed, fold, held, rows)
        pop = v21.popularity_order(v21.clean_index(idx, train, exclude))
        seen_f = set(idx.fam.values())
        keys = [k for k in sorted(held) if set(by_paper[k]['family_id']) & seen_f]
        golds = [set(by_paper[k]['family_id']) & seen_f for k in keys]
        full = idx.rank_full([qtext[k] for k in keys], np.stack([qvec[k] for k in keys]))
        rf = [[f['family_id'] for f in r['families']] for r in full]
        rs = [stacked_list[k] for k in keys]
        o = old.set_index(['paper_key', 'system'])
        for k, a, b in zip(keys, rf, rs):
            checks['n'] += 1
            checks['full_v2_top5_equal'] += ';'.join(a[:5]) == o.loc[(k, 'full_v2'), 'top5']
            checks['stacked_top5_equal'] += ';'.join(bl.blend(a, b, 1.0, pop)[:5]) == o.loc[(k, 'stacked'), 'top5']
        meta = [{'fold': fold} for _ in keys]
        out += metrics_rows('full_v2 (reference)', rf, golds, keys, meta)
        for lam in bl.LAMBDAS:
            out += metrics_rows(f'blend lambda={lam}', [bl.blend(a, b, lam, pop) for a, b in zip(rf, rs)], golds, keys, meta)
        print(f'seed {seed} fold {fold}: {len(keys)} queries', flush=True)
    R = pd.DataFrame(out)
    ref = old[old.system.isin(['popularity', 'stacked'])].rename(columns={'paper_key': 'key'})
    ref = ref.assign(system=ref.system.map({'popularity': 'popularity (reference)', 'stacked': 'stacked v2.1 (reference)'}))
    tiers = old[old.system == 'stacked'].set_index('paper_key')['tier']
    R = pd.concat([ref[['key', 'system'] + ev.METRICS + ['top5']], R], ignore_index=True)
    R['tier'] = R['key'].map(tiers)
    R.to_csv(HERE / f'results_v22_seed{seed}.csv', index=False)
    return R, checks


# ---------------------------------------------------------------- queries_v2 and diagnostics
def published(queries):
    idx = hybrid.Index.from_config()
    qv = hybrid.encode_queries(queries)
    full = idx.rank_full(queries, qv)
    rb = r21.rank_batch(queries)
    st = r21._load()
    return idx, qv, full, rb, st


def queries_v2():
    Q = pd.read_csv(EVAL / 'queries_v2.csv', dtype=str, keep_default_na=False)
    golds = [{f.strip() for f in g.split(';') if f.strip()} for g in Q.gold_families]
    idx, qv, full, rb, st = published(Q.query_text.tolist())
    rf = [[f['family_id'] for f in r['families']] for r in full]
    rs = [list(r['cands'].keys()) for r in rb]
    old = pd.read_csv(EVAL / 'results_queries_v2.csv', keep_default_na=False).set_index(['query_id', 'system'])
    checks = {'n': len(Q),
              'full_v2_top5_equal': sum(';'.join(a[:5]) == old.loc[(k, 'full_v2'), 'top5'] for k, a in zip(Q.query_id, rf)),
              'stacked_top5_equal': sum(';'.join(bl.blend(a, b, 1.0, st['pop'])[:5]) == old.loc[(k, 'stacked'), 'top5']
                                        for k, a, b in zip(Q.query_id, rf, rs))}
    keys = Q.query_id.tolist()
    out = metrics_rows('popularity (reference)', [[f['family_id'] for f in idx.rank_popularity()[:10]]] * len(Q), golds, keys)
    out += metrics_rows('full_v2 (reference)', rf, golds, keys)
    out += metrics_rows('stacked v2.1 (reference)', [r['order'] for r in rb], golds, keys)
    for lam in bl.LAMBDAS:
        out += metrics_rows(f'blend lambda={lam}', [bl.blend(a, b, lam, st['pop']) for a, b in zip(rf, rs)], golds, keys)
    R = pd.DataFrame(out)
    R.to_csv(HERE / 'results_v22_queries_v2.csv', index=False)
    return Q, golds, R, checks, (idx, rf, rs, rb, st)


def rank_in(lst, f):
    return lst.index(f) + 1 if f in lst else None


def fmt_rank(r, padding=False):
    return 'not a candidate' if r is None else (f'{r} (padding)' if padding else str(r))


def diagnostics(Q, golds, ctx):
    idx, rf, rs, rb, st = ctx
    fams = st['fams']
    nm = lambda f: fams[f]['family_name']
    npap = st['clean'].fam_papers
    demo = [l[3:].strip() for l in (RV2 / 'demo_outputs.md').read_text(encoding='utf-8').splitlines() if l.startswith('## ')]
    assert len(demo) == 7
    didx, dqv, dfull, drb, _ = published(demo)
    pop = [f['family_id'] for f in idx.rank_popularity()]
    L = ['## A1. Demo queries', '']
    for i, q in enumerate(demo):
        lists = {'popularity': pop,
                 'bm25_only': [f['family_id'] for f in didx.rank_bm25_only(q)],
                 'dense_only': [f['family_id'] for f in didx.rank_dense_only(dqv[i])],
                 'full_v2': [f['family_id'] for f in dfull[i]['families']],
                 'paper_knn': drb[i]['knn_order'],
                 'stacked': drb[i]['order']}
        cands = drb[i]['cands']
        expected = ONEMAX if '(1+1) EA' in q else (GYM + WALKER if 'neuroevolution' in q.lower() else None)
        L += [f'**{q}**', '']
        if expected:
            L += ['| family | n_papers | ' + ' | '.join(lists) + ' |', '|' + '---|' * (len(lists) + 2)]
            for f in expected:
                cells = []
                for s, lst in lists.items():
                    r = rank_in(lst, f)
                    cells.append(fmt_rank(r, padding=(s == 'stacked' and r is not None and f not in cands)))
                L.append(f'| {f} {nm(f)} | {npap.get(f, 0)} | ' + ' | '.join(cells) + ' |')
        else:
            L += ['| rank | full_v2 | stacked |', '|---|---|---|']
            for r in range(5):
                a, b = lists['full_v2'], lists['stacked']
                L.append(f'| {r + 1} | {nm(a[r]) if r < len(a) else "-"} | {nm(b[r]) if r < len(b) else "-"} |')
        L.append('')
    # A2
    old = pd.read_csv(EVAL / 'results_queries_v2.csv', keep_default_na=False)
    so = old[old.system == 'stacked'].set_index('query_id')
    miss_b = [k for k in Q.query_id if so.loc[k, 'hit@5'] == 0 and str(so.loc[k, 'gold_in_candidates']) == 'True']
    pos = {k: i for i, k in enumerate(Q.query_id)}
    L += ['## A2. Cause-(b) misses in queries_v2', '', f'{len(miss_b)} queries.', '',
          '| query | gold family | n_papers | rank full_v2 | rank stacked |', '|---|---|---|---|---|']
    for k in miss_b:
        i = pos[k]
        for f in sorted(golds[i]):
            L.append(f'| {k} | {nm(f)} | {npap.get(f, 0)} | {fmt_rank(rank_in(rf[i], f))} | '
                     f'{fmt_rank(rank_in(rb[i]["order"], f), padding=f not in rb[i]["cands"] and f in rb[i]["order"])} |')
    mean5 = lambda lists, ix: np.mean([npap.get(f, 0) for i in ix for f in lists[i][:5]])
    ix_b, ix_all = [pos[k] for k in miss_b], list(range(len(Q)))
    so_lists = [r['order'] for r in rb]
    L += ['', '| mean n_papers of the top-5 families | stacked | full_v2 |', '|---|---|---|',
          f'| the {len(miss_b)} cause-(b) misses | {mean5(so_lists, ix_b):.1f} | {mean5(rf, ix_b):.1f} |',
          f'| all {len(Q)} queries | {mean5(so_lists, ix_all):.1f} | {mean5(rf, ix_all):.1f} |', '']
    return L


# ---------------------------------------------------------------- main
def main():
    rows, aliases, _ = ev.load()
    exclude = v21.excluded_entities()
    Q, golds, RQ, cq, ctx = queries_v2()
    diag = diagnostics(Q, golds, ctx)
    qtext = {k: ev.build_query(g, aliases) for k, g in rows.groupby('paper_key')}
    keys = sorted(qtext)
    qvec = dict(zip(keys, hybrid.encode_queries([qtext[k] for k in keys])))
    auto = {s: automatic(s, rows, aliases, qtext, qvec, exclude) for s in (42, 43)}
    # selection
    pop5 = {s: auto[s][0].loc[auto[s][0].system == 'popularity (reference)', 'hit@5'].mean() for s in auto}
    sel = []
    for lam in bl.LAMBDAS:
        name = f'blend lambda={lam}'
        h5 = {s: auto[s][0].loc[auto[s][0].system == name, 'hit@5'].mean() for s in auto}
        sel.append({'lambda': lam, 'auto_hit5_seed42': h5[42], 'auto_hit5_seed43': h5[43],
                    'eligible': all(h5[s] >= pop5[s] for s in auto),
                    'queries_v2_mrr': RQ.loc[RQ.system == name, 'mrr'].mean()})
    S = pd.DataFrame(sel)
    el = S[S.eligible]
    chosen = 1.0 if el.empty else float(el.sort_values(['queries_v2_mrr', 'lambda'], ascending=[False, True]).iloc[0]['lambda'])
    # tier hit@1 for the chosen lambda (automatic, seeds pooled)
    T = pd.concat([auto[s][0][auto[s][0].system == f'blend lambda={chosen}'] for s in auto])
    tier_hit1 = {t: float(T.loc[T.tier == t, 'hit@1'].mean()) for t in ('low', 'medium', 'high')}
    tier_n = {t: int((T.tier == t).sum()) for t in tier_hit1}
    selection = {'_about': 'Retrieval v2.2 selection (PREREGISTRATION_v22.md). queries_v2 is a selection set for this lambda.',
                 'lambda': chosen, 'popularity_auto_hit5': pop5, 'candidates': sel, 'no_eligible_lambda': bool(el.empty),
                 'tier_hit1_pooled_auto': tier_hit1, 'tier_n_pooled_auto': tier_n,
                 'tier_one_in_n': {t: (round(1 / h) if h > 0 else None) for t, h in tier_hit1.items()}}
    (HERE / 'v22_selection.json').write_text(json.dumps(selection, indent=1), encoding='utf-8')
    # report
    head = '| data | system | n | ' + ' | '.join(ev.METRICS) + ' |'
    L = ['# Retrieval v2.2 experiment: report', '', 'Pre-registered in `PREREGISTRATION_v22.md` (71e6287). Frozen v2.1 '
         'model only read. **queries_v2 is the selection set for lambda; its numbers for the chosen lambda are optimistic.**', '',
         *diag, '## B1. Blend curves (score = (1-lambda)/(60+rank_full) + lambda/(60+rank_stacked))', '',
         'Reproduction checks (top-5 identical to the earlier results files): '
         + '; '.join(f'{lab}: full_v2 {c["full_v2_top5_equal"]}/{c["n"]}, lambda=1 vs stacked {c["stacked_top5_equal"]}/{c["n"]}'
                     for lab, c in (('queries_v2', cq), ('seed 42', auto[42][1]), ('seed 43', auto[43][1]))), '',
         head, '|' + '---|' * (len(ev.METRICS) + 3)]
    L += curve_table(RQ, 'queries_v2 (55)')
    for s in (42, 43):
        L += curve_table(auto[s][0], f'auto seed {s} ({auto[s][0][auto[s][0].system == "blend lambda=1.0"].shape[0]})')
    L += ['', '## B2. Selection', '', f'Popularity automatic hit@5: seed 42 {pop5[42]:.3f}, seed 43 {pop5[43]:.3f}.', '',
          '| lambda | auto hit@5 seed 42 | auto hit@5 seed 43 | eligible | queries_v2 MRR |', '|---|---|---|---|---|']
    L += [f'| {r["lambda"]} | {r["auto_hit5_seed42"]:.3f} | {r["auto_hit5_seed43"]:.3f} | {r["eligible"]} | {r["queries_v2_mrr"]:.3f} |'
          for r in sel]
    L += ['', f'**Chosen lambda = {chosen}**' + (' (no eligible lambda; v2.1 kept)' if el.empty else '') + '.', '',
          f'Tier hit@1 of the blended top-1 (lambda = {chosen}, automatic evaluation, seeds pooled): '
          + ', '.join(f'{t} {tier_hit1[t]:.3f} (n {tier_n[t]}, about 1 in {selection["tier_one_in_n"][t]})' for t in tier_hit1), '']
    (HERE / 'report_v22.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    sys.exit(main())
