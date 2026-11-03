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
    rel42 = section(r21.split('## Seed 43')[0], '### Reliability (stacked, top-1 probability tiers; cut-offs from training folds)', None)
    rel43 = section(r21.split('## Seed 43')[1], '### Reliability (stacked, top-1 probability tiers; cut-offs from training folds)', '## Pre-registered')
    L = ['# Retrieval v2.1: results', '',
         'Benchmark-family recommendation from a problem description. Models frozen at tag `retrieval-v2.1-frozen`. '
         'Details: `evaluation/report_auto.md` (v2), `evaluation/report_v21.md` (v2.1), '
         '`evaluation/report_query_sets.md` (written queries); pre-registrations `evaluation/PREREGISTRATION.md`, '
         '`evaluation/PREREGISTRATION_queries.md`.', '',
         '## Setup', '',
         '- 1,488 papers (11,342 benchmark records), 3,199 problem entities, 2,173 v5 benchmark families.',
         '- Five folds **by paper**, stratified by Category x Conference; two seeds (42 primary, 43 replication).',
         '- Each fold\'s index (entity descriptions, entity embeddings, BM25, family paper counts, kNN paper pool) is '
         '**rebuilt from the training papers only**.',
         '- One automatic query per held-out paper from its own fields, with every **benchmark name token masked**; gold = '
         'the paper\'s families that exist in the training index ("seen"). Papers without seen gold are "unseen" and not scored.',
         '- Systems: popularity; BM25 only; dense only (all-mpnet-base-v2); full v2 (BM25 + dense, RRF, cross-encoder, '
         'family roll-up with evidence bonus); paper-kNN voting; stacked (logistic regression over 8 features of the '
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
          f'- **Provenance.** The provenance statement is in `evaluation/PROVENANCE.md`: "{prov}" The item "System outputs '
          'seen before the file was final" has no answer.', '']
    (HERE.parent / 'RESULTS.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
