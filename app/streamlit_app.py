"""
Anju Internal Case Router — Streamlit entry point.

Run from project root:
  pip install -r requirements.txt
  python scripts/seed_knowledge_base.py
  streamlit run app/streamlit_app.py
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

from app.ui_theme import inject_theme
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

    settings = get_settings()
    offline = settings.use_offline_mode()

    st.sidebar.title("Navigation")
    st.sidebar.caption("Internal automation — policy-governed routing (portfolio build).")

    if offline:
        st.sidebar.info(
            "Offline mode: no `OPENAI_API_KEY`. Keyword classification; retrieval skipped when policy requires API."
        )
    else:
        st.sidebar.success("OpenAI configured — LLM + embeddings enabled where policy allows.")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Mock adapters:** Jira · Teams · Salesforce · NetSuite · BambooHR · Wiki checklist"
    )

    st.title("Anju Internal Case Router")
    st.markdown(
        "**Case-to-action automation** across internal systems (support, PS, compliance, customer ops): "
        "classify inbound work, **conditionally** retrieve internal context, apply **deterministic policy** "
        "for routing and selective actions, then **human approval** before mock execution."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mode", "Offline" if offline else "LLM + policy")
    with col2:
        st.metric("Classifier", settings.openai_chat_model if not offline else "heuristic")
    with col3:
        st.metric("Confidence threshold", f"{settings.classification_confidence_threshold:.2f}")

    st.markdown("### Start here (three pages)")
    st.markdown(
        "1. **Case intake** — submit or load a scenario.  \n"
        "2. **Case run** — pipeline output, policy snapshot, approvals, export.  \n"
        "3. **Policy & privacy** — architecture, restricted gate, compliance talk track."
    )

    st.markdown(
        "**Docs:** `docs/PRIVACY_AND_COMPLIANCE.md` · `docs/INTERVIEW.md` · `docs/WORKFLOW_DISCOVERY.md` (as-is vs to-be narrative)."
    )

    with st.expander("Setup tip"):
        st.markdown(
            "Seed the knowledge base with `python scripts/seed_knowledge_base.py` after setting "
            "`OPENAI_API_KEY`. Enable redaction on intake to show data minimization before model calls."
        )


if __name__ == "__main__":
    main()
