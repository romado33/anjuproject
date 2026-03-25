"""Backward-compatible entry: same navigation as ``Home.py`` (sidebar shows **Home**, not *streamlit app*)."""

from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_ROOT = _APP_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.run_multipage import run

run()
