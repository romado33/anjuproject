"""Landing page content (sidebar label comes from st.navigation in run_multipage)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui_theme import (
    inject_theme,
    page_config,
    render_luminee_sidebar_promo,
    render_process_breadcrumb,
)
from config.logging_config import configure_logging
from config.settings import get_settings

configure_logging(get_settings().log_level)
page_config("Home")
inject_theme()
render_process_breadcrumb(current="overview")

settings = get_settings()
offline = settings.use_offline_mode()

st.sidebar.markdown(
    "**Mock adapters:** Jira · Teams · Salesforce / Veeva CRM · NetSuite · BambooHR · Wiki checklist"
)
st.sidebar.markdown("---")
render_luminee_sidebar_promo()

st.title("Anju Internal Automation")
st.markdown(
    "AI-enabled routing, human approval for actions, and instant automated execution "
    "across your internal systems."
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
    st.caption(
        "How the app classifies requests when an API key is present; optional detail for reviewers."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mode", "Offline" if offline else "LLM + policy")
    with col2:
        st.metric("Classifier", settings.openai_chat_model if not offline else "heuristic")
    with col3:
        st.metric("Confidence threshold", f"{settings.classification_confidence_threshold:.2f}")
