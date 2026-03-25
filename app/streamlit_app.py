"""Backward-compatible Streamlit entry point.

The canonical script is ``app/Home.py`` (sidebar shows **Home**). If your IDE,
shortcuts, or muscle memory still use ``streamlit run app/streamlit_app.py``,
this module delegates to the same ``main()`` as ``Home.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_ROOT = _APP_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.Home import main

main()
