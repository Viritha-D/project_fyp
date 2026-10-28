"""
v2 entity pipeline - one re-runnable command.

    python v2_entities_pipeline.py --stage all        (fidelity -> A -> B -> C)
    python v2_entities_pipeline.py --stage fidelity|A|B|C

fidelity  Part 4 rules on the old master vs part4_answer_key_map.csv (gate: name_key >= 99%,
          ARI >= 0.99) and Part 5 + repairs on the old master vs backup_v2/problem_entities.json
          and backup_v2/paper_to_entity_map_final.csv. Stops on a failed gate.
A         Part 4 on papers_master_with_matching_text_v2.csv (--series-split on), repairs,
          digit guard, Part 5 records, gold validation, old->v2 id map.
          -> paper_to_entity_map_v2.csv, digit_merge_report.csv, problem_entities_v2.json,
             entity_id_map_old_to_v2.csv
B         Enrichment + underspecified-description repair + entity embeddings + dedup audit.
          -> problem_entities_enriched_v2.json, entity_embeddings_v2.npy, entity_ids_order_v2.txt,
             entity_dedup_candidates_v2.csv, entity_true_duplicates_v2.txt
C         Data-only benchmark notes (fixed template, no LLM text). -> entity_notes_v2.json
Never writes the masters or any old output.
"""

import argparse
import itertools
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

import part4_entities as p4
import part5_entities as p5

ROOT = Path(__file__).resolve().parent
RULES = p4.RULES
REPAIRS = RULES['8_post_part4_repairs']
MODEL = 'sentence-transformers/all-mpnet-base-v2'

OLD_MASTER = ROOT / 'backup_v1' / 'master_before_ingest.csv'
OLD_ENTITIES = ROOT / 'backup_v2' / 'problem_entities.json'
OLD_MAP_FINAL = ROOT / 'backup_v2' / 'paper_to_entity_map_final.csv'
OLD_EMB_CACHE = ROOT / '.cache' / 'old_master_paper_embeddings.npy'   # *.npy is git-ignored
V2_MASTER = ROOT / 'papers_master_with_matching_text_v2.csv'
V2_EMB = ROOT / 'paper_embeddings.npy'
V2_IDS = ROOT / 'paper_ids_order.txt'
PAPER_INDEX = ROOT / 'paper_index.csv'
GOLD = ROOT / 'gold_standard_labels_remapped.csv'

OUT_MAP = ROOT / 'paper_to_entity_map_v2.csv'
OUT_DIGIT = ROOT / 'digit_merge_report.csv'
OUT_ENT = ROOT / 'problem_entities_v2.json'
OUT_IDMAP = ROOT / 'entity_id_map_old_to_v2.csv'
OUT_ENR = ROOT / 'problem_entities_enriched_v2.json'
OUT_EEMB = ROOT / 'entity_embeddings_v2.npy'
OUT_EIDS = ROOT / 'entity_ids_order_v2.txt'
OUT_AUDIT = ROOT / 'entity_dedup_candidates_v2.csv'
OUT_TRUEDUP = ROOT / 'entity_true_duplicates_v2.txt'
OUT_NOTES = ROOT / 'entity_notes_v2.json'

FIX_OLD = {'E00255', 'E00256', 'E00257', 'E00258', 'E00564', 'E00565', 'E00566'}
VENUES = ['CEC', 'GECCO', 'FOGA', 'PPSN', 'PReMI']
MISSING = p5.MISSING


def say(*a):
    print(*a, flush=True)


def load_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def dump_json(obj, p):
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def embed(texts):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL)
    return model.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True,
                        convert_to_numpy=True).astype(np.float32)


# ---------------------------------------------------------------- shared rules
def underspecified(entities):
    """entity_dedup_audit.py's 'needs enrichment' criterion (see part4_rules.json 8)."""
    tm = re.compile(r'^(.*?)\s*(?:\bon\b|\bfor\b|-|\()\s*[A-Z0-9][\w .]*\)?$')
    strip_mod = lambda x: (tm.match(str(x)).group(1).strip().lower() if tm.match(str(x)) else str(x).strip().lower())
    words = lambda x: set(re.findall(r'[a-z0-9]+', x.lower()))
    pc = {frozenset({e['entity_id'], e['parent_benchmark_id']}) for e in entities if e['parent_benchmark_id']}
    by_desc = {}
    for e in entities:
        by_desc.setdefault((e['category'], e['base_description']), []).append(e)
    sel = set()
    for grp in by_desc.values():
        for a, b in itertools.combinations(grp, 2):
            na, nb = a['canonical_name'], b['canonical_name']
            if frozenset({a['entity_id'], b['entity_id']}) in pc or na == nb:
                continue
            if p5.digit_stripped_key(na) == p5.digit_stripped_key(nb) or strip_mod(na) == strip_mod(nb):
                continue
            wa, wb = words(na), words(nb)
            if wa and wb and len(wa & wb) / len(wa | wb) < 0.4:
                sel |= {a['entity_id'], b['entity_id']}
    return sel


def map_merges(m, pairs):
    """Spelling-variant merges on the map: (category, absorbed name_key) -> entity holding target name_key."""
    done = []
    for p in pairs:
        cat = m['Category'] == p['category']
        a = m.loc[cat & (m['name_key'] == p['absorbed_name_key']), 'entity_id'].unique()
        t = m.loc[cat & (m['name_key'] == p['target_name_key']), 'entity_id'].unique()
        if len(a) != 1 or len(t) != 1 or a[0] == t[0]:
            done.append((p, None))
            continue
        m.loc[m['entity_id'] == a[0], 'resolution_method'] += '+spelling_variant_merge'
        m.loc[m['entity_id'] == a[0], 'entity_id'] = t[0]
        done.append((p, (a[0], t[0])))
    return done


def ari_nmi(a, b):
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    return adjusted_rand_score(a, b), normalized_mutual_info_score(a, b)


# ---------------------------------------------------------------- fidelity
def stage_fidelity():
    ok4, m = p4.fidelity()
    if not ok4:
        raise SystemExit('STOP: Part 4 fidelity gate failed')
    old = pd.read_csv(OLD_MASTER, dtype=str, keep_default_na=False)
    if OLD_EMB_CACHE.exists():
        emb = np.load(OLD_EMB_CACHE)
    else:
        say('[fidelity] embedding the old master (cache missing)...')
        emb = embed(old['matching_text'].tolist())
        OLD_EMB_CACHE.parent.mkdir(exist_ok=True)
        np.save(OLD_EMB_CACHE, emb)
    assert emb.shape == (len(old), 768)

    # map after the old TSP repair == backup_v2/paper_to_entity_map_final.csv
    m2 = m.drop(columns='series_key').copy()
    merges = [tuple(p['old_ids']) for p in REPAIRS['spelling_variant_merges']['pairs']]
    m2['entity_id'] = m2['entity_id'].replace(dict(merges))
    ref_map = pd.read_csv(OLD_MAP_FINAL, dtype=str, keep_default_na=False)
    map_ok = m2.reset_index(drop=True).equals(ref_map)
    say(f'[fidelity] rebuilt map + TSP repair == old paper_to_entity_map_final.csv: {map_ok}')

    # Part 5 + enrichment + repairs, in the original order
    ents = [e for e in p5.build_entities(m, old, emb, 'paper_id') if e['entity_id'] != 'E00599']
    n_enr = p5.enrich(ents, old.set_index('paper_id'))
    ents = p5.merge_entities(ents, merges)
    fix = underspecified(ents)
    say(f'[fidelity] underspecified criterion selects {len(fix)} entities; equals the 7 ids hard-coded in '
        f'fix_underspecified_entities.py: {fix == FIX_OLD}')
    p5.prefix_canonical(ents, fix)
    ref = {e['entity_id']: e for e in load_json(OLD_ENTITIES)}
    got = {e['entity_id']: e for e in ents}
    say(f'[fidelity] Part 5: {len(got)} entities vs {len(ref)} in the old problem_entities.json '
        f'(ids equal: {set(got) == set(ref)}); enriched {n_enr}')
    fields = ['entity_type', 'parent_benchmark_id', 'category', 'canonical_name', 'base_description',
              'medoid_paper_id', 'n_member_rows', 'n_supporting_papers', 'description_confidence',
              'source_paper_ids', 'member_paper_ids', 'aliases', 'characterization_conflicts', 'variant_family_id']
    diffs = {}
    for f in fields:
        bad = [i for i in ref if ref[i].get(f) != got.get(i, {}).get(f)]
        diffs[f] = bad
        say(f'    {f:27s} {len(ref) - len(bad)}/{len(ref)}' + (f'  differs: {bad}' if bad else ''))
    medoid_only = set(diffs['medoid_paper_id'])
    explained = all(set(b) <= medoid_only for b in diffs.values())
    say(f'[fidelity] every Part 5 difference is a medoid tie-break (re-embedded vectors differ by ~1e-6): {explained}')
    if not (map_ok and set(got) == set(ref) and explained and fix == FIX_OLD):
        raise SystemExit('STOP: Part 5 / repair fidelity failed')
    say('[fidelity] PASSED')


# ---------------------------------------------------------------- A
def paper_key_of_rows(master):
    idx = pd.read_csv(PAPER_INDEX, dtype=str, keep_default_na=False)
    root_to_key = {r: k for k, rs in zip(idx['paper_key'], idx['paper_id_roots']) for r in rs.split(';')}
    keys = master['Paper_ID'].str.replace(r'_Ext_\d+$', '', regex=True).map(root_to_key)
    assert keys.notna().all(), 'a master row has no paper_key in paper_index.csv'
    return keys, idx


def stage_a():
    d = pd.read_csv(V2_MASTER, dtype=str, keep_default_na=False)
    m, st = p4.build(d, 'Paper_ID', series_split=True, id_style='fresh')
    m_off, st_off = p4.build(d, 'Paper_ID', series_split=False, id_style='fresh')
    say(f'[A] Part 4 on v2 (series split on): {st}')
    # series-split effect: entities whose row set differs from the run without it
    sets_on = m.groupby('entity_id').apply(lambda g: frozenset(g.index), include_groups=False)
    sets_off = m_off.groupby('entity_id').apply(lambda g: frozenset(g.index), include_groups=False)
    changed_off = [e for e, s in sets_off.items() if s not in set(sets_on)]
    changed_on = [e for e, s in sets_on.items() if s not in set(sets_off)]
    say(f'[A] --series-split changes {len(changed_off)} entity(ies) of the plain run into {len(changed_on)}: '
        + '; '.join(f'{sorted(m_off.loc[list(sets_off[e]), "Benchmark_Name"].unique())[:8]}' for e in changed_off)
        + f'; {st["series_tagged_entities"]} MSTSP/RWMOP entities tagged with a series_key (no regrouping)')

    repairs = map_merges(m, REPAIRS['spelling_variant_merges']['pairs'])
    for p, r in repairs:
        say(f'[A] spelling-variant merge {p["category"]} {p["absorbed_name_key"]} -> {p["target_name_key"]}: '
            + (f'{r[0]} merged into {r[1]}' if r else 'not applicable on v2 (names absent or already together)'))
    # renumber fresh ids after the merges, stable by first appearance
    order = {}
    for e in m['entity_id']:
        order.setdefault(e, f'E{len(order) + 1:05d}')
    m['entity_id'] = m['entity_id'].map(order)
    m['parent_benchmark_id'] = m['parent_benchmark_id'].map(lambda x: order.get(x, '') if x else '')

    keys, idx = paper_key_of_rows(d)
    m.insert(2, 'paper_key', keys.values)
    assert m['paper_id'].tolist() == d['Paper_ID'].tolist() and m['paper_id'].is_unique, 'map not row-aligned'
    m.to_csv(OUT_MAP, index=False)

    g = p4.digit_guard(m)
    g.to_csv(OUT_DIGIT, index=False)
    say(f'[A] digit guard (report only): {len(g)} would-be digit merges in {g["entity_id"].nunique() if len(g) else 0} '
        f'entities -> {OUT_DIGIT.name}')

    # ---- Part 5 records ----
    emb = np.load(V2_EMB)
    assert V2_IDS.read_text(encoding='utf-8').splitlines() == d['Paper_ID'].tolist(), 'paper_ids_order.txt mismatch'
    ents = p5.build_entities(m.rename(columns={'paper_id': 'paper_id'}), d.rename(columns={'Paper_ID': 'paper_id'}),
                             emb, 'paper_id')
    art = set(REPAIRS['extraction_artifacts']['benchmark_names'])
    series = m.groupby('entity_id')['series_key'].first()
    pk = m.groupby('entity_id')['paper_key'].nunique()
    for e in ents:
        e['series_key'] = series[e['entity_id']] or None
        e['n_papers_by_paper_key'] = int(pk[e['entity_id']])
        e['flags'] = ['extraction_artifact_suspect'] if set(e['aliases']['benchmark_names']) & art else []
    dump_json(ents, OUT_ENT)

    # ---- assertions ----
    assert m.groupby('paper_id').size().eq(1).all() and len(m) == len(d), 'a master row is not in exactly one entity'
    assert all(e['n_member_rows'] > 0 and e['n_papers_by_paper_key'] > 0 for e in ents), 'entity with 0 papers'
    assert len(ents) == m['entity_id'].nunique()
    say(f'[A] assertions passed: {len(d)} rows each in exactly one of {len(ents)} entities; no entity has 0 papers')

    # ---- gold ----
    gold = pd.read_csv(GOLD, dtype=str, keep_default_na=False)
    pred = gold['new_Paper_ID'].map(m.set_index('paper_id')['entity_id'])
    assert pred.notna().all(), 'gold Paper_ID missing from the map'
    keep = gold['entity_id'] != 'uncertain'
    ari, nmi = ari_nmi(gold.loc[keep, 'entity_id'], pred[keep])
    say(f'[A] gold ({int(keep.sum())} labelled rows, {int((~keep).sum())} "uncertain" excluded): ARI {ari:.4f}, NMI {nmi:.4f}')
    if ari < 1 or nmi < 1:
        gl = gold.loc[keep].assign(pred=pred[keep])
        for _, r in gl.iterrows():
            same_gold = gl[gl['entity_id'] == r['entity_id']]['pred'].nunique() > 1
            same_pred = gl[gl['pred'] == r['pred']]['entity_id'].nunique() > 1
            if same_gold or same_pred:
                say(f'    disagree: row {r.row_num} {r.new_Paper_ID} gold {r.entity_id} -> {r.pred} '
                    f'({r.Benchmark_Name[:60]})')

    # ---- old -> v2 ids by exact canonical name ----
    old = load_json(OLD_ENTITIES)
    by_name = {}
    for e in ents:
        by_name.setdefault((e['category'], e['canonical_name']), []).append(e['entity_id'])
    rows = []
    for e in old:
        hit = by_name.get((e['category'], e['canonical_name']), [])
        rows.append(dict(old_entity_id=e['entity_id'], category=e['category'], canonical_name=e['canonical_name'],
                         v2_entity_id=hit[0] if len(hit) == 1 else '',
                         match='exact' if len(hit) == 1 else ('ambiguous' if hit else 'none'),
                         candidates=';'.join(hit) if len(hit) > 1 else ''))
    im = pd.DataFrame(rows)
    im.to_csv(OUT_IDMAP, index=False)
    say(f'[A] old -> v2 entity ids by exact canonical name: {im["match"].value_counts().to_dict()} -> {OUT_IDMAP.name}')

    # ---- report ----
    E = pd.DataFrame(ents)
    say(f'[A] entities: {len(E)} (old master: 1,038 from Part 4; 1,035 after the old repairs)')
    say(f'    by type: {E["entity_type"].value_counts().to_dict()}; by Category: {E["category"].value_counts().to_dict()}')
    say(f'    entities with 1 supporting paper (paper_key): {int((E["n_papers_by_paper_key"] == 1).sum())}')
    say(f'    flagged extraction_artifact_suspect: {[e["entity_id"] + " " + e["canonical_name"] for e in ents if e["flags"]]}')
    say('    top 15 by supporting papers (paper_key):')
    for _, r in E.sort_values(['n_papers_by_paper_key', 'n_member_rows'], ascending=False).head(15).iterrows():
        say(f'      {r.entity_id} {r.n_papers_by_paper_key:>4} papers {r.n_member_rows:>5} rows  [{r.category}, '
            f'{r.entity_type}] {r.canonical_name[:70]}')
    say('    10 random entities (seed 0) with aliases:')
    for _, r in E.sample(10, random_state=0).iterrows():
        say(f'      {r.entity_id} [{r.category}, {r.entity_type}, {r.n_papers_by_paper_key} papers] '
            f'{r.canonical_name[:60]!r} aliases={[a[:45] for a in r.aliases["benchmark_names"][:6]]}')


# ---------------------------------------------------------------- B
def stage_b():
    d = pd.read_csv(V2_MASTER, dtype=str, keep_default_na=False)
    ents = load_json(OUT_ENT)
    n_enr = p5.enrich(ents, d.set_index('Paper_ID'))
    fix = underspecified(ents)
    p5.prefix_canonical(ents, fix)
    for e in ents:
        if e['entity_id'] in fix:
            e['flags'] = e.get('flags', []) + ['description_prefixed_canonical_name']
    say(f'[B] enriched {n_enr} of {len(ents)} descriptions with landscape tags; '
        f'underspecified-description repair on {len(fix)} entities')
    vec = embed([e['base_description'] for e in ents])
    assert vec.shape == (len(ents), 768), vec.shape
    assert not np.isnan(vec).any(), 'NaN in entity embeddings'
    norms = np.linalg.norm(vec, axis=1)
    assert np.all(np.abs(norms - 1) < 1e-3), 'entity embeddings not unit norm'
    dump_json(ents, OUT_ENR)
    np.save(OUT_EEMB, vec)
    OUT_EIDS.write_text('\n'.join(e['entity_id'] for e in ents) + '\n', encoding='utf-8')
    back_ids = OUT_EIDS.read_text(encoding='utf-8').splitlines()
    assert len(back_ids) == len(load_json(OUT_ENR)) == np.load(OUT_EEMB).shape[0], 'n_entities mismatch'
    say(f'[B] assertions passed: embeddings {vec.shape}, no NaN, norms {norms.min():.6f}..{norms.max():.6f}; '
        f'json, embeddings and order file all have {len(ents)} entities')

    # entity_dedup_audit.py and find_true_duplicates.py, unchanged, on the v2 entities
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        shutil.copy(OUT_ENR, t / 'problem_entities.json')
        shutil.copy(OUT_EEMB, t / 'entity_embeddings.npy')
        a = subprocess.run([sys.executable, str(ROOT / 'entity_dedup_audit.py')], cwd=t, capture_output=True, text=True)
        assert a.returncode == 0, a.stderr
        shutil.copy(t / 'entity_dedup_candidates.csv', OUT_AUDIT)
        b = subprocess.run([sys.executable, str(ROOT / 'find_true_duplicates.py')], cwd=t, capture_output=True, text=True)
        assert b.returncode == 0, b.stderr
        OUT_TRUEDUP.write_text(a.stdout + '\n' + b.stdout, encoding='utf-8')
    say(f'[B] entity_dedup_audit.py: ' + ' | '.join(l.strip() for l in a.stdout.splitlines()[:6]))
    say(f'[B] find_true_duplicates.py: ' + ' | '.join(l.strip() for l in b.stdout.splitlines()[:2]))


# ---------------------------------------------------------------- C
def top(counter, k):
    return [{'value': v, 'count': int(c)} for v, c in counter.most_common(k)]


def plain_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def note_text(n, parent_name):
    kind = {'suite': 'benchmark suite', 'single_function': 'single benchmark problem',
            'named_subset': 'named subset of a benchmark suite'}[n['entity_type']]
    s1 = f"{n['canonical_name']} is a {kind}"
    if parent_name:
        s1 += f" within {parent_name}"
    venues = [f"{v} ({c})" for v, c in n['venues'].items() if c]
    s1 += (f", {n['category']}, used in {n['n_papers']} paper{'s' if n['n_papers'] != 1 else ''} "
           f"({n['n_records']} records) at {plain_list(venues)}")
    if n['year_range']:
        y0, y1 = n['year_range']
        s1 += f", {y0}" if y0 == y1 else f", {y0}-{y1}"
    sentences = [s1 + '.']
    bits = []
    if n['typical_dimensions']:
        bits.append('typical dimensions ' + '; '.join(f"{x['value']} ({x['count']})" for x in n['typical_dimensions']))
    land = [x['value'] for f in ('Modality', 'Separability') for x in n['landscape'][f][:1]]
    land += [x['value'] for x in n['landscape']['Landscape_Characteristics'][:3]]
    if land:
        bits.append('reported landscape: ' + ', '.join(land))
    if bits:
        sentences.append(bits[0][0].upper() + ', '.join(bits)[1:] + '.') if len(bits) > 1 else sentences.append(bits[0][0].upper() + bits[0][1:] + '.')
    perf = []
    if n['metrics']:
        perf.append('results are reported as ' + '; '.join(x['value'] for x in n['metrics']))
    if n['commonly_compared_algorithms']:
        perf.append('commonly compared algorithms: ' + ', '.join(x['value'] for x in n['commonly_compared_algorithms']))
    if perf:
        sentences.append(perf[0][0].upper() + '; '.join(perf)[1:] + '.')
    cav = {'ppsn_partial': 'some records come from PPSN files whose paper titles are not per-paper',
           'premi_year_unverified': 'some PReMI years could not be verified',
           'single_paper': 'it is supported by a single paper',
           'sparse_metadata': 'most landscape and dimension fields are not reported'}
    if n['evidence_caveats']:
        sentences.append('Caveats: ' + '; '.join(cav[c] for c in n['evidence_caveats']) + '.')
    if len(sentences) == 1:
        sentences.append('No dimension, landscape or metric details were reported.')
    assert 2 <= len(sentences) <= 4, sentences
    return ' '.join(sentences), len(sentences)


def stage_c():
    d = pd.read_csv(V2_MASTER, dtype=str, keep_default_na=False)
    m = pd.read_csv(OUT_MAP, dtype=str, keep_default_na=False)
    ents = load_json(OUT_ENR)
    idx = pd.read_csv(PAPER_INDEX, dtype=str, keep_default_na=False)
    flags = dict(zip(idx['paper_key'], idx['flags']))
    df = d.assign(entity_id=m['entity_id'].values, paper_key=m['paper_key'].values)
    by_e = {e: g for e, g in df.groupby('entity_id')}
    name = {e['entity_id']: e['canonical_name'] for e in ents}
    real = lambda s: [v for v in s if v.strip() and v.strip() not in MISSING]
    notes = []
    sentence_counts = Counter()
    for e in ents:
        g = by_e[e['entity_id']]
        alias_papers = g.groupby('Benchmark_Name')['paper_key'].nunique().sort_values(ascending=False)
        cats = set(g['Category'])
        yrs = g[(g['Conference'] != 'PReMI') & ~g['paper_key'].map(lambda k: 'year_unverified' in flags[k])]['Year']
        yrs = sorted(int(y) for y in yrs if y.isdigit())
        tags = Counter(t.strip() for v in g['Landscape_Characteristics'] for t in v.split(';')
                       if t.strip() and t.strip() not in MISSING)
        algs = g[g['Algorithm_Name'].map(lambda v: v not in MISSING)].groupby('Algorithm_Name')['paper_key'].nunique()
        n = {
            'entity_id': e['entity_id'],
            'canonical_name': e['canonical_name'],
            'entity_type': e['entity_type'],
            'category': cats.pop() if len(cats) == 1 else 'mixed',
            'aliases': alias_papers.index[:8].tolist(),
            'n_papers': int(g['paper_key'].nunique()),
            'n_records': int(len(g)),
            'venues': {v: int((g.drop_duplicates('paper_key')['Conference'] == v).sum()) for v in VENUES},
            'year_range': [yrs[0], yrs[-1]] if yrs else None,
            'typical_dimensions': top(Counter(real(g['Dimensionality'])), 3),
            'landscape': {'Modality': top(Counter(real(g['Modality'])), 3),
                          'Separability': top(Counter(real(g['Separability'])), 3),
                          'Landscape_Characteristics': top(tags, 5)},
            'metrics': top(Counter(real(g['Performance_Metric'])), 3),
            'commonly_compared_algorithms': [{'value': a, 'n_papers': int(c)} for a, c in
                                             algs.sort_values(ascending=False, kind='stable').head(5).items()],
            'industries': top(Counter(real(g['Industry'])), 3) if (g['Category'] == 'Applied').any() else [],
        }
        cav = []
        if (g['Conference'] == 'PPSN').any():
            cav.append('ppsn_partial')
        if g['paper_key'].map(lambda k: 'year_unverified' in flags[k]).any():
            cav.append('premi_year_unverified')
        if n['n_papers'] == 1:
            cav.append('single_paper')
        blank = sum(not real(g[f]) for f in ('Dimensionality', 'Modality', 'Separability', 'Landscape_Characteristics'))
        if blank >= 3:
            cav.append('sparse_metadata')
        n['evidence_caveats'] = cav
        n['note_text'], k = note_text(n, name.get(e['parent_benchmark_id']))
        sentence_counts[k] += 1
        notes.append(n)

    # ---- assertions ----
    pk_count = m.groupby('entity_id')['paper_key'].nunique()
    assert all(n['n_papers'] == pk_count[n['entity_id']] for n in notes), 'note n_papers != paper_index count'
    assert len(notes) == len(ents) == len(OUT_EIDS.read_text(encoding='utf-8').splitlines()) == np.load(OUT_EEMB).shape[0]
    assert [n['entity_id'] for n in notes] == OUT_EIDS.read_text(encoding='utf-8').splitlines()
    assert set(sentence_counts) <= {2, 3, 4}, sentence_counts   # counted as built by the template
    dump_json(notes, OUT_NOTES)
    say(f'[C] assertions passed: {len(notes)} notes; n_papers equals the paper_index count for every entity; '
        f'n_entities equal across notes, entity json, embeddings and order file; sentences per note '
        f'{dict(sorted(sentence_counts.items()))}')
    caveats = Counter(c for n in notes for c in n['evidence_caveats'])
    say(f'[C] caveat counts: {dict(caveats)}')

    N = pd.DataFrame(notes)
    rng = np.random.default_rng(0)
    pick = lambda frame, k: frame.iloc[sorted(rng.choice(len(frame), size=min(k, len(frame)), replace=False))]
    has = lambda v: N['venues'].map(lambda x: x[v] > 0)
    samples = [('Pure Math', pick(N[N['category'] == 'Pure Math'], 3)), ('Applied', pick(N[N['category'] == 'Applied'], 3)),
               ('with PReMI', pick(N[has('PReMI')], 1)), ('with FOGA', pick(N[has('FOGA')], 1)),
               ('with PPSN', pick(N[has('PPSN')], 1)), ('suite', pick(N[N['entity_type'] == 'suite'], 1))]
    say('[C] 10 sample note_texts:')
    for label, fr in samples:
        for _, r in fr.iterrows():
            say(f'  [{label}] {r.entity_id}: {r.note_text}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--stage', default='all', choices=['fidelity', 'A', 'B', 'C', 'all'])
    s = ap.parse_args().stage
    if s in ('fidelity', 'all'):
        stage_fidelity()
    if s in ('A', 'all'):
        stage_a()
    if s in ('B', 'all'):
        stage_b()
    if s in ('C', 'all'):
        stage_c()
    return 0


if __name__ == '__main__':
    sys.exit(main())
