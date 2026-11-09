"""Build retrieval_v2/RESULTS.md (project-report summary) from the saved result files. No model is run."""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import evaluate as ev  # noqa: E402
import evaluate_v21 as e21  # noqa: E402

# Hand-written section added during the pre-final audit (52cf7ef); kept verbatim on every regeneration.
DECISIONS_AFTER_QUERIES_V2 = '''
## Decisions made after seeing queries_v2

queries_v2 was committed at c0f8802 and first scored at 27c4b84 (2026-11-03 06:34 UTC). Nothing was trained on
queries_v2 text or gold, with one exception, the v2.2 λ selection:

- The frozen model files were last changed before queries_v2 was committed: `v21_model.json` (stacker weights,
  tier cut-offs, K) at c7a0e04, `v21.py` at 6b0e1fc, `hybrid.py` and `config.json` at 31b4d55, and families,
  entities and embeddings even earlier. Their hashes are in `evaluation/FROZEN_HASHES.txt`.
- The only code that reads queries_v2 is the scorer and report scripts (`score_human_queries.py`,
  `report_query_sets.py`, `build_results_md.py`) and `v22/run_v22.py`.

Every decision taken after the queries_v2 results were seen:

1. **v2.2 λ, selected on queries_v2 (tuning).** λ was the argmax of queries_v2 MRR among the eligible values
   (`v22/run_v22.py`). The rule chose λ = 1.0, i.e. no change to the ranking. Even so, queries_v2 numbers from then
   on are selection numbers, not test numbers.
2. **Design of the v2.2 experiment (design choice).** The idea of blending full v2 with the stacked ranker, the
   RRF form with k = 60 and the λ grid {0, 0.25, 0.5, 0.75, 1} were all chosen after queries_v2 showed full v2 ahead
   of the stacked ranker.
3. **Eligibility condition for λ (threshold).** The rule required automatic hit@5 ≥ popularity's on both seeds
   (.328 / .310). It was written before the v2.2 run, but after queries_v2 results were known.
4. **Diagnostics (report only).** The diagnostics A1/A2 and the "Known weaknesses" section were chosen because of
   the queries_v2 misses (size bias, the (1+1) EA example).
5. **Secondary systems of the final test (design choice).** Full v2 (λ = 0) and blend λ = 0.5 are in the final
   pre-registration because they did well on queries_v2. Blend 0.5 had the highest queries_v2 MRR (tied with 0.75),
   and the final decision rule lets it replace the primary. It was therefore picked after looking at queries_v2.
6. **Final decision rule on the pooled set (design choice).** Using the pooled t1+t2+t3 set for the product
   decision was decided while writing `evaluation/PREREGISTRATION_final.md`, after queries_v2 and v2.2 results.
7. **CLI wording (display only, no ranking change).** The plain tier meanings in `recommend_v21.py` ("about 1 in 10 /
   6 / 4") were added after queries_v2 was scored. The numbers come from the automatic evaluation, not from queries_v2.
8. **Documentation.** The RESULTS.md limitations about queries_v2 (stacked below full v2, generic suites in the top 5)
   and the provenance answer "Unknown" were added afterwards. They are text only.

Not decided after queries_v2: index hygiene, paper-kNN K, the stacker features and weights, the tier cut-offs, the
dropped margin gate, the two-slate output and the gold of queries_v2. All of these predate it (Part C,
pre-registered in `evaluation/PREREGISTRATION.md`). The gold of queries_v2 and its 55 queries were never edited.
'''

MAIN = ['popularity', 'bm25_only', 'dense_only', 'full_v2', 'paper_knn', 'stacked']


def section(md, start, end):
    t = md[md.index(start) + len(start):]
    return t[:t.index(end)].strip() if end else t.strip()


def main():
    r21 = (HERE / 'report_v21.md').read_text(encoding='utf-8')
    rq = (HERE / 'report_queries_v2.md').read_text(encoding='utf-8')
    R = {s: pd.read_csv(HERE / f'results_v21_seed{s}.csv') for s in (42, 43)}
    m = json.loads((HERE.parent / 'v21_model.json').read_text(encoding='utf-8'))
    prov = (HERE / 'PROVENANCE.md').read_text(encoding='utf-8').strip()
    r22 = (HERE.parent / 'v22' / 'report_v22.md').read_text(encoding='utf-8')
    sel = json.loads((HERE.parent / 'v22' / 'v22_selection.json').read_text(encoding='utf-8'))
    rel42 = section(r21.split('## Seed 43')[0], '### Reliability (stacked, top-1 probability tiers; cut-offs from training folds)', None)
    rel43 = section(r21.split('## Seed 43')[1], '### Reliability (stacked, top-1 probability tiers; cut-offs from training folds)', '## Pre-registered')
    L = ['# Retrieval v2.1 / v2.2: results', '',
         '**v2.2 ranks identically to v2.1.** The v2.2 blend experiment selected lambda = 1.0, which is the stacked '
         'v2.1 ranking unchanged (checked: identical top-5 on all 55 / 558 / 548 queries, and identical CLI output on the '
         '7 demo queries). The product system is therefore called the **stacked ranker (v2.1/v2.2)** below; tables label '
         'it `stacked ranker (v2.1/v2.2)`. Tags: `retrieval-v2.1-frozen`, `retrieval-v2.2`.', '',
         'Benchmark-family recommendation from a problem description. Models frozen at tag `retrieval-v2.1-frozen`. '
         'Details: `evaluation/report_auto.md` (v2), `evaluation/report_v21.md` (v2.1), '
         '`evaluation/report_query_sets.md` (written queries); pre-registrations `evaluation/PREREGISTRATION.md`, '
         '`evaluation/PREREGISTRATION_queries.md`, `v22/PREREGISTRATION_v22.md`; blend experiment `v22/report_v22.md`.', '',
         '## Setup', '',
         '- 1,488 papers (11,342 benchmark records), 3,199 problem entities, 2,173 v5 benchmark families.',
         '- Five folds **by paper**, stratified by Category x Conference; two seeds (42 primary, 43 replication).',
         '- Each fold\'s index (entity descriptions, entity embeddings, BM25, family paper counts, kNN paper pool) is '
         '**rebuilt from the training papers only**.',
         '- One automatic query per held-out paper from its own fields, with every **benchmark name token masked**; gold = '
         'the paper\'s families that exist in the training index ("seen"). Papers without seen gold are "unseen" and not scored.',
         '- Systems: popularity; BM25 only; dense only (all-mpnet-base-v2); full v2 (BM25 + dense, RRF, cross-encoder, '
         'family roll-up with evidence bonus); paper-kNN voting; stacked ranker (v2.1/v2.2) (logistic regression over 8 features of the '
         'candidates from full v2 and paper-kNN, cross-fitted).',
         '- 95% bootstrap intervals over papers (1,000 resamples).', '']
    for s in (42, 43):
        n = (R[s].system == 'stacked').sum()
        L += [f'## Overall, seed {s} (n = {n} scored papers)', '', e21.table(R[s], systems=MAIN), '']
    L += ['## By Category (seed 42)', '', e21.table(R[42], 'Category', systems=MAIN), '',
          '## By Category (seed 43)', '', e21.table(R[43], 'Category', systems=MAIN), '',
          '## Pre-registered criterion', '', section(r21, '## Pre-registered success criterion', '## Unseen analysis'), '',
          '## Reliability of the confidence tiers (stacked)', '', '**Seed 42**', '', rel42.split('## ')[0].strip(), '',
          '**Seed 43**', '', rel43, '',
          '## Unseen analysis and oracle (seed 42)', '', section(r21, '## Unseen analysis (seed 42)', '## Two-slate'), '',
          '## Stacked ranker weights (deployment model, standardised features)', '',
          '| feature | coefficient |', '|---|---|']
    L += [f'| {f} | {c:+.3f} |' for f, c in zip(m['stacker']['features'], m['stacker']['coef'])]
    L += [f'| intercept | {m["stacker"]["intercept"]:+.3f} |', '',
          f'paper-kNN K = {m["K"]}; tier cut-offs {m["tier_cuts"][0]:.4f} / {m["tier_cuts"][1]:.4f}.', '',
          '## Written query set (queries_v2, 55 queries, published index)', '',
          section(rq, '## Overall', '## By group').replace('## Primary', '### Primary'), '', '### By group', '', section(rq, '## By group', '## Stacked confidence'), '',
          '### Confidence tiers on the written queries', '', section(rq, '## Stacked confidence tiers (frozen cut-offs)', None), '',
          'Secondary sets `ai_queries_v1.csv` and `queries_reworded_v1.csv`: not run (files not supplied).', '',
          '## Limitations', '',
          '- **Stacking, not strict nesting.** The stacked ranker for fold i is trained on the out-of-fold features of the '
          'other folds, whose indexes contain fold i\'s papers as training data.',
          '- **Candidate ceiling.** A gold family is among the stacked ranker\'s candidates for only 56.6% (seed 42) / 52.2% '
          '(seed 43) of scored queries; no re-ranking can recover the rest.',
          '- **Unseen papers.** 930 of 1,488 papers (seed 42) have no gold family in the training index, and 97.8% of these '
          'use only single-paper benchmarks, so no split could make them findable (oracle hit@5 over all papers .375).',
          '- **Applied problems.** Stacked hit@5 on Applied papers is .127 (seed 42), slightly below full v2 (.152; paired '
          'difference -.025 [-.057, .006]); the gain over popularity comes from Pure Math.',
          '- **Under-confident tiers.** In every tier the measured hit@1 is above the mean predicted probability; the tiers '
          'rank queries but their probabilities are not calibrated.',
          '- **Automatic Pure Math queries carry little information.** With benchmark names masked, a Pure Math query is '
          'mostly an algorithm name, a dimension and generic landscape words, which favours popular suites.',
          '- **Gold selection.** Gold for all query sets (automatic and written) was chosen with the families browse file '
          '(`evaluation/families_browse.csv`), i.e. within the v5 family layer.',
          '- **Written queries.** On the 55 written queries, stacked is below full v2 (hit@5 difference -.073 [-.182, .036], '
          'MRR -.086 [-.186, .002]); the stacked ranker often fills the top 5 with large generic suites (BBOB, CEC 2017, '
          'DTLZ) for specific queries.',
          '- **queries_v2 is a selection set.** The v2.2 lambda was selected on queries_v2 (MRR), so every number on '
          'queries_v2 after the blend experiment is a selection number, not a test number.',
          f'- **Provenance.** The provenance statement is in `evaluation/PROVENANCE.md`: "{prov}" It is unknown whether system '
          'outputs were seen before the file was final.', '']
    blend_tab = section(r22, '## B1. Blend curves (score = (1-lambda)/(60+rank_full) + lambda/(60+rank_stacked))', '## B2. Selection')
    sel_tab = section(r22, '## B2. Selection', '**Chosen lambda')
    L += ['## Blend experiment (v2.2)', '',
          'Final ranking = weighted reciprocal rank fusion of the full v2 family ranking and the stacked family ranking: '
          'score = (1 - lambda) / (60 + rank_full) + lambda / (60 + rank_stacked); a family missing from one list gets no '
          'contribution from that term; lambda in {0, 0.25, 0.5, 0.75, 1}. Pre-registered in `v22/PREREGISTRATION_v22.md` '
          'before any run.', '', blend_tab, '',
          '**Selection rule (fixed before the run).** Among the lambdas whose automatic-evaluation hit@5 is not below '
          'popularity\'s on both seeds (.328 / .310), choose the highest MRR on queries_v2; ties go to the smaller lambda.', '',
          sel_tab, '',
          f'**Why the rule chose lambda = {sel["lambda"]}.** Only lambda = 1.0 meets the eligibility condition: it keeps the '
          'stacked ranker\'s automatic hit@5 (.376 / .352), while every lambda < 1 falls to about .19 / .21, far below '
          'popularity. lambda = 0.5 and 0.75 have the higher queries_v2 MRR (.468 vs .336) but are not eligible.', '',
          '**Why every lambda < 1 collapses on the automatic evaluation.** Full v2\'s families (its shortlist roll-up) are '
          'always also stacked candidates, because the stacked candidate set is the shortlist families plus the top kNN '
          'families. A family on both lists receives both terms of the fused score, so as soon as full v2 has any weight its '
          'families outrank the families that only the stacked ranking places high; the blended top 5 is then essentially '
          'full v2\'s families in a new order, and inherits full v2\'s low automatic hit@5.', '',
          '**Selection, not test.** lambda was selected on queries_v2, so the queries_v2 numbers in this section are '
          'selection numbers, not test numbers. The final independent test is pre-registered in '
          '`evaluation/PREREGISTRATION_final.md`.', '',
          '## Known weaknesses (from `v22/report_v22.md`)', '',
          '- **Size bias.** The stacked ranker favours large families: on the 21 cause-(b) misses of queries_v2 the mean '
          'size of its top-5 families is 25.8 papers vs 5.7 for full v2 (24.8 vs 4.8 on all 55 queries). In 7 of those 21 '
          'queries full v2 had a gold family in its top 5 (e.g. linear ordering and symbolic regression at rank 1) that the '
          'stacked ranker pushed below rank 5.',
          '- **(1+1) EA runtime example.** For "I need benchmarks for a runtime analysis of a (1+1) EA on pseudo-Boolean '
          'functions", OneMax is rank 7 and LeadingOnes rank 30 (reached only through popularity padding) in the stacked '
          'ranker; neither is a candidate in BM25 only or in full v2.',
          '- **Full v2 brings in odd single-paper families.** E.g. "Stackelberg duopoly" (rank 1) and "Indoor localization '
          'using TOA and RSS" for the differential-evolution demo query, "Gymnasium environments" and "Test-Assignment '
          'Problem" for the TSP query; the stacked ranker instead pads with generic suites (DTLZ for TSP; sphere, rastrigin, '
          'mnist for software defect prediction).', '']
    text = '\n'.join(L)
    for a, b in (('| stacked |', '| stacked ranker (v2.1/v2.2) |'), ('| stacked - ', '| stacked ranker (v2.1/v2.2) - ')):
        text = text.replace(a, b)
    text = text + '\n' + DECISIONS_AFTER_QUERIES_V2
    (HERE.parent / 'RESULTS.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
