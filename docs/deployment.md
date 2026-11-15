# Deployment

**Hosted demo: TODO, not deployed yet.** Put the link here once it is deployed.

## Two modes

| mode | how it starts | what it runs | dependencies |
|---|---|---|---|
| precomputed (default) | `streamlit run app.py` | shows the gallery of real, unedited v2.3 outputs from `app/gallery.json`; the text box validates input but runs no retrieval | `requirements.txt` (streamlit, pandas, numpy; same pins as `app/requirements.txt`) |
| live | `app/run_demo.sh` (sets `DEMO_MODE=live`) | runs v2.3 and the fallback module on your own text | `app/requirements-live.txt` plus CPU torch |

`app/run_demo.sh` checks both `FROZEN_HASHES*.txt` files before it starts. In live mode, the app also refuses to run if
the sha256 of `retrieval_v2/recommend_v23.py` differs from `FROZEN_HASHES_v23.txt`.

## Run live, locally

These steps were measured in a clean virtualenv (`docs/audit_demo.md`, 2026-11-14).

```
python3.13 -m venv .venv
.venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0+cpu
.venv/bin/pip install -r app/requirements-live.txt
source .venv/bin/activate && app/run_demo.sh
```

**Footprint.**

- **Install size:** about 1.8 GB.
- **Memory:** peaks at 1.4 to 1.5 GB at the first answer.
- **First answer:** 7 to 16 seconds. A fresh start downloads about 0.5 GB of model weights from Hugging Face
  (all-mpnet-base-v2 and ms-marco-MiniLM-L-6-v2). Later answers take under a second.

## Hosted on Streamlit Community Cloud (precomputed)

1. Create an app from this repository, on the branch you choose.
2. Set the main file path to `app.py`, which runs `app/streamlit_app.py` unchanged.
3. Set the Python version to **3.13**. The clean-clone test ran on Python 3.13.18.
4. The dependencies come from the root `requirements.txt`, which sits next to `app.py`: streamlit 1.67.0, pandas 3.1.1
   and numpy 2.5.4, with no models or torch. Check the build log to confirm that this is the file Cloud used.
5. Leave `DEMO_MODE` unset, so the app starts in precomputed mode.

**Why the hosted app is precomputed.**

- Community Cloud documents roughly 690 MB to 2.7 GB of RAM and 0.078 to 2 CPU cores, "approximately" and subject to
  change.
- Live mode needs 1.4 to 1.5 GB at peak and would exceed the 20-second answer limit on a fraction of a core.
- A lighter model would make it a different system.

**In hosted mode the learned store is read-only**, because that file system is not durable. No suggestion is written.

**No Git LFS needed.** Every file the app reads is a plain git blob and is pinned as one in `.gitattributes`. A clone
with `GIT_LFS_SKIP_SMUDGE=1` runs the hosted mode without opening any LFS pointer. The evidence is in `docs/data.md`
("Files the app reads").

## Before deploying

Run the checks:

```
grep -v "^#" retrieval_v2/evaluation/FROZEN_HASHES.txt | sha256sum -c --strict
grep -v "^#" retrieval_v2/evaluation/FROZEN_HASHES_v23.txt | sha256sum -c --strict
python app/tools/check_demo_inputs.py
python -m pytest tests -q
```

Nothing in this repository deploys by itself: there is no CI deploy step and no hosting configuration file.
