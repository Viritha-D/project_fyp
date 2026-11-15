"""
Entry point for Streamlit Community Cloud: set the main file path to `app.py`.

It runs `app/streamlit_app.py` unchanged, with `app/` on the import path (as when that file is run directly). The mode
follows DEMO_MODE as before: unset means precomputed (the hosted default), DEMO_MODE=live means live (local only).
"""
import runpy
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / 'app'
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

runpy.run_path(str(APP_DIR / 'streamlit_app.py'), run_name='__main__')
