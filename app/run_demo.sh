#!/usr/bin/env bash
# Run the demo locally in LIVE mode (the frozen recommender on your own descriptions).
# Needs the environment in retrieval_v2/evaluation/FROZEN_ENV.txt plus streamlit (app/requirements-live.txt).
set -euo pipefail
cd "$(dirname "$0")/.."
grep -v '^#' retrieval_v2/evaluation/FROZEN_HASHES.txt | sha256sum -c --strict --quiet
echo "Frozen files verified (FROZEN_HASHES.txt)."
DEMO_MODE=live exec streamlit run app/streamlit_app.py "$@"
