"""
Retrieval v2.1 (Part C) evaluation, following PREREGISTRATION.md exactly.

Usage: python retrieval_v2/evaluation/evaluate_v21.py [--seeds 42 43]
Outputs (retrieval_v2/evaluation/): results_v21_seed<S>.csv, candidates_v21_seed<S>.csv, folds_seed43.csv,
report_v21.md, and retrieval_v2/v21_model.json (deployment model, section 9).
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import evaluate as ev  # noqa: E402
import hybrid  # noqa: E402
import v21  # noqa: E402

ROOT = hybrid.ROOT
SYSTEMS = ['popularity', 'bm25_only', 'dense_only', 'full_v2', 'popularity_clean', 'paper_knn', 'stacked']
METRICS = ev.METRICS


def make_folds(rows, k, seed):
    from sklearn.model_selection import StratifiedKFold
    p = rows.groupby('paper_key').agg(Category=('Category', lambda s: s.value_counts().index[0]),
                                      Conference=('Conference', 'first')).reset_index()
    p['stratum'] = p['Category'] + '|' + p['Conference']
    small = p['stratum'].value_counts()
    p.loc[p['stratum'].map(small) < k, 'stratum'] = 'rare'
    p['fold'] = -1
    for i, (_, test) in enumerate(StratifiedKFold(k, shuffle=True, random_state=seed).split(p, p['stratum'])):
        p.loc[test, 'fold'] = i
    return p


def fold_index(seed, fold, held, rows):
    if seed == 42:
        return ev.fold_index(fold, held, rows, False)       # the cached Part B builds
    out = ev.CACHE / f'seed{seed}' / f'fold{fold}'
    out.mkdir(parents=True, exist_ok=True)
    text = '\n'.join(sorted(held)) + '\n'
    digest = hashlib.sha256(text.encode()).hexdigest()
    stamp = out / 'build.sha256'
    if not stamp.exists() or stamp.read_text().strip() != digest or not (out / 'entity_embeddings.npy').exists():
        (out / 'heldout_paper_keys.txt').write_text(text, encoding='utf-8')
        r = subprocess.run([sys.executable, str(ROOT / 'v2_entities_pipeline.py'), '--hold-out',
                            str(out / 'heldout_paper_keys.txt'), '--out-dir', str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        stamp.write_text(digest)
    train = rows[~rows['paper_key'].isin(held)]
    return hybrid.Index.from_holdout(out, train), train


def run_seed(seed, rows, aliases, fams, emb_all, exclude, qtext, qvec):
    fam_kind = {f: x['family_kind'] for f, x in fams.items()}
    papers = make_folds(rows, 5, seed)
    if seed == 42:
        old = pd.read_csv(HERE / 'folds.csv', dtype={'fold': int}, keep_default_na=False)
        assert dict(zip(old.paper_key, old.fold)) == dict(zip(papers.paper_key, papers.fold)), 'seed-42 folds differ'
    else:
        papers.to_csv(HERE / f'folds_seed{seed}.csv', index=False)
    by_paper = {k: g for k, g in rows.groupby('paper_key')}
    gold_all = {k: set(g['family_id']) for k, g in by_paper.items()}
    info = papers.set_index('paper_key')
    results, cand_rows, qmeta, kinfo, unseen = [], [], [], [], []
    for fold in range(5):
        held = set(papers.loc[papers.fold == fold, 'paper_key'])
        idx, train = fold_index(seed, fold, held, rows)
        clean = v21.clean_index(idx, train, exclude)
        knn = v21.PaperKNN(emb_all, train, exclude)
        train_keys = set(train['paper_key'])
        clean_gold = {k: set(g.loc[~g['entity_id'].isin(exclude), 'family_id']) for k, g in by_paper.items()}
        K, kmeans, n_inner = v21.choose_k(knn, train_keys, papers, qvec, clean_gold, seed)
        kinfo.append({'seed': seed, 'fold': fold, 'K': K, 'n_inner_queries': n_inner,
                      **{f'inner_hit@5_K{k}': round(v, 4) for k, v in kmeans.items()}})
        seen_fams = set(idx.fam.values())
        qs, gs, meta = [], [], []
        for pk in sorted(held):
            seen = gold_all[pk] & seen_fams
            rec = {'seed': seed, 'paper_key': pk, 'fold': fold, 'Category': info.loc[pk, 'Category'],
                   'Conference': info.loc[pk, 'Conference'], 'seen_gold': ';'.join(sorted(seen)),
                   'n_entities': by_paper[pk]['entity_id'].nunique(),
                   'gold_evidence': ('gold family >= 2 training papers'
                                     if any(idx.fam_papers.get(f, 0) >= 2 for f in seen) else 'gold families < 2 training papers')}
            if seen:
                qs.append(qtext[pk]); gs.append(seen); meta.append(rec)
            else:
                unseen.append(rec)
        # Part B systems, unchanged
        partb = ev.run_systems(idx, qs, gs)
        # v2.1
        V = np.stack([qvec[m['paper_key']] for m in meta])
        PS = knn.paper_sims(V)
        votes = [knn.votes(PS[i], K) for i in range(len(meta))]
        cands, full21 = v21.candidate_features(clean, qs, V, votes, fam_kind)
        pop_clean = v21.popularity_order(clean)
        for i, (m, g) in enumerate(zip(meta, gs)):
            qmeta.append({**m, 'gold': g, 'knn_rank': v21.ranked_votes(votes[i]), 'pop_clean': pop_clean[:10],
                          'full21': full21[i], 'n_cands': len(cands[i]),
                          'only_excluded_gold': all(f not in set(clean.fam.values()) for f in g)})
            for s in partb[i * 4:(i + 1) * 4]:
                name = 'full_v2' if s['system'] == 'full' else s['system']
                results.append({**{k: m[k] for k in ('seed', 'paper_key', 'fold', 'Category', 'Conference', 'gold_evidence')},
                                **{k: s[k] for k in METRICS}, 'system': name, 'top5': s['top5']})
            for c in cands[i]:
                cand_rows.append({'seed': seed, 'fold': fold, 'paper_key': m['paper_key'], 'family_id': c['family_id'],
                                  'in_shortlist': c['in_shortlist'], 'label': int(c['family_id'] in g),
                                  **{f: c[f] for f in v21.FEATURES}})
        print(f'seed {seed} fold {fold}: K={K} scored {len(qs)} unseen {len(held) - len(qs)}', flush=True)

    CR = pd.DataFrame(cand_rows)
    # cross-fitted stacker
    prob = pd.Series(np.nan, index=CR.index)
    cuts = {}
    for fold in range(5):
        tr, te = CR['fold'] != fold, CR['fold'] == fold
        st = v21.Stacker().fit(CR.loc[tr, v21.FEATURES], CR.loc[tr, 'label'])
        prob[te] = st.proba(CR.loc[te, v21.FEATURES])
        ptr = pd.Series(st.proba(CR.loc[tr, v21.FEATURES]), index=CR.index[tr])
        top1_tr = ptr.groupby(CR.loc[tr, 'paper_key']).max()
        cuts[fold] = (float(top1_tr.quantile(1 / 3)), float(top1_tr.quantile(2 / 3)))
    CR['prob'] = prob
    by_q = {k: g.sort_values(['prob', 'family_id'], ascending=[False, True]) for k, g in CR.groupby('paper_key')}
    for m in qmeta:
        g = by_q[m['paper_key']]
        order = g['family_id'].tolist()
        stacked = order + [f for f in m['pop_clean'] if f not in order]
        p1 = float(g['prob'].iloc[0])
        c = cuts[m['fold']]
        base = {k: m[k] for k in ('seed', 'paper_key', 'fold', 'Category', 'Conference', 'gold_evidence')}
        for name, ids in (('popularity_clean', m['pop_clean']), ('paper_knn', m['knn_rank']), ('stacked', stacked),
                          ('two_slate', v21.two_slate(stacked, m['knn_rank'], fam_kind))):
            extra = {'top1_prob': p1, 'tier': v21.tier(p1, c)} if name == 'stacked' else {}
            results.append({**base, **ev.per_query(ids[:10], m['gold']), 'system': name, 'top5': ';'.join(ids[:5]), **extra})
    R = pd.DataFrame(results)
    R.to_csv(HERE / f'results_v21_seed{seed}.csv', index=False)
    CR.to_csv(HERE / f'candidates_v21_seed{seed}.csv', index=False)
    return R, CR, pd.DataFrame(qmeta), pd.DataFrame(unseen), pd.DataFrame(kinfo), cuts, papers


# ---------------------------------------------------------------- reporting
def md(df):
    cols = list(df.columns)
    return '\n'.join(['| ' + ' | '.join(map(str, cols)) + ' |', '|' + '---|' * len(cols)] +
                     ['| ' + ' | '.join(str(v) for v in r) + ' |' for r in df.itertuples(index=False)])


def table(R, by=None, systems=SYSTEMS):
    lines = ['| group | system | n | ' + ' | '.join(METRICS) + ' |', '|' + '---|' * (len(METRICS) + 3)]
    groups = [('all', R)] if by is None else [(str(k), g) for k, g in R.groupby(by)]
    for name, g in groups:
        for s in systems:
            x = g[g['system'] == s]
            if len(x):
                lines.append(f'| {name} | {s} | {len(x)} | ' + ' | '.join(ev.fmt(ev.boot(x[mm])) for mm in METRICS) + ' |')
    return '\n'.join(lines)


def paired(R, a, b, metric='hit@5', mask=None):
    A = R[R.system == a].set_index('paper_key')[metric]
    B = R[R.system == b].set_index('paper_key')[metric]
    if mask is not None:
        A, B = A[mask(A.index)], B[mask(B.index)]
    return ev.boot((A - B.loc[A.index]).values)


def criterion(R):
    cat = R[R.system == 'stacked'].set_index('paper_key')['Category']
    out = {}
    for ref in ('popularity', 'popularity_clean'):
        d_all = paired(R, 'stacked', ref)
        d_pm = paired(R, 'stacked', ref, mask=lambda ix: cat.loc[ix].values == 'Pure Math')
        d_ap = paired(R, 'stacked', ref, mask=lambda ix: cat.loc[ix].values == 'Applied')
        out[ref] = {'overall': d_all, 'Pure Math': d_pm, 'Applied': d_ap,
                    'a': d_all[2] >= 0, 'b': d_pm[2] >= 0, 'c': d_ap[1] > 0}
    return out


def reliability(R):
    x = R[R.system == 'stacked']
    lines = ['| tier | n | mean predicted p(top-1 gold) | hit@1 |', '|---|---|---|---|']
    for t in ('low', 'medium', 'high'):
        s = x[x.tier == t]
        lines.append(f'| {t} | {len(s)} | {s.top1_prob.mean():.3f} | {ev.fmt(ev.boot(s["hit@1"]))} |')
    from scipy.stats import spearmanr
    lines.append(f'\nSpearman(top-1 probability, hit@1) = {spearmanr(x.top1_prob, x["hit@1"]).correlation:.3f}; '
                 f'Brier score = {((x.top1_prob - x["hit@1"]) ** 2).mean():.3f}')
    return '\n'.join(lines)


def unseen_report(U, Q, papers, rows, fams, R):
    allp = pd.concat([U.assign(seen=False), Q[U.columns.intersection(Q.columns)].assign(seen=True)], ignore_index=True)
    allp['entities'] = pd.cut(allp['n_entities'], [0, 1, 2, 5, 10 ** 6], labels=['1', '2', '3-5', '>=6'])
    fam_np = {f: x['n_papers'] for f, x in fams.items()}
    gold = rows.groupby('paper_key')['family_id'].apply(set)
    U = U.assign(all_single=U.paper_key.map(lambda k: all(fam_np[f] <= 1 for f in gold[k])))
    lines = [f'Unseen papers: {len(U)} of {len(allp)}. Of these, {int(U.all_single.sum())} '
             f'({U.all_single.mean():.1%}) have only gold families with a single paper in the whole data '
             '(no split can make them seen).', '']
    hit5 = {s: R[R.system == s].set_index('paper_key')['hit@5'] for s in SYSTEMS}
    for by in ('Category', 'Conference', 'entities'):
        lines += [f'| {by} | papers | unseen | unseen share | oracle hit@5 | ' + ' | '.join(f'{s} hit@5 (all papers)' for s in ('popularity', 'full_v2', 'paper_knn', 'stacked')) + ' |',
                  '|' + '---|' * 9]
        for k, g in allp.groupby(by, observed=True):
            n = len(g)
            cells = [f'{hit5[s].reindex(g.paper_key).fillna(0).sum() / n:.3f}' for s in ('popularity', 'full_v2', 'paper_knn', 'stacked')]
            lines.append(f'| {k} | {n} | {int((~g.seen).sum())} | {(~g.seen).mean():.3f} | {g.seen.mean():.3f} | ' + ' | '.join(cells) + ' |')
        lines.append('')
    n = len(allp)
    cells = [f'{hit5[s].sum() / n:.3f}' for s in ('popularity', 'full_v2', 'paper_knn', 'stacked')]
    lines.append(f'All papers: oracle hit@5 = {allp.seen.mean():.3f}; hit@5 over all papers (unseen = miss): '
                 + ', '.join(f'{s} {c}' for s, c in zip(('popularity', 'full_v2', 'paper_knn', 'stacked'), cells)))
    return '\n'.join(lines)


def deployment(rows, emb_all, exclude, qvec, CR42, papers42):
    clean_gold = {k: set(g.loc[~g['entity_id'].isin(exclude), 'family_id']) for k, g in rows.groupby('paper_key')}
    knn = v21.PaperKNN(emb_all, rows, exclude)
    K, kmeans, _ = v21.choose_k(knn, set(rows['paper_key']), papers42, qvec, clean_gold, 42, n_inner=5)
    st = v21.Stacker().fit(CR42[v21.FEATURES], CR42['label'])
    top1 = pd.Series(st.proba(CR42[v21.FEATURES])).groupby(CR42['paper_key'].values).max()
    m = {'_about': 'Retrieval v2.1 deployment model (PREREGISTRATION.md section 9).', 'K': K,
         'inner_cv_hit@5': kmeans, 'knn_candidates': v21.KNN_CANDIDATES, 'stacker': st.export(),
         'tier_cuts': [float(top1.quantile(1 / 3)), float(top1.quantile(2 / 3))],
         'excluded_entities': sorted(exclude)}
    (ROOT / 'retrieval_v2' / 'v21_model.json').write_text(json.dumps(m, indent=1), encoding='utf-8')
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, nargs='+', default=[42, 43])
    a = ap.parse_args()
    rows, aliases, fams = ev.load()
    exclude = v21.excluded_entities()
    emb_all = np.load(hybrid.path('paper_embeddings.npy'))
    assert emb_all.shape[0] == len(rows)
    qtext = {k: ev.build_query(g, aliases) for k, g in rows.groupby('paper_key')}
    keys = sorted(qtext)
    qvec = dict(zip(keys, hybrid.encode_queries([qtext[k] for k in keys])))
    out = {s: run_seed(s, rows, aliases, fams, emb_all, exclude, qtext, qvec) for s in a.seeds}
    n_ex_rows = int(rows['entity_id'].isin(exclude).sum())
    L = ['# Retrieval v2.1 (Part C): evaluation', '',
         'Pre-registered in `PREREGISTRATION.md` (committed before this run). Nothing below was tuned on these results.', '',
         f'## 1. Index hygiene', '',
         f'Excluded entities: {len(exclude)} ({", ".join(sorted(exclude))}); records: {n_ex_rows}. Kept in the data.', '']
    for s, (R, CR, Q, U, KI, cuts, papers) in out.items():
        L += [f'Seed {s}: scored queries whose only seen gold families are excluded: {int(Q.only_excluded_gold.sum())}.']
    L.append('')
    for s, (R, CR, Q, U, KI, cuts, papers) in out.items():
        L += [f'## Seed {s}', '',
              f'Papers {len(papers)}; scored {R[R.system == "stacked"].shape[0]}; unseen {len(U)}.', '',
              '### K chosen by inner CV (paper-kNN)', '', md(KI), '',
              f'Stacker: {len(v21.FEATURES)} features ({", ".join(v21.FEATURES)}); candidates per query: '
              f'median {int(Q.n_cands.median())}, candidate rows {len(CR)}, positives {int(CR.label.sum())}; '
              f'queries with a gold family among the candidates: {CR.groupby("paper_key").label.max().mean():.3f}. '
              'Trained by cross-fitting (stacking, not strict nesting).', '',
              '### Overall', '', table(R), '', '### By Category', '', table(R, 'Category'), '',
              '### By Conference', '', table(R, 'Conference'), '', '### By gold evidence', '', table(R, 'gold_evidence'), '',
              '### Reliability (stacked, top-1 probability tiers; cut-offs from training folds)', '',
              'Cut-offs per fold: ' + '; '.join(f'fold {f}: {c[0]:.3f} / {c[1]:.3f}' for f, c in cuts.items()), '',
              reliability(R), '']
    L += ['## Pre-registered success criterion', '',
          'd = hit@5(stacked) - hit@5(reference), paired bootstrap 95% interval. (a) overall upper >= 0; '
          '(b) Pure Math upper >= 0; (c) Applied lower > 0; required on both seeds.', '',
          '| seed | reference | overall d | Pure Math d | Applied d | (a) | (b) | (c) |', '|---|---|---|---|---|---|---|---|']
    met_all = True
    for s, (R, *_rest) in out.items():
        for ref, c in criterion(R).items():
            L.append(f'| {s} | {ref} | {ev.fmt(c["overall"])} | {ev.fmt(c["Pure Math"])} | {ev.fmt(c["Applied"])} | '
                     f'{c["a"]} | {c["b"]} | {c["c"]} |')
            if ref == 'popularity':
                met_all &= c['a'] and c['b'] and c['c']
    L += ['', f'**Criterion (against the Part B popularity baseline, both seeds): {"MET" if met_all else "NOT MET"}.**', '']
    R42, CR42, Q42, U42, _, _, papers42 = out[a.seeds[0]]
    L += [f'## Unseen analysis (seed {a.seeds[0]})', '', unseen_report(U42, Q42, papers42, rows, fams, R42), '']
    L += ['## Two-slate output (3 standard + 2 specific) at k = 5', '',
          '| seed | best plain ranker | its hit@5 | two-slate hit@5 | d hit@5 | its recall@5 | two-slate recall@5 | d recall@5 |',
          '|---|---|---|---|---|---|---|---|']
    for s, (R, *_rest) in out.items():
        best = max(SYSTEMS, key=lambda x: R[R.system == x]['hit@5'].mean())
        b, t = R[R.system == best], R[R.system == 'two_slate']
        L.append(f'| {s} | {best} | {ev.fmt(ev.boot(b["hit@5"]))} | {ev.fmt(ev.boot(t["hit@5"]))} | '
                 f'{ev.fmt(paired(R, "two_slate", best))} | {ev.fmt(ev.boot(b["recall@5"]))} | '
                 f'{ev.fmt(ev.boot(t["recall@5"]))} | {ev.fmt(paired(R, "two_slate", best, "recall@5"))} |')
    if 42 in out:
        m = deployment(rows, emb_all, exclude, qvec, out[42][1], papers42)
        L += ['', f'## Deployment model', '', f'`retrieval_v2/v21_model.json`: K = {m["K"]} (inner CV on all papers: '
              f'{m["inner_cv_hit@5"]}), tier cut-offs {m["tier_cuts"]}, stacker coefficients (standardised): '
              + ', '.join(f'{f} {c:+.3f}' for f, c in zip(v21.FEATURES, m['stacker']['coef']))]
    (HERE / 'report_v21.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    sys.exit(main())
