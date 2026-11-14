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
if st.button('Recommend', type='primary'):
    ok, msg = core.validate_query(text)
    if not ok:
        st.warning(msg)
    elif MODE != 'live':
        st.warning('Live retrieval is not available in the hosted demo (it needs more memory and CPU than the free '
                   'tier guarantees). Run it locally with run_demo.sh, or see the precomputed examples below.')
    else:
        import live
        with st.spinner('Ranking with the frozen system...'):
            res, err = core.run_with_timeout(live.recommend, text.strip())
        if err:
            st.error(err)
        else:
            render_result(res, 'live')

reliability_panel()

st.subheader('Gallery: precomputed examples')
st.caption(f"Label: **{GALLERY['label']}**. System: {GALLERY.get('system', '')}. Queries chosen by a fixed rule ({GALLERY['rule']}), unedited system output, "
           f"with the gold families from queries_v2. Precomputed on {GALLERY['built']}.")
for k, item in enumerate(GALLERY['items']):
    tag = 'HIT' if item['hit'] else 'MISS'
    with st.expander(f"{item['query_id']} [{tag}] {item['query_text'][:110]}"):
        st.markdown(f"**Query:** {item['query_text']}")
        st.markdown(f"**Gold (queries_v2):** {item['gold_family_names']}: **{tag}** "
                    f"({'a gold family is in the top 5' if item['hit'] else 'no gold family in the top 5'})")
        render_result(item['result'], f'g{k}')

actual, expected, ok = core.frozen_hash_status()
st.divider()
st.caption(f"Mode: {MODE}. Product system v2.3 (blend 0.5): retrieval_v2/recommend_v23.py sha256 `{actual}` "
           f"({'matches FROZEN_HASHES_v23.txt' if ok else 'DOES NOT MATCH FROZEN_HASHES_v23.txt'}). Gallery built with "
           f"`{GALLERY['system_hash']}`.")
