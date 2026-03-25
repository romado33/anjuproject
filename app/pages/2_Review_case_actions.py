"""Single page: pipeline review, policy snapshot, approvals, and light metrics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui_theme import inject_theme, page_config, render_process_breadcrumb
from config.logging_config import configure_logging
from config.settings import get_settings
from src.models.case import ApprovalDecision, CaseStatus
from src.policy.engine import aggregate_operator_metrics, policy_controls_snapshot
from src.workflow.engine import CaseWorkflowEngine

configure_logging(get_settings().log_level)
page_config("Review case actions")
inject_theme()
render_process_breadcrumb(current="review")


@st.cache_resource
def get_engine() -> CaseWorkflowEngine:
    return CaseWorkflowEngine()


engine = get_engine()
cases = engine.list_cases(limit=80)

_FINAL_DECISIONS = frozenset({"approved", "modified", "rejected"})


def _progress_step(status: CaseStatus) -> int:
    if status in (
        CaseStatus.INTAKE,
        CaseStatus.CLASSIFYING,
        CaseStatus.RETRIEVING,
        CaseStatus.ROUTING,
        CaseStatus.PLANNING,
    ):
        return 1
    if status == CaseStatus.PENDING_APPROVAL:
        return 2
    if status in (CaseStatus.APPROVED, CaseStatus.REJECTED):
        return 3
    return 4

st.title("Review case actions")
st.caption("Review proposed actions, record decisions, and run mock downstream integrations.")

if not cases:
    st.warning("No cases yet. Start on **Case intake** to run a scenario.")
    st.stop()

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

step = _progress_step(case.status)
st.markdown("### Progress")
st.progress(step / 4)
step_labels = ["Intake", "Decision", "Approval", "Complete"]
label_line = " -> ".join(
    [f"**{name}**" if i + 1 == step else name for i, name in enumerate(step_labels)]
)
st.caption(label_line)

if case.status == CaseStatus.PENDING_APPROVAL:
    st.info(
        "Next step: choose **approved**, **modified**, or **rejected** for each action below, "
        "then click **Submit decisions**."
    )
elif case.status == CaseStatus.APPROVED:
    st.info(
        "Next step: click **Execute approved actions (mock)** to run the mock integrations."
    )
elif case.status == CaseStatus.COMPLETED:
    st.success("Case is complete — see **Audit log & export** below for the full trail.")
elif case.status == CaseStatus.REJECTED:
    st.warning("Case was rejected. Start again from **Case intake** if you want to retry.")

if case.routing:
    st.markdown("### Decision summary")
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f'<div class="demo-card"><div class="demo-kpi">Owning team</div>'
        f'<div class="demo-value">{case.routing.target_team}</div></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="demo-card"><div class="demo-kpi">Queue</div>'
        f'<div class="demo-value">{case.routing.queue_name}</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="demo-card"><div class="demo-kpi">SLA</div>'
        f'<div class="demo-value">{case.routing.sla_hours}h</div></div>',
        unsafe_allow_html=True,
    )

st.info(
    "The actions below are proposed by **deterministic policy for this case** (routing matrix, integration "
    "selection, LLM/RAG gates, restricted mode). **Policy & privacy** in the sidebar describes those controls — "
    "they are not a separate track; they run automatically on every intake."
)

st.subheader("Proposed actions & approvals")
if not case.proposed_actions:
    st.caption("No actions proposed.")
elif case.status == CaseStatus.PENDING_APPROVAL:
    reviewer = st.text_input("Reviewer name", value="Internal Reviewer", key="rev_name")
    st.caption(
        "For each row, pick **approved**, **modified**, or **rejected** — nothing is pre-selected."
    )

    for i, action in enumerate(case.proposed_actions):
        col_detail, col_decision = st.columns([1.25, 1])
        with col_detail:
            st.markdown(f"**{action.title}**")
            st.caption(f"{action.target_system} · {action.action_type.value}")
        with col_decision:
            st.radio(
                "Decision",
                ["approved", "modified", "rejected"],
                horizontal=True,
                index=None,
                key=f"dec_{case.case_id}_{action.id}",
                help="Choose one option before submitting.",
            )
        if st.session_state.get(f"dec_{case.case_id}_{action.id}") == "modified":
            st.text_area(
                "Modified payload JSON",
                value=json.dumps(action.payload, indent=2),
                key=f"mod_{case.case_id}_{action.id}",
                height=140,
            )
        if i < len(case.proposed_actions) - 1:
            st.divider()

    submit = st.button("Submit decisions", type="primary", use_container_width=True)

    if submit:
        out: list[ApprovalDecision] = []
        for action in case.proposed_actions:
            dec = st.session_state.get(f"dec_{case.case_id}_{action.id}")
            if dec not in _FINAL_DECISIONS:
                st.error(
                    f"Select **approved**, **modified**, or **rejected** for each action "
                    f"(missing decision for: {action.title})."
                )
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

else:
    approval_by_action = {a.action_id: a.decision for a in case.approvals}
    for action in case.proposed_actions:
        col_detail, col_status = st.columns([1.25, 1])
        with col_detail:
            st.markdown(f"**{action.title}**")
            st.caption(f"{action.target_system} · {action.action_type.value}")
        with col_status:
            recorded = approval_by_action.get(action.id)
            if recorded:
                st.caption(f"Recorded: **{recorded}**")
            else:
                st.caption("—")

    st.info(f"Current status: **{case.status.value}**.")
    if case.execution_results:
        with st.expander("Execution results", expanded=False):
            st.json(case.execution_results)

    if case.status == CaseStatus.APPROVED:
        execute_btn = st.button(
            "Execute approved actions (mock)",
            type="primary",
            use_container_width=True,
        )
        if execute_btn:
            try:
                final = engine.execute_approved(case_id)
            except Exception as exc:
                st.error(str(exc))
                st.stop()
            st.success(
                "Execution complete — results are stored on the case and **written to the audit trail**. "
                "Reopening this page shows the updated log below."
            )
            st.json(final.execution_results)
            st.rerun()

if case.audit_trail:
    st.markdown("### Audit log & export")
    st.markdown(
        "Every meaningful step for this case is stored as an **append-only audit entry**: classification, "
        "policy routing, redaction (if any), human approvals, and **each mock adapter run** after you execute. "
        "Use the exports for a compliance-style snapshot or handoff."
    )
    if case.status == CaseStatus.COMPLETED and case.execution_results:
        st.success(
            f"**{len(case.execution_results)}** executed action(s) are reflected in the audit trail "
            "(search for `adapter_execution` in the entries or review chronologically below)."
        )
    with st.expander(
        f"Recent audit entries ({len(case.audit_trail)} total)",
        expanded=case.status == CaseStatus.COMPLETED,
    ):
        for entry in case.audit_trail[-25:]:
            ts = entry.timestamp.isoformat(timespec="seconds")
            st.markdown(f"**{entry.step}** · `{ts}`")
            detail = entry.detail
            if len(detail) > 1_200:
                detail = detail[:1_200] + "…"
            st.caption(detail)
            if entry.metadata:
                st.json(entry.metadata)
            st.divider()
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "Download full case JSON",
            data=json.dumps(case.model_dump(mode="json"), indent=2),
            file_name=f"{case.case_id}.json",
            mime="application/json",
        )
    with dl2:
        audit_blob = json.dumps(
            {"case": case.model_dump(mode="json"), "export_schema": "anju-case-router/audit/v1"},
            indent=2,
        )
        st.download_button(
            "Download audit bundle JSON",
            data=audit_blob,
            file_name=f"audit-{case.case_id}.json",
            mime="application/json",
        )

with st.expander("Advanced details", expanded=False):
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

    # --- Policy snapshot (compact) ---
    snap = policy_controls_snapshot(case)
    st.markdown("#### Policy snapshot")
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

    st.markdown("#### Classification")
    if case.classification:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Product", case.classification.product.value)
        c2.metric("Issue type", case.classification.issue_type.value)
        c3.metric("Urgency", case.classification.urgency.value)
        c4.metric("Confidence", f"{case.classification.confidence:.2f}")
        st.markdown("**Reasoning**")
        st.write(case.classification.reasoning)

    st.markdown("#### Retrieval")
    if case.rag_influence_summary:
        st.info(case.rag_influence_summary)
    if case.rag_skipped is True:
        st.caption("RAG was skipped by policy (see audit `rag_skipped`).")

    with st.expander("KB chunks", expanded=False):
        if case.rag_context:
            for i, ch in enumerate(case.rag_context, start=1):
                meta = ch.get("metadata") or {}
                st.markdown(f"**Chunk {i}** — {meta.get('source_file', 'unknown')}")
                st.caption(f"distance={ch.get('distance')}")
                st.write(ch.get("document", ""))
        else:
            st.caption("No chunks (offline, policy skip, or empty KB).")
