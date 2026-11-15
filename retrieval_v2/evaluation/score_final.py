"""
Final independent test: score the accepted sets once, as pre-registered (PREREGISTRATION_final.md, amendments 1-6).

Sets and validity
- Accepted: t1 (queries_t1.csv, ids + names), t3 (queries_t3_resolved.csv, ids resolved from names), t4 (queries_t4.csv).
  t2 is rejected (amendment 1). No t2b / t5 file exists.
- Only valid queries are used (whole-query rule). Ids are prefixed with the set (t1:Q01 ...).
- Duplicate rule (amendment 1): identical text or dense cosine >= 0.95 across sets -> keep the first by file order
  (t1, t3, t4); 0.8-0.95 flagged and kept.
- AI-use rule (amendments 3, 5): sets whose writer reports AI use for queries or family choice leave the primary set;
  formatting-only use does not exclude; sets with no statement stay in, flagged "provenance not stated". Statements
  are taken from PROVENANCE_t.md and are fixed below as PROVENANCE_STATUS (read and checked against the file).

Systems (published index, frozen models, batched path; ties by family id ascending)
- PRIMARY  stacked ranker v2.2 (lambda 1.0): recommend_v21.rank_batch order (candidates by probability, then hygiene
  popularity padding).
- SECONDARY full v2 (lambda 0) and blend 0.5: v22/blend.py over the full v2 shortlist roll-up and the stacked
  candidates, padded with hygiene popularity. popularity: Part B popularity of the published index.
- EXPLORATORY bm25_only, dense_only (Part B), paper_knn (kNN voted families).

Statistics
- Per-system metrics: means over queries with 95% bootstrap intervals (1,000 resamples, seed 42; PREREGISTRATION_final).
- Primary claim, blend decision and every paired comparison and sensitivity analysis: paired bootstrap, 10,000
  resamples, seed 42 (amendments 1 and 4).
- Error causes (a)/(b)/(c) for every system (amendment 2); groups; stacked confidence tiers (frozen cut-offs).
- Sensitivity (amendment 4): (a) per set, (b) leave one set out, (c) cluster bootstrap over connected components of
  queries sharing a gold family, (d) only sets with a qualifying statement. Leave-one-writer-out (amendment 5).

Outputs: scored_queries_final.csv, report_final.md, results_final.json.

Usage: python retrieval_v2/evaluation/score_final.py                 (the single real run)
       python retrieval_v2/evaluation/score_final.py --dry-run DIR   (pipeline test on queries_v2 only; writes to DIR)
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE), str(HERE.parent / 'v22')]
import blend as v22blend  # noqa: E402
import evaluate as ev  # noqa: E402
import hybrid  # noqa: E402
import recommend_v21 as r21  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
SET_ORDER = ['t1', 't3', 't4']
# Amendments 3 and 5 applied to PROVENANCE_t.md as recorded before the cut-off (checked in check_provenance()).
PROVENANCE_STATUS = {
    't1': {'statement': None, 'primary': True, 'flag': 'provenance not stated', 'qualifies_d': False, 'writer': 'Sanjesh Nandha'},
    't3': {'statement': None, 'primary': True, 'flag': 'provenance not stated', 'qualifies_d': False, 'writer': 'Adarsh Prakash'},
    't4': {'statement': 'relayed: Copilot used only for formatting; did not modify or edit anything', 'primary': True,
           'flag': 'statement relayed by the user (formatting-only AI use; does not exclude)', 'qualifies_d': True,
           'writer': 'Sanjesh Nandha K'},
}
WRITERS = {'Sanjesh Nandha': ['t1', 't4'], 'Adarsh Prakash': ['t3']}
SYSTEMS = ['stacked', 'popularity', 'full_v2_lambda0', 'blend_0.5', 'bm25_only', 'dense_only', 'paper_knn']
ROLE = {'stacked': 'PRIMARY', 'popularity': 'secondary', 'full_v2_lambda0': 'secondary', 'blend_0.5': 'secondary',
        'bm25_only': 'exploratory', 'dense_only': 'exploratory', 'paper_knn': 'exploratory'}
METRICS = ['hit@1', 'hit@3', 'hit@5', 'recall@5', 'mrr']
B_DESC, B_PAIRED, SEED = 1000, 10000, 42


def group_of(text):
    return re.sub(r'\([^)]*\)', '', str(text).split(';')[0]).strip() or '(no group)'


def split(s):
    return [x.strip() for x in str(s).split(';') if x.strip()]


# ---------------------------------------------------------------- inputs
def check_provenance():
    p = (HERE / 'PROVENANCE_t.md').read_text(encoding='utf-8')
    row = next(l for l in p.splitlines() if l.startswith('| AI statement'))
    cells = [c.strip() for c in row.strip('|').split('|')]
    assert cells[1] == 'not provided' and cells[3] == 'not provided', 't1/t3 AI statements changed: update PROVENANCE_STATUS'
    assert 'copilot was only used for formatting' in cells[4], 't4 statement changed: update PROVENANCE_STATUS'
    return cells


def load_test_sets():
    fams = {f['family_id'].upper(): f['family_id'] for f in json.loads((HERE.parent.parent / 'families_v5.json').read_text())}
    out = []
    t1 = pd.read_csv(HERE / 'queries_t1.csv', dtype=str, keep_default_na=False)
    for _, r in t1.iterrows():
        out.append(('t1', r.query_id, r.query_text, {fams[i] for i in split(r.gold_ids_norm)}, group_of(r.notes)))
    t3 = pd.read_csv(HERE / 'queries_t3_resolved.csv', dtype=str, keep_default_na=False)
    for _, r in t3[t3.valid == 'True'].iterrows():
        out.append(('t3', r.query_id, r.query_text, set(split(r.gold_families)), group_of(r.notes)))
    t4 = pd.read_csv(HERE / 'queries_t4.csv', dtype=str, keep_default_na=False)
    for _, r in t4.iterrows():
        out.append(('t4', r.query_id, r.query_text, {fams[i.upper()] for i in split(r.gold_families)}, r.group_norm))
    v = pd.read_csv(HERE / 'validation_t34_rows.csv', dtype=str, keep_default_na=False)
    assert (v.row_valid == 'True').all(), 'validation says some t3/t4 rows are invalid'
    return out


def load_dry_run():
    q = pd.read_csv(HERE / 'queries_v2.csv', dtype=str, keep_default_na=False).head(30)
    return [(['d1', 'd2', 'd3'][i // 10], r.query_id, r.query_text, set(split(r.gold_families)), group_of(r.notes))
            for i, (_, r) in enumerate(q.iterrows())]


def dedup(rows, encode):
    E = encode([r[2] for r in rows])
    C = E @ E.T
    keep, dropped, flagged = [], [], []
    for i, r in enumerate(rows):
        dup = next((j for j in keep if rows[j][0] != r[0] and (ev_norm(rows[j][2]) == ev_norm(r[2]) or C[i, j] >= 0.95)), None)
        if dup is not None:
            dropped.append((r[0] + ':' + r[1], rows[dup][0] + ':' + rows[dup][1], float(C[i, dup])))
            continue
        for j in keep:
            if rows[j][0] != r[0] and 0.8 <= C[i, j] < 0.95:
                flagged.append((rows[j][0] + ':' + rows[j][1], r[0] + ':' + r[1], float(C[i, j])))
        keep.append(i)
    cross = [float(C[i, j]) for i in range(len(rows)) for j in range(i) if rows[i][0] != rows[j][0]]
    return [rows[i] for i in keep], dropped, flagged, max(cross) if cross else float('nan')


def ev_norm(s):
    return re.sub(r'\s+', ' ', str(s).casefold()).strip()


# ---------------------------------------------------------------- scoring (once)
def score(rows):
    queries = [r[2] for r in rows]
    idx = hybrid.Index.from_config()
    rb = r21.rank_batch(queries)                                          # batched path
    st = r21._load()
    clean, pop_clean = st['clean'], st['pop']
    full = idx.rank_full(queries, np.stack([x['qvec'] for x in rb]))
    pop = [f['family_id'] for f in idx.rank_popularity()]
    out = []
    for r, x, fr in zip(rows, rb, full):
        f_list = [f['family_id'] for f in fr['families']]
        s_list = list(x['cands'])
        ranked = {
            'stacked': (x['order'], set(s_list)),
            'popularity': (pop[:10], set(pop)),
            'full_v2_lambda0': (v22blend.blend(f_list, s_list, 0.0, pop_clean), set(f_list)),
            'blend_0.5': (v22blend.blend(f_list, s_list, 0.5, pop_clean), set(f_list) | set(s_list)),
            'bm25_only': None, 'dense_only': None,
            'paper_knn': (x['knn_order'], set(x['knn_order'])),
        }
        bm = [f['family_id'] for f in idx.rank_bm25_only(r[2])]
        dn = [f['family_id'] for f in idx.rank_dense_only(x['qvec'])]
        ranked['bm25_only'] = (bm, set(bm))
        ranked['dense_only'] = (dn, set(dn))
        lt2_all = all(clean.fam_papers.get(g, 0) < 2 for g in r[3])
        lt2_any = any(clean.fam_papers.get(g, 0) < 2 for g in r[3])
        for s in SYSTEMS:
            lst, cands = ranked[s]
            m = ev.per_query(lst[:10], r[3])
            cause = ''
            if m['hit@5'] == 0:
                cause = 'b' if (r[3] & cands) else 'a'
            out.append({'set': r[0], 'query_id': f'{r[0]}:{r[1]}', 'group': r[4], 'system': s, 'role': ROLE[s],
                        'gold': ';'.join(sorted(r[3])), 'top5': ';'.join(lst[:5]), **m, 'miss_cause': cause,
                        'gold_all_lt2_papers': lt2_all, 'gold_any_lt2_papers': lt2_any,
                        'stacked_top1_prob': x['top1_prob'] if s == 'stacked' else '',
                        'stacked_tier': x['tier'] if s == 'stacked' else ''})
    return pd.DataFrame(out), {f: clean.fam_papers.get(f, 0) for f in {g for r in rows for g in r[3]}}


# ---------------------------------------------------------------- statistics
def boot_mean(v, B, seed=SEED):
    v = np.asarray(v, float)
    m = v[np.random.default_rng(seed).integers(0, len(v), (B, len(v)))].mean(1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def paired(R, a, b, metric, keys=None, B=B_PAIRED):
    A = R[R.system == a].set_index('query_id')[metric]
    Bv = R[R.system == b].set_index('query_id')[metric]
    if keys is not None:
        A, Bv = A.loc[keys], Bv.loc[keys]
    return boot_mean((A - Bv.loc[A.index]).values, B)


def components(R):
    g = R[R.system == 'stacked'][['query_id', 'gold']]
    parent = {q: q for q in g.query_id}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    owner = {}
    for q, gold in zip(g.query_id, g.gold):
        for f in split(gold):
            if f in owner:
                parent[find(q)] = find(owner[f])
            else:
                owner[f] = q
    comp = {}
    for q in g.query_id:
        comp.setdefault(find(q), []).append(q)
    return list(comp.values())


def cluster_paired(R, a, b, metric, comps, B=B_PAIRED):
    d = (R[R.system == a].set_index('query_id')[metric] - R[R.system == b].set_index('query_id')[metric])
    sums = np.array([d.loc[c].sum() for c in comps])
    sizes = np.array([len(c) for c in comps])
    idx = np.random.default_rng(SEED).integers(0, len(comps), (B, len(comps)))
    stats = sums[idx].sum(1) / sizes[idx].sum(1)
    return float(d.mean()), float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def f3(t):
    return f'{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]'


def m3(t):
    return f'{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]'


# ---------------------------------------------------------------- report
def report(R, meta, out_dir):
    n = R[R.system == 'stacked'].shape[0]
    L = ['# Final independent test', '', meta['header'], '']
    # composition
    S = R[R.system == 'stacked']
    L += ['## Pooled set', '', f"Pooled valid queries: **n = {n}**. Duplicates dropped (>= 0.95 or identical): "
          f"{len(meta['dropped'])}; flagged (0.8-0.95): {len(meta['flagged'])}; maximum cross-set cosine "
          f"{meta['max_cross']:.3f}.", '', '| set | queries | writer | provenance (amendments 3, 5) |', '|---|---|---|---|']
    for s, c in S.set.value_counts().reindex(sorted(S.set.unique())).items():
        p = meta['prov'].get(s, {})
        L.append(f"| {s} | {c} | {p.get('writer', '-')} | {p.get('flag', '-')} |")
    L += ['', '| group | queries |', '|---|---|'] + [f'| {g} | {c} |' for g, c in S.group.value_counts().items()] + ['']
    # main table
    L += ['## Results (pooled)', '', 'Means over queries, 95% bootstrap intervals (1,000 resamples, seed 42).', '',
          '| system | role | n | ' + ' | '.join(METRICS) + ' |', '|---|---|---|' + '---|' * len(METRICS)]
    res = {}
    for s in SYSTEMS:
        x = R[R.system == s]
        res[s] = {m: boot_mean(x[m], B_DESC) for m in METRICS}
        L.append(f'| {s} | {ROLE[s]} | {len(x)} | ' + ' | '.join(m3(res[s][m]) for m in METRICS) + ' |')
    # paired
    pc = {}
    L += ['', '## Paired comparisons (stacked minus other; paired bootstrap, 10,000 resamples, seed 42)', '',
          '| comparison | d hit@5 | d MRR |', '|---|---|---|']
    for o in ('popularity', 'full_v2_lambda0', 'blend_0.5'):
        pc[o] = {m: paired(R, 'stacked', o, m) for m in ('hit@5', 'mrr')}
        L.append(f"| stacked - {o} | {f3(pc[o]['hit@5'])} | {f3(pc[o]['mrr'])} |")
    # primary claim
    d = pc['popularity']['hit@5']
    supported = d[1] > 0
    width = d[2] - d[1]
    verdict = 'SUPPORTED' if supported else ('NOT SUPPORTED' + (' (inconclusive at this size; fewer than 40 queries)' if n < 40 else ''))
    comps = components(R)
    cl = cluster_paired(R, 'stacked', 'popularity', 'hit@5', comps)
    disagree = (cl[1] > 0) != supported
    L += ['', '## Primary confirmatory claim', '',
          f"Paired difference in hit@5, stacked ranker v2.2 minus popularity, pooled valid queries: **{f3(d)}**, "
          f"n = {n}, interval width {width:.3f} (paired bootstrap, 10,000 resamples, seed 42). Lower bound "
          f"{'above' if supported else 'not above'} 0: **{verdict}**."
          + (f" The cluster bootstrap over {len(comps)} groups of queries sharing a gold family (sensitivity (c)) gives "
             f"{f3(cl)}, which {'DISAGREES' if disagree else 'agrees'} with this conclusion"
             + (' (its lower bound is on the other side of 0)' if disagree else '') + '.'), '']
    # blend decision
    bd = paired(R, 'blend_0.5', 'stacked', 'mrr')
    replace = bd[1] > 0
    L += ['## Blend decision (MRR)', '',
          f"Paired MRR advantage of blend 0.5 over the primary: {f3(bd)} (10,000 resamples, seed 42). The interval is "
          f"{'entirely above 0' if replace else 'not entirely above 0'}: **{'blend 0.5 replaces the primary' if replace else 'the primary (stacked ranker v2.2) stays'}**. "
          'This choice was made after seeing the test.', '']
    # error causes
    L += ['## Error causes for every system (queries with no gold family in the top 5)', '',
          '| system | misses | (a) no gold among candidates | (b) gold among candidates, below rank 5 | (c) every gold family < 2 papers | at least one gold family < 2 papers |',
          '|---|---|---|---|---|---|']
    for s in SYSTEMS:
        x = R[(R.system == s) & (R['hit@5'] == 0)]
        L.append(f"| {s} | {len(x)} | {int((x.miss_cause == 'a').sum())} | {int((x.miss_cause == 'b').sum())} | "
                 f"{int(x.gold_all_lt2_papers.astype(bool).sum())} | {int(x.gold_any_lt2_papers.astype(bool).sum())} |")
    L += ['', 'For popularity the candidates are all families, so (a) cannot occur.', '']
    # groups
    L += ['## By group (hit@5 and MRR, 1,000 resamples)', '', '| group | n | ' + ' | '.join(f'{s} hit@5' for s in SYSTEMS[:4]) + ' | stacked MRR |',
          '|---|---|' + '---|' * 5]
    for g, x in R.groupby('group'):
        k = x[x.system == 'stacked'].shape[0]
        L.append(f'| {g} | {k} | ' + ' | '.join(m3(boot_mean(x[x.system == s]['hit@5'], B_DESC)) for s in SYSTEMS[:4])
                 + f" | {m3(boot_mean(x[x.system == 'stacked']['mrr'], B_DESC))} |")
    # tiers
    L += ['', '## Stacked confidence tiers (frozen cut-offs 0.0723 / 0.1372)', '', '| tier | n | mean top-1 probability | hit@1 |', '|---|---|---|---|']
    for t in ('low', 'medium', 'high'):
        x = S[S.stacked_tier == t]
        L.append(f'| {t} | {len(x)} | ' + (f'{x.stacked_top1_prob.astype(float).mean():.3f} | {m3(boot_mean(x["hit@1"], B_DESC))}' if len(x) else '- | -') + ' |')
    # sensitivity
    def block(keys, label):
        cells = []
        for o in ('popularity', 'full_v2_lambda0', 'blend_0.5'):
            cells += [f3(paired(R, 'stacked', o, 'hit@5', keys)), f3(paired(R, 'stacked', o, 'mrr', keys))]
        return f'| {label} | {len(keys)} | ' + ' | '.join(cells) + ' |'
    head = ('| analysis | n | vs popularity d hit@5 | d MRR | vs full v2 d hit@5 | d MRR | vs blend 0.5 d hit@5 | d MRR |',
            '|---|---|---|---|---|---|---|---|')
    sets = sorted(S.set.unique())
    L += ['', '## Sensitivity analyses (amendment 4; descriptive, not decisive; paired bootstrap, 10,000 resamples)', '',
          *head]
    L.append(block(list(S.query_id), 'primary (pooled)'))
    for s in sets:
        L.append(block(list(S[S.set == s].query_id), f'(a) {s} only'))
    for s in sets:
        L.append(block(list(S[S.set != s].query_id), f'(b) without {s}'))
    qual = [s for s in sets if meta['prov'].get(s, {}).get('qualifies_d')]
    dkeys = list(S[S.set.isin(qual)].query_id)
    cl_rows = []
    for o in ('popularity', 'full_v2_lambda0', 'blend_0.5'):
        cl_rows += [f3(cluster_paired(R, 'stacked', o, 'hit@5', comps)), f3(cluster_paired(R, 'stacked', o, 'mrr', comps))]
    L.append(f'| (c) cluster bootstrap, {len(comps)} components | {len(S)} | ' + ' | '.join(cl_rows) + ' |')
    L.append(block(dkeys, f"(d) only sets with a qualifying statement ({', '.join(qual)})") if dkeys
             else '| (d) | 0 | not computable: no set has a qualifying statement | | | | | |')
    for w, ws in meta['writers'].items():
        keys = list(S[~S.set.isin(ws)].query_id)
        if keys:
            L.append(block(keys, f'leave out writer {w} ({", ".join(ws)}) (amendment 5)'))
    sizes = sorted((len(c) for c in comps), reverse=True)
    L += ['', f'Components for (c): {len(comps)}; largest sizes {sizes[:5]}; singletons {sizes.count(1)}.', '']
    # gold-family facts for the limitations
    fp = meta['fam_papers']
    L += ['## Gold families', '', f"Distinct gold families in the pooled set: {len(fp)}; with fewer than 2 papers in the "
          f"index: {sum(v < 2 for v in fp.values())} ({sum(v < 2 for v in fp.values()) / max(len(fp), 1):.0%}). Gold "
          f"families shared between sets: {meta['shared']}.", '']
    (out_dir / 'report_final.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    summary = {'n': n, 'primary': {'d_hit5': d, 'width': width, 'supported': supported, 'verdict': verdict},
               'cluster_c': {'d_hit5': cl, 'disagrees': disagree, 'components': len(comps)},
               'blend_decision': {'d_mrr_blend_minus_stacked': bd, 'replace': replace},
               'metrics': {s: {m: list(v) for m, v in res[s].items()} for s in SYSTEMS},
               'paired': {o: {m: list(v) for m, v in pc[o].items()} for o in pc}, 'run': meta['header']}
    (out_dir / 'results_final.json').write_text(json.dumps(summary, indent=1) + '\n', encoding='utf-8')
    print('\n'.join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', metavar='DIR')
    a = ap.parse_args()
    start = datetime.now(IST)
    if a.dry_run:
        out_dir = Path(a.dry_run)
        rows, prov = load_dry_run(), {s: {'writer': 'dry run', 'flag': 'dry run', 'qualifies_d': s == 'd3'} for s in ('d1', 'd2', 'd3')}
        writers = {'dry-writer': ['d1', 'd3']}
    else:
        out_dir = HERE
        check_provenance()
        rows, prov, writers = load_test_sets(), PROVENANCE_STATUS, WRITERS
        assert not any((HERE / f).exists() for f in ('scored_queries_final.csv', 'report_final.md')), 'already scored once'
    kept, dropped, flagged, max_cross = dedup(rows, hybrid.encode_queries)
    R, fam_papers = score(kept)
    R.to_csv(out_dir / 'scored_queries_final.csv', index=False)
    S = R[R.system == 'stacked']
    by_set = {s: {g for x in S[S.set == s].gold for g in split(x)} for s in S.set.unique()}
    shared = {f'{a}&{b}': len(by_set[a] & by_set[b]) for i, a in enumerate(sorted(by_set)) for b in sorted(by_set)[i + 1:]}
    header = (f"Scoring run started {start.strftime('%Y-%m-%d %H:%M:%S')} IST (cut-off 12 November 2026, 10:00 IST, amendment 6). "
              f"{'DRY RUN on queries_v2 (pipeline test only).' if a.dry_run else 'Single scoring run on t1, t3, t4.'} "
              'Frozen system tag retrieval-v2.2; environment FROZEN_ENV.txt; batched path; ties by family id ascending.')
    report(R, {'header': header, 'dropped': dropped, 'flagged': flagged, 'max_cross': max_cross, 'prov': prov,
               'writers': writers, 'fam_papers': fam_papers, 'shared': shared}, out_dir)


if __name__ == '__main__':
    sys.exit(main())
