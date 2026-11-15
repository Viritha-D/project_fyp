# Deployment

**Hosted demo: TODO, not deployed yet.** Put the link here once it is deployed.

## Two modes

| mode | how it starts | what it runs | dependencies |
|---|---|---|---|
| precomputed (default) | `streamlit run app/streamlit_app.py` | shows the gallery of real, unedited v2.3 outputs from `app/gallery.json`; the text box validates input but runs no retrieval | `app/requirements.txt` (streamlit, pandas, numpy) |
| live | `app/run_demo.sh` (sets `DEMO_MODE=live`) | runs v2.3 and the fallback module on your own text | `requirements.txt` plus CPU torch |

`app/run_demo.sh` checks both `FROZEN_HASHES*.txt` files before it starts. In live mode, the app also refuses to run if
the sha256 of `retrieval_v2/recommend_v23.py` differs from `FROZEN_HASHES_v23.txt`.

## Run live, locally

These steps were measured in a clean virtualenv (`docs/audit_demo.md`, 2026-11-14).

```
python3.13 -m venv .venv
.venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0+cpu
.venv/bin/pip install -r requirements.txt
source .venv/bin/activate && app/run_demo.sh
```

**Footprint.**

- **Install size:** about 1.8 GB.
- **Memory:** peaks at 1.4 to 1.5 GB at the first answer.
- **First answer:** 7 to 16 seconds. A fresh start downloads about 0.5 GB of model weights from Hugging Face
  (all-mpnet-base-v2 and ms-marco-MiniLM-L-6-v2). Later answers take under a second.

## Hosted on Streamlit Community Cloud (precomputed)

1. Create an app from this repository, on the branch you choose.
2. Set the main file path to `app/streamlit_app.py` and the Python version to 3.13.
3. Use `app/requirements.txt` for the dependencies. Community Cloud's documentation says it looks first for a dependency
   file next to the entry point, and then at the root. So it picks `app/requirements.txt` (no models) rather than the
   root `requirements.txt` (the full live stack). Check the build log to confirm which file it used.
4. Leave `DEMO_MODE` unset, so the app starts in precomputed mode.

**Why the hosted app is precomputed.**

- Community Cloud documents roughly 690 MB to 2.7 GB of RAM and 0.078 to 2 CPU cores, "approximately" and subject to
  change.
- Live mode needs 1.4 to 1.5 GB at peak and would exceed the 20-second answer limit on a fraction of a core.
- A lighter model would make it a different system.

**In hosted mode the learned store is read-only**, because that file system is not durable. No suggestion is written.

## Before deploying

Run the checks:

```
grep -v "^#" retrieval_v2/evaluation/FROZEN_HASHES.txt | sha256sum -c --strict
grep -v "^#" retrieval_v2/evaluation/FROZEN_HASHES_v23.txt | sha256sum -c --strict
python app/tools/check_demo_inputs.py
python -m pytest tests -q
```

Nothing in this repository deploys by itself: there is no CI deploy step and no hosting configuration file.
