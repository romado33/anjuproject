"""Single page: pipeline review, policy snapshot, approvals, and light metrics."""

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
from src.models.case import ApprovalDecision
from src.policy.engine import aggregate_operator_metrics, policy_controls_snapshot
from src.workflow.engine import CaseWorkflowEngine

from config.settings import get_settings

configure_logging(get_settings().log_level)
page_config("Case run")
inject_theme()


@st.cache_resource
def get_engine() -> CaseWorkflowEngine:
    return CaseWorkflowEngine()


engine = get_engine()
cases = engine.list_cases(limit=80)

st.title("Case run")
st.caption(
    "**Case-to-action automation** across internal systems: classify, optional RAG, deterministic routing, "
    "selective proposed actions — **policy snapshot** and **human approval** before mock execution."
)

if not cases:
    st.warning("No cases yet. Use **Case intake** first.")
    st.stop()

# --- Metrics: pipeline state + operator-style signals ---
rag_skipped_n = sum(1 for c in cases if c.rag_skipped)
restricted_n = sum(1 for c in cases if c.restricted_mode)
pending_n = sum(1 for c in cases if c.status.value == "pending_approval")
agg = aggregate_operator_metrics(cases)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Cases stored", len(cases))
m2.metric("Pending approval", pending_n)
m3.metric("Restricted (policy gate)", restricted_n)
m4.metric("RAG skipped (policy)", f"{rag_skipped_n} / {len(cases)}")

o1, o2, o3, o4 = st.columns(4)
o1.metric("Handoffs reduced (est.)", f"{agg['handoffs_reduced_est']:.1f}")
o2.metric("No external LLM path", f"{agg['cases_without_external_llm']} / {len(cases)}")
o3.metric("No Jira proposed (selective)", f"{agg['cases_no_jira_ticket']} / {len(cases)}")
o4.metric("Elevated human review", f"{agg['cases_elevated_review']} / {len(cases)}")
st.caption(
    "Handoffs reduced compares an illustrative pre-automation systems-touch baseline (4.2) to mean proposed actions. "
    "No-Jira counts cases where policy chose CRM/Teams-only or similar."
)

# --- Case selector ---
labels = []
for c in cases:
    mark = ""
    if c.case_id == st.session_state.get("active_case_id"):
        mark = " · active"
    labels.append(f"{c.case_id[:8]}… — {c.status.value}{mark}")

default_idx = 0
if "active_case_id" in st.session_state:
    for i, c in enumerate(cases):
        if c.case_id == st.session_state["active_case_id"]:
            default_idx = i
            break

sel_label = st.selectbox("Select case", labels, index=default_idx)
case_id = cases[labels.index(sel_label)].case_id

case = engine.get_case(case_id)
if case is None:
    st.error("Case not found.")
    st.stop()

# --- Policy snapshot (compact) ---
snap = policy_controls_snapshot(case)
with st.expander("Policy snapshot", expanded=False):
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Risk tier", snap["risk_tier"])
    p2.metric("LLM allowed", "yes" if snap["llm_allowed"] else "no")
    p3.metric("RAG skipped", "yes" if snap["rag_skipped"] else "no")
    p4.metric("Elevated review", "yes" if snap["elevated_human_review"] else "no")
    if case.restricted_mode:
        st.warning(
            "Restricted case: external LLM and embedding retrieval were not used for this intake."
        )
    for note in snap["policy_notes"]:
        st.caption(note)

# --- Intake & classification ---
if case.restricted_mode:
    st.error(
        "Restricted-content signals detected — deterministic path only. "
        "See **Policy & privacy** for what triggers this."
    )

st.subheader("Intake")
if case.redacted_request_text:
    st.caption(
        "Redaction was applied for model calls. Original below; models used the redacted variant."
    )
st.text(case.intake.request_text[:8000])
if case.redacted_request_text:
    with st.expander("Text sent to models (redacted)"):
        st.text(case.redacted_request_text[:8000])

if case.classification:
    st.subheader("Classification")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Product", case.classification.product.value)
    c2.metric("Issue type", case.classification.issue_type.value)
    c3.metric("Urgency", case.classification.urgency.value)
    c4.metric("Confidence", f"{case.classification.confidence:.2f}")
    st.markdown("**Reasoning**")
    st.write(case.classification.reasoning)

st.subheader("Retrieval")
if case.rag_influence_summary:
    st.info(case.rag_influence_summary)
if case.rag_skipped is True:
    st.caption("RAG was skipped by policy (see audit `rag_skipped`).")

with st.expander("KB chunks (if any)"):
    if case.rag_context:
        for i, ch in enumerate(case.rag_context, start=1):
            meta = ch.get("metadata") or {}
            st.markdown(f"**Chunk {i}** — {meta.get('source_file', 'unknown')}")
            st.caption(f"distance={ch.get('distance')}")
            st.write(ch.get("document", ""))
    else:
        st.caption("No chunks (offline, policy skip, or empty KB).")

if case.routing:
    st.subheader("Routing")
    r1, r2, r3 = st.columns(3)
    r1.metric("Team", case.routing.target_team)
    r2.metric("Queue", case.routing.queue_name)
    r3.metric("SLA (h)", case.routing.sla_hours)
    st.write(case.routing.reasoning)

st.subheader("Proposed actions")
if not case.proposed_actions:
    st.caption("None.")
else:
    for a in case.proposed_actions:
        st.markdown(f"**{a.title}** · `{a.action_type.value}` → {a.target_system}")
        st.caption(a.reasoning)
        with st.expander("Payload"):
            st.json(a.payload)

# --- Approvals & execution (pending only) ---
st.subheader("Approvals & execution")
if case.status.value != "pending_approval":
    st.info(
        f"This case is **{case.status.value}**. Approvals apply when status is `pending_approval`."
    )
    if case.execution_results:
        with st.expander("Execution results (mock)"):
            st.json(case.execution_results)
else:
    reviewer = st.text_input("Reviewer name", value="Internal Reviewer", key="rev_name")

    for action in case.proposed_actions:
        st.markdown(f"#### {action.title}")
        st.caption(f"{action.action_type.value} · {action.target_system}")
        st.radio(
            "Decision",
            ["approved", "modified", "rejected"],
            horizontal=True,
            key=f"dec_{case.case_id}_{action.id}",
        )
        if st.session_state.get(f"dec_{case.case_id}_{action.id}", "approved") == "modified":
            st.text_area(
                "Replace payload JSON",
                value=json.dumps(action.payload, indent=2),
                key=f"mod_{case.case_id}_{action.id}",
                height=140,
            )
        st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        submit = st.button("Submit decisions", type="primary", use_container_width=True)
    with col_b:
        execute_btn = st.button(
            "Execute approved actions (mock)",
            use_container_width=True,
        )

    if submit:
        out: list[ApprovalDecision] = []
        for action in case.proposed_actions:
            dec = st.session_state.get(f"dec_{case.case_id}_{action.id}", "approved")
            if dec not in ("approved", "modified", "rejected"):
                st.error(f"Missing decision for action {action.id}")
                st.stop()
            mod_payload = None
            if dec == "modified":
                raw = st.session_state.get(f"mod_{case.case_id}_{action.id}", "")
                try:
                    mod_payload = json.loads(raw)
                except json.JSONDecodeError as exc:
                    st.error(f"Invalid JSON for action {action.id}: {exc}")
                    st.stop()
            out.append(
                ApprovalDecision(
                    action_id=action.id,
                    decision=dec,  # type: ignore[arg-type]
                    reviewer=reviewer or "demo_reviewer",
                    modified_payload=mod_payload,
                )
            )
        updated = engine.apply_approvals(case_id, out)
        st.success(f"Recorded — case status: **{updated.status.value}**")
        st.session_state["active_case_id"] = case_id
        st.rerun()

    if execute_btn:
        try:
            final = engine.execute_approved(case_id)
        except Exception as exc:
            st.error(str(exc))
            st.stop()
        st.success("Execution complete (mock adapters).")
        st.json(final.execution_results)
        st.rerun()

# --- Export ---
with st.expander("Audit trail & export"):
    st.json([e.model_dump(mode="json") for e in case.audit_trail[-40:]])
    st.download_button(
        "Download full case JSON",
        data=json.dumps(case.model_dump(mode="json"), indent=2),
        file_name=f"{case.case_id}.json",
        mime="application/json",
    )
    audit_blob = json.dumps(
        {"case": case.model_dump(mode="json"), "export_schema": "anju-case-router/audit/v1"},
        indent=2,
    )
    st.download_button(
        "Download audit JSON",
        data=audit_blob,
        file_name=f"audit-{case.case_id}.json",
        mime="application/json",
    )
