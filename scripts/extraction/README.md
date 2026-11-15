# Extraction pipeline (provenance)

`gecco_pipeline/` holds the Gemini-based extractor that produced the per-row records for
GECCO and PPSN (the user confirmed it was used for PPSN). Only three of its modules are
here, copied unchanged from the user's upload:

| file | role |
|---|---|
| `gecco_pipeline/config.py` | settings: Gemini model (`gemini-3.5-flash`), temperature 0.1, rate limits; API keys come from the environment / `.env`, never from the code |
| `gecco_pipeline/extractor.py` | uploads one PDF to the Gemini File API and asks for a `PaperResult` (one `metadata` block + a list of `extractions`) |
| `gecco_pipeline/processor.py` | batch driver; a PDF with more than 200 pages is split into 200-page parts, each part is extracted, and the parts' extractions are merged under **the first part's metadata** |

Not in the repository (imported by the code above, so it does not run as is):
`gecco_pipeline/schemas.py`, `prompt_template.py`, `utils.py`, `__init__.py`. The PReMI
extraction scripts (described as a zip) were not found in any branch or commit.

## What this means for PPSN

Each PPSN Source_File is one PDF processed by this pipeline, so every row from that file
carries the single `metadata` (Paper_Title, Authors, Year) the model returned for it, and
for a split PDF that is the metadata of its first 200-page part. That matches the data:
every PPSN file has exactly one title, one author list and one Original_Paper_ID root,
while its rows span several unrelated Problem_Contexts. For the 2020 and 2024 files the
returned title is the proceedings name; for 2016, 2018 and 2022 it is one paper's title.
So the per-row Paper_Title / Authors of PPSN rows describe the PDF, not the paper each
row came from. The PPSN PDFs themselves are not in the repository, so page counts and
the paper behind each row could not be checked.
