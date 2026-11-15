"""
Benchmark recommender demo (Streamlit).

Modes
- live (local, run_demo.sh sets DEMO_MODE=live): runs the product system v2.3 = blend 0.5
  (retrieval_v2/recommend_v23.py, local tag retrieval-v2.3-blend; a thin wrapper over the frozen code) on the typed
  description.
- precomputed (default; Streamlit Community Cloud): shows the gallery of real, unedited outputs from app/gallery.json.
  Live retrieval (all-mpnet-base-v2 + cross-encoder + torch) does not reliably fit the cloud resource limits, and a
  lighter model would be a different system, so the cloud app does not run it.

Every reliability number shown is read from app/site_data.json (generated from retrieval_v2/RESULTS.md by
app/tools/site_stats.py); none is typed here.
"""

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

import core

APP = Path(__file__).resolve().parent
MODE = 'live' if os.environ.get('DEMO_MODE', '').lower() == 'live' else 'precomputed'
SITE = json.loads((APP / 'site_data.json').read_text(encoding='utf-8'))
GALLERY = json.loads((APP / 'gallery.json').read_text(encoding='utf-8'))
DEMO = json.loads((APP / 'demo_inputs.json').read_text(encoding='utf-8'))
TIERS = SITE['tiers_seed42']
CAT = SITE['by_category_seed42']
APPLIED_LIMIT = 0.60

st.set_page_config(page_title='Benchmark recommender', page_icon='📊', layout='wide')


# ---------------------------------------------------------------- rendering
def band_line(tier):
    return f"**{core.BAND_LABEL}: {core.BAND[tier]}** of 3 (1 = top)"



def applied_banner_text():
    it = SITE['independent_test']
    text = (f"Applied problems rarely have a standard benchmark; these are related problems from published papers. "
            f"Results depend on whether the problem has a named benchmark. Automatic evaluation (stacked ranker): a "
            f"family the paper used was in the top 5 for {CAT['Applied']['hit@5']['mean']:.3f} of Applied papers vs "
            f"{CAT['Pure Math']['hit@5']['mean']:.3f} of Pure Math papers.")
    if it['status'] == 'reported':
        g = it['stacked_hit@5_by_group']
        text += (' Independent test (stacked ranker, hit@5): ' + ', '.join(
            f"{k.split(' /')[0]} {v['stacked_hit@5']:.3f}" for k, v in g.items()) + '.')
    return text


def version_line(res):
    return (f"Produced by v2.3 (blend 0.5) · recommend_v23.py sha256 `{res['system_hash'][:12]}`")


def render_result(res, key):
    st.caption(version_line(res))
    if res['applied_share'] > APPLIED_LIMIT:
        st.warning(applied_banner_text())
    st.markdown(band_line(res['tier']))
    for i, f in enumerate(res['families'], 1):
        n = f['note']
        with st.container(border=True):
            st.markdown(f"#### {i}. {f['family_name']}")
            if n['single_paper']:
                st.info('Single paper only: this family is supported by one paper in the data.')
            for line in core.note_lines(n):
                st.markdown(f'- {line}')
            if n['evidence_papers']:
                st.markdown('**Closest evidence papers:** ' + '; '.join(
                    f"{p['title']} ({p['conference']} {p['year']})" for p in n['evidence_papers']))
            if n['members']:
                st.markdown('**Members:** ' + '; '.join(n['members']))
    c1, c2 = st.columns(2)
    c1.download_button('Download CSV', core.to_csv(res), file_name='benchmark_recommendation.csv', mime='text/csv', key=f'csv{key}')
    c2.download_button('Download Markdown', core.to_markdown(res), file_name='benchmark_recommendation.md',
                       mime='text/markdown', key=f'md{key}')


FEATURE_LABELS = {'category': 'problem category', 'variable_type': 'variable type', 'objectives': 'objectives',
                  'n_objectives': 'number of objectives', 'dimensionality': 'dimensionality',
                  'separability': 'separability', 'modality': 'modality', 'landscape': 'landscape',
                  'constraints': 'constraints'}
FEATURE_CHOICES = {'category': ['pure_math', 'applied'],
                   'variable_type': ['continuous', 'binary', 'integer', 'permutation', 'mixed', 'program'],
                   'objectives': ['single', 'multi'], 'separability': ['separable', 'non-separable'],
                   'modality': ['unimodal', 'multimodal'], 'constraints': ['constrained', 'unconstrained']}
STORE_NOTE_HOSTED = ('Learned store: read-only in the hosted demo, because its file system is not durable. Suggestions '
                     'are stored (as unverified) only when the demo runs locally.')


def fmt_value(v):
    return ', '.join(v) if isinstance(v, list) else str(v)


def render_features(sl, key, editable):
    """Show the extracted features; in live mode let the user correct them (the matching is re-run)."""
    prof = sl['profile']
    st.markdown('**Extracted features** (rule-based; "unknown" = not stated, never guessed):')
    st.table(pd.DataFrame([{'feature': FEATURE_LABELS[k], 'value': fmt_value(v) or 'unknown'} for k, v in prof.items()]))
    if editable:
        with st.form(f'correct{key}'):
            new = dict(prof)
            for k, opts in FEATURE_CHOICES.items():
                choices = ['unknown'] + opts
                new[k] = st.selectbox(f"Correct {FEATURE_LABELS[k]}", choices, index=choices.index(prof[k]), key=f'{key}{k}')
            if st.form_submit_button('Re-run matching with these features'):
                if new['n_objectives'] != 'unknown' and new['objectives'] != ('single' if new['n_objectives'] == 1 else 'multi'):
                    new['n_objectives'] = 'unknown'
                st.session_state['profile_override'] = new
                st.rerun()


def render_selflearn(res, key, editable):
    """Fallback view: low-confidence banner, features, shortlist with matched / conflicting / unknown, sources,
    earlier suggestions tagged with their status, and the frozen ranking kept for reference."""
    sl = res['selflearn']
    d = sl['decision']
    why = []
    if d['low_confidence']:
        why.append(f"the ranking's confidence (p1 = {d['p1']:.4f}) is below the threshold {d['threshold']:.4f}, chosen on "
                   'the development queries')
    if d['feature_conflict']:
        why.append('the features you stated conflict with every one of the top five families')
    st.error('**Low confidence.** ' + '; and '.join(why).capitalize() + '. Below are the closest available benchmark '
             'families by the features you stated. None is a confirmed match.')
    st.caption(version_line(res))
    render_features(sl, key, editable)
    for i, it in enumerate(sl['shortlist'], 1):
        with st.container(border=True):
            st.markdown(f"#### {i}. {it['family_name']}" + (f"  — *{it['label']}*" if it['label'] else ''))
            st.markdown(f"- **Matched:** {', '.join(it['matched']) or 'none'}\n"
                        f"- **Conflicting:** {', '.join(it['conflicting']) or 'none'}\n"
                        f"- **Unknown:** {', '.join(it['unknown']) or 'none'}\n"
                        f"- {it['n_papers']} paper{'s' if it['n_papers'] != 1 else ''} in the data")
            if it['source']:
                s = it['source']
                st.markdown(f"**Source:** {s['title']} ({s['conference']} {s['year']})")
    if sl.get('earlier_suggestions'):
        st.markdown('**Earlier suggestions for similar features** (from the learned store):')
        for c in sl['earlier_suggestions']:
            st.markdown(f"- {c['family_name']} `{c['status']}`" + (' (not confirmed by anyone)' if c['status'] == 'unverified' else ''))
    if sl.get('store_read_only') or not editable:
        st.caption(STORE_NOTE_HOSTED)
    elif sl.get('stored'):
        st.caption(f"Stored as unverified record {sl['stored']}. Verify with: python -m selflearn.verify")
    elif sl.get('store_note'):
        st.caption(f"Not stored: {sl['store_note']}.")
    with st.expander('v2.3 ranking for this question (low confidence)'):
        render_result(res, f'{key}r')


def render_answer(res, key, editable):
    status = res.get('status', 'confident')
    if status == 'out_of_scope':
        st.warning(res['message'].capitalize() + '. No shortlist is shown, and nothing is stored.')
    elif status == 'fallback':
        render_selflearn(res, key, editable)
    else:
        render_result(res, key)
        if res.get('selflearn'):
            with st.expander('Extracted features'):
                render_features(res['selflearn'], key, editable)


def fmt(m):
    return f"{m['mean']:.3f} [{m['ci'][0]:.3f}, {m['ci'][1]:.3f}]"


def reliability_panel():
    with st.expander('How reliable is this?'):
        a = SITE['automatic_evaluation']
        st.markdown(f"**Automatic evaluation.** {a['description']}")
        rows = []
        for seed in ('seed 42', 'seed 43'):
            for sname, label in ((SITE['system_name'], 'this system'), ('popularity', 'popularity baseline')):
                m = a[seed][sname]
                rows.append({'run': seed, 'system': label, 'n': m['n'], 'hit@1': fmt(m['hit@1']), 'hit@5': fmt(m['hit@5']),
                             'MRR': fmt(m['mrr'])})
        st.table(pd.DataFrame(rows))
        st.markdown(f'**{core.BAND_LABEL}.** Measured for the stacked ranker in the automatic evaluation (seed 42): ' +
                    ', '.join(f"band {core.BAND[t]} hit@1 {TIERS[t]['hit@1']:.3f}" for t in ('high', 'medium', 'low')) +
                    '. The bands come from the stacked ranker\'s confidence, not from v2.3, and on the independent test '
                    'they did not rise in order.')
        d = SITE['dev_written_queries']
        st.markdown(f"**Written development queries.** {d['description']}")
        st.table(pd.DataFrame([{'system': s if s != SITE['system_name'] else 'this system', 'n': d[s]['n'],
                                'hit@5': fmt(d[s]['hit@5']), 'MRR': fmt(d[s]['mrr'])}
                               for s in (SITE['system_name'], 'full_v2', 'popularity')]))
        it = SITE['independent_test']
        if it['status'] == 'pending':
            st.markdown('**Independent test:** pending. It is scored once on the pre-registered date and reported '
                        'whatever the result.')
        else:
            pc, bd = it['primary_claim'], it['blend_decision']
            d = pc['d_hit@5_vs_popularity']
            st.markdown(f"**Independent test** ({it['n']} new written queries, scored once). Primary claim, "
                        f"{pc['system']} vs popularity: hit@5 difference {d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}], "
                        f"**{pc['verdict']}**.")
            st.table(pd.DataFrame([{'system': lab, 'hit@5': fmt(it[k]['hit@5']), 'MRR': fmt(it[k]['mrr'])}
                                   for k, lab in (('stacked', 'stacked ranker (primary claim)'),
                                                  ('blend_0.5', 'blend 0.5 = v2.3 (product)'),
                                                  ('popularity', 'popularity baseline'))]))
            m = bd['d_mrr_blend_minus_stacked']
            st.markdown(f"Blend decision: MRR difference blend minus stacked {m[0]:+.3f} [{m[1]:+.3f}, {m[2]:+.3f}]: "
                        f"{bd['outcome']}. The blend was chosen after seeing the test, so its test numbers are "
                        "selection numbers.")


# ---------------------------------------------------------------- page
st.title('Benchmark recommender for evolutionary algorithms')
st.caption('Suggests benchmark families that published papers used for similar problems (product system v2.3, '
           'blend 0.5). Benchmarks only; no algorithm recommendation. Treat the list as suggestions to check.')
if MODE == 'precomputed':
    st.info('This hosted demo shows **precomputed examples** of the product system v2.3 (below). Live retrieval runs locally '
            'with run_demo.sh.')

text = st.text_area('Describe your algorithm or problem', placeholder=DEMO['placeholder'], height=110)
consent = st.checkbox('Keep my question text with the suggestion in the learned store (local mode only)', value=False)
if st.button('Recommend', type='primary'):
    ok, msg = core.validate_query(text)
    if not ok:
        st.warning(msg)
    elif MODE != 'live':
        st.warning('Live retrieval is not available in the hosted demo (it needs more memory and CPU than the free '
                   'tier guarantees). Run it locally with run_demo.sh, or see the precomputed examples below.')
    else:
        st.session_state['last_query'] = text.strip()
        st.session_state['profile_override'] = None
if MODE == 'live' and st.session_state.get('last_query'):
    import live
    with st.spinner('Ranking with the frozen system...'):
        res, err = core.run_with_timeout(live.recommend, st.session_state['last_query'], consent,
                                         st.session_state.get('profile_override'))
    if err:
        st.error(err)
    else:
        render_answer(res, 'live', editable=True)

reliability_panel()

if MODE != 'live':
    st.caption(STORE_NOTE_HOSTED)
st.subheader('Gallery: precomputed examples')
st.caption(f"Label: **{GALLERY['label']}**. System: {GALLERY.get('system', '')}. Queries chosen by a fixed rule ({GALLERY['rule']}), unedited system output, "
           f"with the gold families from queries_v2. Precomputed on {GALLERY['built']}.")
for k, item in enumerate(GALLERY['items']):
    tag = 'HIT' if item['hit'] else 'MISS'
    with st.expander(f"{item['query_id']} [{tag}] {item['query_text'][:110]}"):
        st.markdown(f"**Query:** {item['query_text']}")
        st.markdown(f"**Gold (queries_v2):** {item['gold_family_names']}: **{tag}** "
                    f"({'a gold family is in the top 5' if item['hit'] else 'no gold family in the top 5'})")
        render_answer(item['result'], f'g{k}', editable=False)

actual, expected, ok = core.frozen_hash_status()
st.divider()
st.caption(f"Mode: {MODE}. Product system v2.3 (blend 0.5): retrieval_v2/recommend_v23.py sha256 `{actual}` "
           f"({'matches FROZEN_HASHES_v23.txt' if ok else 'DOES NOT MATCH FROZEN_HASHES_v23.txt'}). Gallery built with "
           f"`{GALLERY['system_hash']}`.")
