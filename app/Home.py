"""
Anju Internal Case Router — Streamlit entry point.

Run from project root:
  pip install -r requirements.txt
  python scripts/seed_knowledge_base.py
  streamlit run app/Home.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure imports resolve before other app modules load
_APP_DIR = Path(__file__).resolve().parent
_ROOT = _APP_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.ui_theme import inject_theme, render_process_breadcrumb
from config.logging_config import configure_logging
from config.settings import get_settings

configure_logging(get_settings().log_level)


def main() -> None:
    st.set_page_config(
        page_title="Anju Internal Case Router",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()
    render_process_breadcrumb(current="overview")

    settings = get_settings()
    offline = settings.use_offline_mode()

    st.sidebar.title("Navigation")
    st.sidebar.caption("Internal operations workflow")

    if offline:
        st.sidebar.info(
            "Offline mode: no `OPENAI_API_KEY`. Keyword classification; retrieval skipped when policy requires API."
        )
    else:
        st.sidebar.success("OpenAI configured — LLM + embeddings enabled where policy allows.")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Mock adapters:** Jira · Teams · Salesforce / Veeva CRM · NetSuite · BambooHR · Wiki checklist"
    )

    st.title("Anju Internal Automation")
    st.markdown(
        '<div class="demo-card"><div class="demo-value">Turn one inbound request into a routed, '
        'approval-gated action plan across internal systems.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Start")
    guide_1, guide_2 = st.columns(2)
    with guide_1:
        try:
            st.page_link(
                "pages/1_Case_intake.py",
                label="1. Case intake",
                use_container_width=True,
            )
        except Exception:
            st.markdown("Step 1: open **Case intake** from the sidebar.")
    with guide_2:
        try:
            st.page_link(
                "pages/2_Review_case_actions.py",
                label="2. Review case actions",
                use_container_width=True,
            )
        except Exception:
            st.markdown("Step 2: open **Review case actions** from the sidebar.")

    with st.expander("Model & routing settings", expanded=False):
        st.caption("How this demo classifies requests when an API key is present; optional detail for reviewers.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mode", "Offline" if offline else "LLM + policy")
        with col2:
            st.metric("Classifier", settings.openai_chat_model if not offline else "heuristic")
        with col3:
            st.metric("Confidence threshold", f"{settings.classification_confidence_threshold:.2f}")


if __name__ == "__main__":
    main()
