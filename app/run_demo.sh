#!/usr/bin/env bash
# Run the demo locally in LIVE mode (product system v2.3 = blend 0.5 on your own descriptions).
# Needs the environment in retrieval_v2/evaluation/FROZEN_ENV.txt plus streamlit (app/requirements-live.txt).
set -euo pipefail
cd "$(dirname "$0")/.."
grep -v '^#' retrieval_v2/evaluation/FROZEN_HASHES.txt | sha256sum -c --strict --quiet
grep -v '^#' retrieval_v2/evaluation/FROZEN_HASHES_v23.txt | sha256sum -c --strict --quiet
echo "Frozen files verified (FROZEN_HASHES.txt, FROZEN_HASHES_v23.txt)."
DEMO_MODE=live exec streamlit run app/streamlit_app.py "$@"
