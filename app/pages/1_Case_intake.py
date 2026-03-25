"""Submit a new case or load a sample scenario."""

from __future__ import annotations

import html
import json
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
from src.showcase_scenarios import (
    SCENARIOS,
    SHOWCASE_BUTTON_LABELS,
    SHOWCASE_KEYS,
    load_showcase_scenarios,
)
from src.models.case import CaseIntake
from src.rag.retriever import chunk_and_embed_kb
from src.rag.vector_store import SqliteVectorStore
from src.workflow.engine import CaseWorkflowEngine

configure_logging(get_settings().log_level)
page_config("Case intake")
inject_theme()
render_process_breadcrumb(current="intake")
render_luminee_sidebar_promo()


@st.cache_resource
def get_engine() -> CaseWorkflowEngine:
    return CaseWorkflowEngine()


@st.cache_resource
def ensure_kb() -> str:
    settings = get_settings()
    if settings.use_offline_mode():
        return "offline"
    try:
        store = SqliteVectorStore(settings)
        if store.count() > 0:
            return f"ready:{store.count()}"
        kb_dir = ROOT / "data" / "knowledge_base"
        n = chunk_and_embed_kb(settings, kb_dir, reset=False)
        return f"seeded:{n}"
    except Exception:
        # Keep intake usable even if local LangChain/OpenAI deps are mismatched.
        return "unavailable"


def _run_case(
    *,
    request_text: str,
    submitter: str,
    submitter_email: str,
    redact: bool,
    redaction_policy: str,
) -> None:
    intake = CaseIntake(
        request_text=request_text,
        source_channel="streamlit_intake",
        submitter_name=submitter or None,
        submitter_email=submitter_email or None,
        redact_pii=redact,
        redaction_policy=redaction_policy,  # type: ignore[arg-type]
    )
    with st.spinner("Running case analysis..."):
        try:
            case = get_engine().start_case(intake)
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
            st.stop()

    st.session_state["active_case_id"] = case.case_id
    st.session_state["last_case_snapshot"] = json.loads(case.model_dump_json())
    st.success(f"Case `{case.case_id}` processed — status `{case.status.value}`.")
    try:
        st.page_link(
            "pages/2_Review_case_actions.py",
            label="Continue to Review case actions →",
            use_container_width=True,
        )
    except Exception:
        st.markdown("Open **Review case actions** to review reasoning, policy, and sign-off.")


st.title("Case intake")
kb_status = ensure_kb()
settings = get_settings()
offline = settings.use_offline_mode()
st.caption(
    "Each scenario run applies **internal policy** automatically (classification, routing, which actions are "
    "proposed, LLM/RAG and restricted-content gates). On **Review case actions**, each case shows how those "
    "controls shaped the proposals, with a link to the full **Policy & privacy** reference."
)
if kb_status == "unavailable":
    st.warning(
        "Knowledge retrieval is temporarily unavailable in this environment. "
        "You can still run the full policy and approval flow; cases will continue without KB chunks."
    )
st.markdown("### Sample scenarios")
st.caption(
    "Pick one typical path — each runs the same routing pipeline, then waits for human approval."
)
showcase = load_showcase_scenarios()
row1 = st.columns(2)
row2 = st.columns(2)
for idx, scenario in enumerate(showcase):
    col = row1[idx] if idx < 2 else row2[idx - 2]
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="workflow-kpi">{html.escape(scenario.title)}</div>'
                f'<div class="workflow-value" style="font-weight:400;font-size:0.95rem;">'
                f"{html.escape(scenario.description)}</div>",
                unsafe_allow_html=True,
            )
            btn_label = SHOWCASE_BUTTON_LABELS.get(scenario.key, f"Run: {scenario.title}")
            if st.button(btn_label, type="primary", use_container_width=True, key=f"showcase_run_{scenario.key}"):
                _run_case(
                    request_text=scenario.request_text,
                    submitter="Sample User",
                    submitter_email="sample@example.com",
                    redact=True,
                    redaction_policy="strict",
                )

with st.expander("More scenarios (CRM, cross-product)", expanded=False):
    extra = [s for s in SCENARIOS if s.key not in SHOWCASE_KEYS]
    scenario_labels = {f"{s.title} ({s.key})": s for s in extra}
    if not scenario_labels:
        st.caption("No additional scenarios configured.")
    else:
        choice = st.selectbox("Scenario", list(scenario_labels.keys()))
        selected = scenario_labels[choice]

        default_text = st.text_area(
            "Request text",
            value=selected.request_text,
            height=220,
            help="Paste an email, portal ticket, or Teams message body.",
        )

        submitter = st.text_input("Submitter name", value="Sample User")
        submitter_email = st.text_input("Submitter email", value="sample@example.com")
        redact = st.checkbox(
            "Redact identifiers",
            value=True,
        )
        redaction_policy = st.selectbox(
            "Redaction policy",
            options=["standard", "strict"],
            index=1,
            disabled=not redact,
        )

        if st.button("Run selected case", type="primary", use_container_width=True):
            _run_case(
                request_text=default_text,
                submitter=submitter,
                submitter_email=submitter_email,
                redact=redact,
                redaction_policy=redaction_policy,
            )

with st.expander("System status", expanded=False):
    st.markdown(
        f"- Mode: **{'offline' if offline else 'LLM + embeddings'}**  \n"
        f"- KB status: **{kb_status}**  \n"
        "- Privacy controls: redaction + restricted-content gate"
    )
