# Provenance of the independent query sets

Recorded at intake: t1 and t2 on 2026-11-09, t3 and t4 on 2026-11-11. Nothing below is guessed. "not provided" means the
field was blank, or held only an unfilled placeholder, in the request that delivered the information. Quoted values are
verbatim.

| field | t1 | t2 | t3 | t4 |
|---|---|---|---|---|
| file in repo | `queries_t1.xlsx` | `queries_t2.xlsx` | `queries_t3.xlsx` | `queries_t4_original.docx` (converted: `queries_t4.xlsx`, `queries_t4.csv`) |
| original upload name | `user_queries_1.xlsx` | `user_queries.xlsx` | `queries_t3.xlsx` | `queries_benchmarks.docx` |
| sha256 | `f6319d7ff8865f8a73256408d7eb26eacddeb833df3d0a9ab38017871b6a9202` | `4546752893d579c26f12caac15b029260e2211de8a8beb9a000254dd0be19b45` | `879d4177fdaf96c58151fa5f34e063772456092648e78e43411dd6ae7696b74c` | `feeae691669d0a5ef91e92640917f38edba6b2522f13131b1ef3dda9a6a2b977` |
| size (bytes) | 7,784 | 8,774 | 8,360 | 18,530 |
| docProps creator | `openpyxl` | `openpyxl` | `openpyxl` | `Un-named` |
| docProps lastModifiedBy | (absent) | (absent) | (absent) | `sanjeshnandha` |
| docProps created | 2026-11-05T03:05:41Z | 2026-11-09T09:13:53Z | 2026-11-11T09:27:31Z | (absent) |
| docProps modified | 2026-11-05T03:05:45Z | 2026-11-09T09:13:53Z | 2026-11-11T09:27:31Z | 2026-11-11T15:12:40Z |
| docProps revision | (absent) | (absent) | (absent) | 1 |
| docProps application | Microsoft Excel Compatible / Openpyxl 3.1.5 | Microsoft Excel Compatible / Openpyxl 3.1.5 | Microsoft Excel Compatible / Openpyxl 3.1.5 | WPS Office_12.1.28496.28496_F1E327BC-269C-435d-A152-05C5408002CA (Pages 3, TotalTime 3; custom: KSOProductBuildVer 1033-12.1.28496.28496, ICV F25E26716CF836939038F46A82DADFBF_42) |
| sheet / table | sheet `queries` | sheet `Sheet1` | sheet `queries` | one Word table, 5 columns |
| rows (excluding header) | 20 | 20 | 20 | 20 |
| form | ids + names | ids + names | names-only | ids + names |
| writer | not provided | not provided | not provided | Sanjesh Nandha K |
| start time | not provided | not provided | not provided | not provided |
| finish time | not provided | not provided | not provided | "3:37 pm" as printed in the document ("Finished:  November 11, 2026 , 3:37 pm "). Writer's own answer on the finish time: not yet answered. Recorded without conclusion: the file's last-saved stamp (docProps modified) is 2026-11-11T15:12:40Z as stored, and the user states the file was sent to them before 3:37 pm. |
| drafting | not provided | not provided | not provided | "Drafted questions using google and research papers", with the two links given in the document: https://link.springer.com/article/10.1007/s00521-020-04832-8#Sec12 and https://link.springer.com/chapter/10.1007/978-0-387-36797-2_7 |
| tools used (including any AI tool) | not provided | not provided | not provided | "Copilot for creating word document" |
| AI statement: did any AI tool write or suggest queries, ids or family names | not provided | not provided | not provided | not yet answered |
| t2 writer's answer: where the ids came from | - | not yet answered | - | - |
| commit adding the original | d6f57a0 | d6f57a0 | 32e0be6 | 32e0be6 |
| status | delivered | delivered; rejected, 100% invalid (amendment 1) | delivered | delivered |

**How the originals were committed.**

- t1 and t2 were committed alone and unchanged (byte-identical to the uploads) in d6f57a0, "add independent query
  sets t1, t2 before validation and scoring".
- t3 and t4 were committed alone and unchanged in 32e0be6, "add independent query sets t3 and t4 (originals) before
  validation and scoring". That commit came after amendment 3 (81384f4) and before any validation or scoring.
- The names t3 and t4 were assigned because two writers were both told to save as `queries_t3.xlsx` (amendment 3).

**Note on docProps (uninformative here).** The docProps creator and application fields read `openpyxl` / "Microsoft
Excel Compatible / Openpyxl 3.1.5" in every xlsx query file in this project. That includes queries_v2.xlsx and its
source uploads (checked 2026-11-09). So these fields do not show how a file was written or by whom. All raw values,
including t4's, are kept above as recorded and no inference is drawn from them. (An earlier version of this note drew
such an inference; it was removed on 2026-11-09 at the user's request.)

**What the user supplied.**

- 2026-11-09: writers, times and tools of t1 and t2 were not provided, and the t2 writer's answer on where the ids
  came from was not yet answered.
- 2026-11-11: the t1 AI statement and t3's writer, times, tools and AI statement were not provided. For t4, the
  writer, finish time, drafting note with links, and tools were given as quoted above. The t4 AI statement is not
  yet answered.
- 2026-11-11 (amendment 4 request): the t1 AI statement and t3's writer, start/finish, tools and AI statement are
  still not provided. The t4 AI statement and the writer's own answer on the finish time are not yet answered. The
  printed "3:37 pm", the stored last-saved stamp and the user's statement about when the file was sent are recorded
  above without any conclusion.

Under amendment 3, a set with no AI statement by the scoring date stays in the primary analysis, flagged
"provenance not stated".
