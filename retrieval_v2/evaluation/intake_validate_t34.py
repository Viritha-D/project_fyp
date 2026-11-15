"""
Validation of query sets t3 and t4 (PREREGISTRATION_final_amendment3.md). No retrieval, no ranking, no scoring.

t3 (names-only): resolve_gold_names.py writes queries_t3_resolved.csv (amendment 2); each name is reported as
   matched, no match or ambiguous (with candidates).
t4 (ids + names): amendment 1 rule (a) id exists (case-insensitive), (b) not an excluded family, (c) written name equals
   stored name after NFKC / lower case / whitespace collapsing, and as many names as ids. As an information-only
   cross-check, resolve_gold_names.py is run on t4's names (a names-only copy in a temporary folder).
Both: whole-query validity, the 25% set rule, n_papers of each gold family, gold families under 2 papers, words per
   query, gold overlap with queries_v2 and t1, dense cosine (all-mpnet-base-v2) of the query texts against queries_v2,
   t1 and the other new set (flag >= 0.8, duplicate >= 0.95), and the corpus-closeness distribution: for t1, t3, t4
   and queries_v2, each query's maximum cosine with the matching_text of all 11,342 paper rows (the frozen
   paper_embeddings.npy, which embeds that text with the same model).
Nothing is repaired. Writes validation_t34.md, validation_t34_rows.csv, similarity_t34.csv, queries_t3_resolved.csv.

Usage: python retrieval_v2/evaluation/intake_validate_t34.py
"""

import csv
import difflib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXCLUDED = {'F02124': 'Not Reported', 'F00334': 'extraction_artifact_suspect (E00657)'}
spec = importlib.util.spec_from_file_location('resolver', HERE / 'resolve_gold_names.py')
resolver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolver)
rkey = resolver.key                                                  # casefold + whitespace collapse (amendment 2)


def norm_c(s):                                                      # amendment 1 rule (c) normalisation
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(s)).lower()).strip()


def split(s):
    return [x.strip() for x in str(s).split(';') if x.strip()]


def main():
    fams = {f['family_id']: f for f in json.loads((ROOT / 'families_v5.json').read_text(encoding='utf-8'))}
    upper = {f.upper(): f for f in fams}
    by_key = {}
    for f, x in fams.items():
        by_key.setdefault(rkey(x['family_name']), []).append(f)
    q2 = pd.read_csv(HERE / 'queries_v2.csv', dtype=str, keep_default_na=False)
    t1 = pd.read_csv(HERE / 'queries_t1.csv', dtype=str, keep_default_na=False)
    t3 = pd.read_csv(HERE / 'queries_t3.csv', dtype=str, keep_default_na=False)
    t4 = pd.read_csv(HERE / 'queries_t4.csv', dtype=str, keep_default_na=False)
    gold_q2 = {f for g in q2.gold_families for f in split(g)}
    gold_t1 = {f.upper() for g in t1.gold_families for f in split(g)}
    rows, qv = [], {}

    # ---------------- t3: official resolver run
    r = subprocess.run([sys.executable, str(HERE / 'resolve_gold_names.py'), str(HERE / 'queries_t3.xlsx'),
                        '--out', str(HERE / 'queries_t3_resolved.csv')], capture_output=True, text=True)
    assert r.returncode in (0, 1), r.stdout + r.stderr
    res3 = pd.read_csv(HERE / 'queries_t3_resolved.csv', dtype=str, keep_default_na=False)
    for _, q in t3.iterrows():
        names = [x.strip() for x in q.gold_family_names.split(';') if x.strip()]
        probs = []
        if not names:
            probs.append('no gold family names')
        for n in names:
            hits = by_key.get(rkey(n), [])
            d = {'set': 't3', 'query_id': q.query_id, 'name_as_written': n, 'id_as_written': '', 'resolution':
                 'match' if len(hits) == 1 else ('no match' if not hits else 'ambiguous'),
                 'family_id': hits[0] if len(hits) == 1 else '', 'stored_name': fams[hits[0]]['family_name'] if len(hits) == 1 else '',
                 'candidates': '; '.join(f'{i} ({fams[i]["family_name"]})' for i in hits) if len(hits) > 1 else
                               ('; '.join(f'{fams[i]["family_name"]} ({i})' for k in difflib.get_close_matches(rkey(n), list(by_key), n=3, cutoff=0.6) for i in by_key[k])
                                if not hits else ''),
                 'n_papers': fams[hits[0]]['n_papers'] if len(hits) == 1 else '', 'excluded': EXCLUDED.get(hits[0], '') if len(hits) == 1 else ''}
            if d['resolution'] != 'match':
                probs.append(f'{d["resolution"]}: "{n}"')
            elif d['excluded']:
                probs.append(f'excluded: "{n}" -> {hits[0]}')
            rows.append(d)
        valid = not probs
        official = res3.loc[res3.query_id == q.query_id, 'valid'].iloc[0] == 'True'
        assert valid == official, f't3 {q.query_id}: own check {valid} vs resolver {official}'
        for d in rows:
            if d['set'] == 't3' and d['query_id'] == q.query_id:
                d.update(row_valid=valid, row_problems=' | '.join(probs))
        if not names:
            rows.append({'set': 't3', 'query_id': q.query_id, 'name_as_written': '', 'resolution': 'no names', 'row_valid': False,
                         'row_problems': 'no gold family names'})

    # ---------------- t4: amendment 1 rule (a)-(c)
    for _, q in t4.iterrows():
        ids, names = split(q.gold_families), [x.strip() for x in q.gold_family_names.split(';')]
        probs, ds = [], []
        if len(ids) != len(names):
            probs.append(f'(c) {len(ids)} ids but {len(names)} names')
        for i, raw in enumerate(ids):
            wn = names[i] if i < len(names) else ''
            fid = upper.get(raw.upper())
            d = {'set': 't4', 'query_id': q.query_id, 'id_as_written': raw, 'name_as_written': wn, 'resolution': '',
                 'family_id': fid or '', 'stored_name': fams[fid]['family_name'] if fid else '(id does not exist)',
                 'n_papers': fams[fid]['n_papers'] if fid else '', 'excluded': EXCLUDED.get(fid, '') if fid else '',
                 'candidates': '; '.join(by_key.get(rkey(wn), []))}
            if fid is None:
                probs.append(f'(a) {raw} does not exist')
            else:
                if fid in EXCLUDED:
                    probs.append(f'(b) {raw} excluded')
                ok = norm_c(fams[fid]['family_name']) == norm_c(wn)
                d['name_similarity'] = round(difflib.SequenceMatcher(None, norm_c(fams[fid]['family_name']), norm_c(wn)).ratio(), 3)
                d['resolution'] = 'name matches id' if ok else 'name differs from stored name'
                if not ok:
                    probs.append(f'(c) {raw}: written "{wn}" vs stored "{fams[fid]["family_name"]}"')
            ds.append(d)
        for d in ds:
            d.update(row_valid=not probs, row_problems=' | '.join(probs))
        rows.extend(ds)
    V = pd.DataFrame(rows)
    V.to_csv(HERE / 'validation_t34_rows.csv', index=False)

    # ---------------- t4 names through the resolver (information only)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 't4_names_only.csv'
        t4[['query_id', 'query_text', 'gold_family_names', 'notes']].to_csv(p, index=False)
        subprocess.run([sys.executable, str(HERE / 'resolve_gold_names.py'), str(p), '--out', str(Path(td) / 'r.csv')],
                       capture_output=True, text=True)
        x4 = pd.read_csv(Path(td) / 'r.csv', dtype=str, keep_default_na=False)
    x4['agrees_with_written_ids'] = [v == 'True' and set(split(g)) == {i.upper() for i in split(w)}
                                     for v, g, w in zip(x4.valid, x4.gold_families, t4.gold_families)]

    # ---------------- per-set table
    def setinfo(name, df, qrows):
        qv_ = qrows.groupby('query_id', sort=False).agg(valid=('row_valid', 'first'))
        fam_ids = {f for f in qrows.family_id if f}
        w = df.query_text.str.split().str.len()
        inv = int((~qv_.valid.astype(bool)).sum())
        return {'set': name, 'rows': len(df), 'valid': len(df) - inv, 'invalid': inv, 'share': inv / len(df),
                'status': 'rejected' if inv / len(df) > 0.25 else 'accepted', 'fams': fam_ids,
                'lt2': sum(fams[f]['n_papers'] < 2 for f in fam_ids), 'in_q2': len(fam_ids & gold_q2), 'in_t1': len(fam_ids & gold_t1),
                'words': (w.mean(), w.median(), w.min(), w.max())}
    S = [setinfo('t3', t3, V[V.set == 't3']), setinfo('t4', t4, V[V.set == 't4'])]

    # ---------------- similarity + corpus closeness
    from sentence_transformers import SentenceTransformer
    import sentence_transformers, torch
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    enc = lambda t: model.encode(list(t), normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True).astype(np.float32)
    texts = {'queries_v2': q2, 't1': t1, 't3': t3, 't4': t4}
    E = {k: enc(v.query_text) for k, v in texts.items()}
    P = np.load(ROOT / 'paper_embeddings.npy')
    sims = []
    for s in ('t3', 't4'):
        for o in [x for x in ('queries_v2', 't1', 't3', 't4') if x != s]:
            C = E[s] @ E[o].T
            for i, qid in enumerate(texts[s].query_id):
                j = int(np.argmax(C[i]))
                sims.append((s, qid, o, texts[o].query_id.iloc[j], float(C[i, j]), texts[s].query_text.iloc[i], texts[o].query_text.iloc[j]))
    SM = pd.DataFrame(sims, columns=['set', 'query_id', 'against', 'match_id', 'cosine', 'text', 'match_text'])
    SM.to_csv(HERE / 'similarity_t34.csv', index=False)
    ident = [(a, b) for s, o in (('t3', 't4'), ('t3', 't1'), ('t4', 't1'), ('t3', 'queries_v2'), ('t4', 'queries_v2'))
             for a, ta in zip(texts[s].query_id, texts[s].query_text) for b, tb in zip(texts[o].query_id, texts[o].query_text)
             if norm_c(ta) == norm_c(tb)]
    within = {s: float(np.max(np.triu(E[s] @ E[s].T, 1))) for s in ('t3', 't4')}
    corpus = {k: (E[k] @ P.T).max(axis=1) for k in ('queries_v2', 't1', 't3', 't4')}

    # ---------------- report
    L = ['# Validation of query sets t3 and t4 (no scoring)', '',
         'Produced by `intake_validate_t34.py` under amendment 3. No retrieval, ranking or scoring was run. Gold checks use '
         'families_v5.json only (names resolved with resolve_gold_names.py for t3). Nothing was repaired.', '',
         '## Per-set validation', '',
         '| set | form | rows | valid | invalid | invalid share | status (25% rule) | distinct gold families (valid) | of which < 2 papers | also in queries_v2 gold | also in t1 gold | words per query mean / median / min / max |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for s, form in zip(S, ('names-only', 'ids + names')):
        w = s['words']
        L.append(f'| {s["set"]} | {form} | {s["rows"]} | {s["valid"]} | {s["invalid"]} | {s["share"]:.0%} | **{s["status"]}** | '
                 f'{len(s["fams"])} | {s["lt2"]} | {s["in_q2"]} | {s["in_t1"]} | {w[0]:.1f} / {w[1]:.0f} / {w[2]} / {w[3]} |')
    L += ['', '"distinct gold families (valid)" counts the families of names or ids that pass their own checks (matched names for '
          't3, existing ids with a matching name for t4), whether or not the whole query is valid.', '']
    L += ['## t3: resolution of every written name', '', '| query | name as written | result | family (id) | n_papers | candidates |',
          '|---|---|---|---|---|---|']
    for _, d in V[V.set == 't3'].iterrows():
        fam = f'{d.stored_name} ({d.family_id})' if d.get('family_id') else ''
        L.append(f'| {d.query_id} | {d.name_as_written} | {d.resolution} | {fam} | {d.n_papers} | {d.candidates if d.resolution != "match" else ""} |')
    L += ['', '(For "no match", the candidates are the closest names by string similarity, information only, never used. For '
          '"ambiguous", they are every family with that exact name.)', '',
          '## t4: rule (a)-(c) for every gold id', '', '| query | id as written | name as written | stored name for that id | result | n_papers | ids whose stored name equals the written name (information only) |',
          '|---|---|---|---|---|---|---|']
    for _, d in V[V.set == 't4'].iterrows():
        L.append(f'| {d.query_id} | {d.id_as_written} | {d.name_as_written} | {d.stored_name} | {d.resolution} | {d.n_papers} | {d.candidates or "-"} |')
    L += ['', '## Invalid queries', '']
    for s in ('t3', 't4'):
        bad = V[(V.set == s) & (~V.row_valid.astype(bool))].groupby('query_id', sort=False).row_problems.first()
        L.append(f'**{s}: {len(bad)} invalid**' + ('' if len(bad) else ' (none)'))
        L += [f'- {s}:{q}: {p}' for q, p in bad.items()]
        L.append('')
    agree = int(x4.agrees_with_written_ids.sum())
    L += ['## t4 names through resolve_gold_names.py (information only; does not decide validity)', '',
          f'{len(x4)} queries: {int((x4.valid == "True").sum())} resolve fully by name, and {agree} of these resolve to exactly '
          'the ids written in the file.', '']
    for _, x in x4[x4.valid != 'True'].iterrows():
        L.append(f'- {x.query_id}: {x.problems}')
    L += ['', '## Query similarity (dense cosine, all-mpnet-base-v2, query text only)', '',
          f'Identical texts (normalised) across t3, t4, t1, queries_v2: {len(ident)}' + (f' {ident}' if ident else '') + '.', '',
          '| set | against | best cosine >= 0.8 (flag) | >= 0.95 (duplicate) | max |', '|---|---|---|---|---|']
    for (s, o), g in SM.groupby(['set', 'against'], sort=False):
        L.append(f'| {s} | {o} | {int((g.cosine >= 0.8).sum())} | {int((g.cosine >= 0.95).sum())} | {g.cosine.max():.3f} |')
    L += ['', 'Within-set maximum cosine: ' + ', '.join(f'{s} {v:.3f}' for s, v in within.items()) + '.', '', 'Flags (>= 0.8):', '']
    fl = SM[SM.cosine >= 0.8].sort_values('cosine', ascending=False)
    L += [f'- {r.set}:{r.query_id} vs {r.against}:{r.match_id}, cosine {r.cosine:.3f}' + (' **DUPLICATE (>= 0.95)**' if r.cosine >= 0.95 else '')
          for r in fl.itertuples()] or ['- none']
    L += ['', 'Highest best-match per comparison:', '']
    for (s, o), g in SM.groupby(['set', 'against'], sort=False):
        r = g.sort_values('cosine', ascending=False).iloc[0]
        L.append(f'- {s}:{r.query_id} ↔ {o}:{r.match_id}, {r.cosine:.3f}: "{r.text[:100]}" ↔ "{r.match_text[:100]}"')
    L += ['', '## Corpus closeness (descriptive; amendment 3 s. 5)', '',
          "Each query's maximum cosine with the matching_text of all 11,342 paper rows (frozen `paper_embeddings.npy`). Queries "
          f'embedded with all-mpnet-base-v2 in this session (sentence-transformers {sentence_transformers.__version__}, torch '
          f'{torch.__version__}).', '',
          '| set | n | min | 25% | median | 75% | 90% | max | mean | share >= 0.7 | share >= 0.8 |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for k in ('queries_v2', 't1', 't3', 't4'):
        c = corpus[k]
        q = np.percentile(c, [0, 25, 50, 75, 90, 100])
        L.append(f'| {k} | {len(c)} | ' + ' | '.join(f'{v:.3f}' for v in q) + f' | {c.mean():.3f} | {(c >= 0.7).mean():.2f} | {(c >= 0.8).mean():.2f} |')
    (HERE / 'validation_t34.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    sys.exit(main())
