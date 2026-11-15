import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / 'app'     # tests/app/ -> repository root / app
sys.path.insert(0, str(APP))
