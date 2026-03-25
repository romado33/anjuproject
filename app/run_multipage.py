"""Single entry for Streamlit ``st.navigation`` so sidebar labels are explicit (e.g. Home, not script stem)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.logging_config import configure_logging
from config.settings import get_settings

_APP_DIR = Path(__file__).resolve().parent
_ROOT = _APP_DIR.parent
_ASSETS = _ROOT / "assets"
_LOGO_PATH = _ASSETS / "anju-software-log.svg"
_LOGO_FALLBACK = _ASSETS / "anju_wordmark.svg"


def run() -> None:
    configure_logging(get_settings().log_level)
    logo_file = _LOGO_PATH if _LOGO_PATH.is_file() else _LOGO_FALLBACK
    if logo_file.is_file():
        st.logo(logo_file, size="large", link="https://www.anjusoftware.com/")
    pages = [
        st.Page(
            str(_APP_DIR / "pages" / "0_Home.py"),
            title="Home",
            default=True,
            icon="🏠",
        ),
        st.Page(str(_APP_DIR / "pages" / "1_Case_intake.py"), title="Case intake"),
        st.Page(
            str(_APP_DIR / "pages" / "2_Review_case_actions.py"),
            title="Review case actions",
        ),
        st.Page(str(_APP_DIR / "pages" / "4_Integrations.py"), title="Integrations"),
        st.Page(
            str(_APP_DIR / "pages" / "3_Policy_and_Privacy.py"),
            title="Policy & privacy",
        ),
    ]
    st.navigation(pages).run()
