"""Single page: pipeline review, policy snapshot, approvals, and light metrics."""

from __future__ import annotations

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
from src.models.case import ApprovalDecision, CaseRecord, CaseStatus, ProposedAction
from src.workflow.engine import CaseWorkflowEngine

configure_logging(get_settings().log_level)
page_config("Review case actions")
inject_theme()
render_process_breadcrumb(current="review")
render_luminee_sidebar_promo()


@st.cache_resource
def get_engine() -> CaseWorkflowEngine:
    return CaseWorkflowEngine()


engine = get_engine()
cases = engine.list_cases(limit=80)

_FINAL_DECISIONS = frozenset({"approved", "modified", "rejected"})


def _render_concise_case_snapshot(case: CaseRecord) -> None:
    """Short per-case blurb after AI / privacy explainers (Policy & privacy lives in the sidebar)."""
    if case.proposed_actions:
        n = len(case.proposed_actions)
        systems = sorted({a.target_system for a in case.proposed_actions})
        n_types = len({a.action_type for a in case.proposed_actions})
        if len(systems) > 4:
            sys_str = ", ".join(systems[:3]) + f", +{len(systems) - 3} more"
        else:
            sys_str = ", ".join(systems)
        st.markdown(
            f"**{n}** proposed actions to **{sys_str}** ({n_types} action types). "
            "Human approval and mock runs use the **same audit trail**."
        )
    else:
        st.markdown(
            "No downstream actions on this case; intake, classification, and routing still ran under policy."
        )

    sig: list[str] = []
    if case.restricted_mode:
        sig.append("restricted path (no external LLM)")
    if case.rag_skipped is True:
        sig.append("RAG skipped")
    elif case.rag_skipped is False:
        sig.append("RAG applied")
    if not case.llm_allowed:
        sig.append("LLM off")
    elif not case.restricted_mode:
        sig.append("LLM allowed")
    if sig:
        st.caption("Case signals: " + " · ".join(sig) + ".")

    st.caption(
        "Routing and integrations follow the **policy matrix and safety gates**. "
        "For architecture, retention, and compliance detail, open **Policy & privacy** in the sidebar."
    )


def _render_ai_workflow_expander() -> None:
    with st.expander("How AI is used in this workflow", expanded=False):
        st.markdown(
            """
**During case intake (before this page)**

- **LLM classification** (OpenAI structured output) runs when an API key is configured, the pipeline is not in **offline** mode, and **restricted** content policy does not block external models. It assigns product, issue type, urgency, and confidence.
- **Embeddings + RAG** may retrieve KB chunks to inform routing when policy allows; otherwise retrieval is **skipped** and noted on the case.
- **Team routing, SLA, and proposed actions** are produced by **deterministic policy rules** using that classification (and optional KB context)—not ad-hoc LLM prose for each action.
- **Offline or restricted intakes** skip external LLM and/or retrieval; classification falls back to **keyword heuristics**.

**On this review screen**

- **No AI**: approvals and edits are human decisions; **Execute** runs **mock adapters** only.
            """
        )


def _render_privacy_policy_expander(case: CaseRecord) -> None:
    with st.expander("How privacy policies are applied in this workflow", expanded=False):
        st.markdown(
            """
**At intake**

- **Restricted-content rules** can disable external LLM and embedding retrieval; processing stays on-policy and **audited**.
- **Redaction** (when enabled on submit) limits what crosses the boundary before classification and retrieval.
- **RAG** is allowed or skipped based on product/risk policy—not every case hits the knowledge base.

**On this review screen**

- Approvals are **append-only** in the audit log; **mock execution** does not change production data in this demo.
            """
        )
        bits: list[str] = []
        if case.restricted_mode:
            bits.append("restricted intake (signals detected)")
        if case.rag_skipped is True:
            bits.append("RAG skipped for this case")
        elif case.rag_skipped is False:
            bits.append("RAG ran where policy allowed")
        if bits:
            st.caption("**This case:** " + " · ".join(bits) + ".")


def _proposed_action_details_expander_label(title: str, action_id: str) -> str:
    t = (title or "").strip() or "Untitled action"
    if len(t) > 48:
        t = t[:47] + "…"
    sid = action_id[:8]
    return f"View action details — {t} · `{sid}`"


def _render_proposed_action_details(action: ProposedAction) -> None:
    """Rationale and payload for reviewers (policy planner output + adapter-bound JSON)."""
    with st.expander(_proposed_action_details_expander_label(action.title, action.id), expanded=False):
        st.markdown("**Policy / planner rationale**")
        st.write(action.reasoning.strip() if action.reasoning else "*No reasoning recorded.*")
        st.markdown("**Adapter payload** (shape sent to the downstream / mock integration)")
        st.json(action.payload)
        st.caption(
            f"Action ID `{action.id}` · `{action.action_type.value}` · **{action.target_system}**"
        )


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

st.subheader("Proposed actions & approvals")
ai_col, priv_col = st.columns(2)
with ai_col:
    _render_ai_workflow_expander()
with priv_col:
    _render_privacy_policy_expander(case)

_render_concise_case_snapshot(case)

if case.proposed_actions:
    st.markdown("---")

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
        _render_proposed_action_details(action)
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
        _render_proposed_action_details(action)

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
