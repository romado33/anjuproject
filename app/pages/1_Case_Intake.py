"""Submit a new case or load a sample scenario."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui_theme import inject_theme, page_config
from config.logging_config import configure_logging
from config.settings import get_settings
from src.demo_scenarios import SCENARIOS
from src.models.case import CaseIntake
from src.rag.retriever import chunk_and_embed_kb
from src.rag.vector_store import SqliteVectorStore
from src.workflow.engine import CaseWorkflowEngine

configure_logging(get_settings().log_level)
page_config("Case Intake")
inject_theme()


@st.cache_resource
def get_engine() -> CaseWorkflowEngine:
    return CaseWorkflowEngine()


@st.cache_resource
def ensure_kb() -> str:
    settings = get_settings()
    if settings.use_offline_mode():
        return "offline"
    store = SqliteVectorStore(settings)
    if store.count() > 0:
        return f"ready:{store.count()}"
    kb_dir = ROOT / "data" / "knowledge_base"
    n = chunk_and_embed_kb(settings, kb_dir, reset=False)
    return f"seeded:{n}"


st.title("Case intake")
kb_status = ensure_kb()
settings = get_settings()
offline = settings.use_offline_mode()
st.caption(
    f"Single intake for **case-to-action automation** (support, PS, compliance handoffs — not ticket triage only). "
    f"KB: **{kb_status}** · Mode: **{'offline (no OpenAI)' if offline else 'LLM + embeddings'}**. "
    "**Restricted-content** signals skip external models — see **Policy & privacy**."
)

try:
    st.page_link(
        "pages/3_Policy_and_Privacy.py",
        label="Policy & privacy (controls & compliance)",
    )
except Exception:
    st.markdown("*See sidebar: Policy & privacy for restricted gate and redaction.*")

scenario_labels = {f"{s.title} ({s.key})": s for s in SCENARIOS}
choice = st.selectbox("Demo scenario (or write your own below)", list(scenario_labels.keys()))
selected = scenario_labels[choice]

default_text = st.text_area(
    "Request text",
    value=selected.request_text,
    height=220,
    help="Paste an email, portal ticket, or Teams message body.",
)

submitter = st.text_input("Submitter name (optional)", value="Demo User")
submitter_email = st.text_input("Submitter email (optional)", value="demo@example.com")
redact = st.checkbox(
    "Redact direct identifiers before LLM / embeddings",
    value=True,
    help="Masks common email/phone patterns. Recommended on for interviews; use strict for trial/site-style tokens.",
)
redaction_policy = st.selectbox(
    "Redaction policy",
    options=["standard", "strict"],
    index=1,
    help="Strict: email/phone plus NCT IDs, site # patterns, study-style tokens (portfolio heuristic — production would use DLP).",
    disabled=not redact,
)

if st.button("Run pipeline", type="primary", use_container_width=True):
    intake = CaseIntake(
        request_text=default_text,
        source_channel="streamlit_intake",
        submitter_name=submitter or None,
        submitter_email=submitter_email or None,
        redact_pii=redact,
        redaction_policy=redaction_policy,  # type: ignore[arg-type]
    )
    with st.spinner("Classifying → optional RAG → policy routing → proposed actions…"):
        try:
            case = get_engine().start_case(intake)
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
            st.stop()

    st.session_state["active_case_id"] = case.case_id
    st.session_state["last_case_snapshot"] = json.loads(case.model_dump_json())
    st.success(f"Case `{case.case_id}` processed — status `{case.status.value}`.")
    st.markdown("Open **Case run** to review reasoning, policy snapshot, and approvals.")

with st.expander("Setup & privacy notes"):
    st.markdown(
        "- Offline mode works without API keys (keyword routing).  \n"
        "- Full mode requires `OPENAI_API_KEY` and a seeded KB (`python scripts/seed_knowledge_base.py`).  \n"
        "- **Privacy:** see `docs/PRIVACY_AND_COMPLIANCE.md`; use synthetic scenarios for demos."
    )
