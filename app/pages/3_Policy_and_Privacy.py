"""Policy-first architecture, restricted gate, and privacy/compliance narrative."""

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
from src.policy.engine import policy_controls_snapshot
from src.workflow.engine import CaseWorkflowEngine

configure_logging(get_settings().log_level)
page_config("Policy & privacy")
inject_theme()

PRIVACY_PATH = ROOT / "docs" / "PRIVACY_AND_COMPLIANCE.md"

st.title("Policy & privacy")
st.caption(
    "How **interpretation** (LLM) stays separate from **control** (deterministic policy, "
    "human approval, and restricted-content handling)."
)

st.markdown(
    """
### Architecture: LLM vs policy

| Layer | Role |
|-------|------|
| **Classification** | LLM (when allowed) or offline heuristics — interprets product, issue, urgency |
| **Retrieval** | Only when policy says so — skip for low-risk/high-confidence paths |
| **Routing & actions** | **Deterministic policy** — selective integrations, not a fixed bundle every time |
| **Restricted gate** | Regex-style signals (PHI/AE language, trial IDs, etc.) → **no external LLM or embeddings** |
| **Approval** | Human gate before any mocked write to Jira, Teams, CRM, etc. |

### Restricted-case gate (heuristic detection)

If inbound text matches high-risk patterns (e.g. adverse event language, subject/patient identifiers, NCT IDs),
the pipeline uses **keyword classification + policy actions only** — external models and embedding calls are skipped.
In production this would be **data classification + DLP**, not regular expressions alone.
"""
)

st.markdown("### Privacy & compliance (summary)")
if PRIVACY_PATH.is_file():
    st.markdown(PRIVACY_PATH.read_text(encoding="utf-8"))
else:
    st.warning(f"Could not load `{PRIVACY_PATH}`.")

st.markdown("---")
st.markdown("### Optional: policy snapshot for a stored case")


@st.cache_resource
def _engine() -> CaseWorkflowEngine:
    return CaseWorkflowEngine()


engine = _engine()
cases = engine.list_cases(limit=40)
if cases:
    opts = {f"{c.case_id[:8]}… — {c.status.value}": c.case_id for c in cases}
    pick = st.selectbox("Case (read-only snapshot)", list(opts.keys()))
    cid = opts[pick]
    case = engine.get_case(cid)
    if case:
        snap = policy_controls_snapshot(case)
        st.json(snap)
        st.download_button(
            "Download policy snapshot JSON",
            data=json.dumps(snap, indent=2),
            file_name=f"policy-{cid[:8]}.json",
            mime="application/json",
        )
else:
    st.caption("No cases yet — run **Case intake** first.")
