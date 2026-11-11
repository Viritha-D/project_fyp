"""
Benchmark recommender demo (Streamlit).

Modes
- live (local, run_demo.sh sets DEMO_MODE=live): runs the frozen recommender (retrieval_v2/recommend_v21.py, tag
  retrieval-v2.2, unchanged) on the typed description.
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
def tier_line(tier):
    h = TIERS[tier]['hit@1']
    return (f"**Evidence tier: {tier}** (applies to the whole list). In the automatic evaluation, queries in this tier "
            f"had the top family among those their paper actually used {h:.1%} of the time (about 1 in "
            f"{round(1 / h) if h else '–'}).")


def render_result(res, key):
    if res['applied_share'] > APPLIED_LIMIT:
        st.warning(f"Applied problems rarely have a standard benchmark; these are related problems from published "
                   f"papers. In the automatic evaluation, a family the paper used was in the top 5 for "
                   f"{CAT['Applied']['hit@5']['mean']:.1%} of Applied papers vs {CAT['Pure Math']['hit@5']['mean']:.1%} "
                   f"of Pure Math papers.")
    st.markdown(tier_line(res['tier']))
    for i, f in enumerate(res['families'], 1):
        n = f['note']
        with st.container(border=True):
            st.markdown(f"#### {i}. {f['family_name']}")
            st.caption(f"Evidence tier for this list: {res['tier']} (measured hit@1 {TIERS[res['tier']]['hit@1']:.3f})")
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
        st.markdown('**Evidence tiers (seed 42):** ' + ', '.join(
            f"{t} hit@1 {TIERS[t]['hit@1']:.3f}" for t in ('low', 'medium', 'high')))
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
            st.markdown('**Independent test:**')
            st.markdown(it['markdown'])


# ---------------------------------------------------------------- page
st.title('Benchmark recommender for evolutionary algorithms')
st.caption('Suggests benchmark families that published papers used for similar problems. Benchmarks only; no '
           'algorithm recommendation. Treat the list as suggestions to check.')
if MODE == 'precomputed':
    st.info('This hosted demo shows **precomputed** outputs of the frozen system (below). Live retrieval runs locally '
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

st.subheader('Gallery: precomputed outputs')
st.caption(f"Label: **{GALLERY['label']}**. Queries chosen by a fixed rule ({GALLERY['rule']}), unedited system output, "
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
st.caption(f"Mode: {MODE}. Frozen system: retrieval_v2/recommend_v21.py sha256 `{actual}` "
           f"({'matches FROZEN_HASHES.txt' if ok else 'DOES NOT MATCH FROZEN_HASHES.txt'}). Gallery built with "
           f"`{GALLERY['system_hash']}`.")
