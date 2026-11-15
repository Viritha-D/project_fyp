import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]              # repository root, so `import selflearn` works
sys.path.insert(0, str(ROOT))
