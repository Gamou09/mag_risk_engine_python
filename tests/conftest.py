import sys
from pathlib import Path

# Ensure the project root is importable when running pytest without installation.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
