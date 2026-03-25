# Demo walkthrough — Anju Internal Case Router

Use this script for a **5–10 minute** walkthrough of the Streamlit app. Paths assume you run from the repo root with `PYTHONPATH=.` (see [README.md](../README.md)).

## Before you start

1. Install dependencies and configure `.env` from `.env.example`.
2. Optional but recommended: `python scripts/seed_knowledge_base.py` (needs `OPENAI_API_KEY`) so RAG can retrieve from `data/knowledge_base/`.
3. Start the app: `streamlit run app/Home.py` (or `python -m streamlit run app/Home.py`).

## App structure (sidebar)

| Sidebar label        | File                          | Role |
|---------------------|-------------------------------|------|
| **Home**            | `app/pages/0_Home.py` (via `st.navigation` in `app/Home.py`) | Landing, links into the workflow |
| **Case intake**     | `app/pages/1_Case_intake.py`  | Run demo scenarios, optional custom text |
| **Review case actions** | `app/pages/2_Review_case_actions.py` | Approvals, mock execute, audit export |
| **Policy & privacy** | `app/pages/3_Policy_and_Privacy.py` | Reference: controls and compliance narrative (open from sidebar on any page) |

Entry scripts **`app/Home.py`** and **`app/streamlit_app.py`** only register pages; they do not hold the landing UI. Sidebar titles come from `st.Page(…, title=…)`, so the first item stays **Home** even when launching `streamlit_app.py`.

**Home** adds custom sidebar content below the nav: a short **mock adapters** line (Jira, Teams, CRM, etc.) and the **Luminee** promo block (`render_luminee_sidebar_promo()` in `app/ui_theme.py`).

**Case workflow** breadcrumb (top of Home, Case intake, Review case actions): **Overview → Case intake → Review case actions** only. **Policy & privacy** is **reference** material (separate page from the sidebar), not a workflow step.

---

## 1. Home

- Summarize the one-liner value prop (card under the title).
- Expand **Model & routing settings** if you need to show mode (offline vs LLM + policy), classifier model, and confidence threshold.
- **Start**: link to Case intake, then Review case actions.
- Sidebar: **mock adapters** line + **Luminee** promo (no duplicate “Navigation” header or OpenAI status strip).

**Talking point:** Policy is enforced **inside** each case run; open **Policy & privacy** from the sidebar for the full prose reference.

---

## 2. Case intake

- **Next step** card explains intake → review.
- **Four demo scenarios** (2×2): typical Anju paths — IRMS implementation, FDA/TrialMaster compliance, TrialMaster export, TA Scan feasibility. Each primary button runs the full pipeline and lands in `pending_approval` when complete.
- **More scenarios** expander: CRM routing, cross-product (not in the main four).
- After a run: success message, **Continue to Review case actions**.
- There is **no** full-width Policy link on this page; reviewers see contextual policy copy and the **Policy & privacy** sidebar entry when they reach **Review case actions**.

**Talking point:** `CaseIntake` is normalized in `CaseWorkflowEngine.start_case` so Streamlit hot-reload + cached engine do not break Pydantic validation.

---

## 3. Review case actions

- **Progress** bar and status hints.
- **Decision summary** (team, queue, SLA) when routing exists.
- **Proposed actions & approvals** section (in order):
  - Side-by-side expanders: **How AI is used in this workflow** and **How privacy policies are applied in this workflow**.
  - A **concise case snapshot** (counts, systems, case signals: RAG/LLM/restricted) and a caption pointing to **Policy & privacy** in the **sidebar** (no in-page Policy banner).
  - **Suggested actions**: each row = title, system, type, decision radios (**approved / modified / rejected**) — nothing pre-selected; **View action details** expanders show planner rationale and JSON payload.
- **Submit decisions** → status becomes `approved` or `rejected` if **all** actions rejected.
- **Execute approved actions (mock)** appears only when **approved**; rejected actions are **skipped** on execute; modified payloads are passed through.

**Talking point:** Partial approval: case can be `approved` with some actions rejected; execution runs only approved/modified lines.

- **Audit log & export**: append-only trail (classification, policy, approvals, `adapter_execution`). Recent entries expander; download full case or audit bundle JSON.

---

## 4. Policy & privacy

- **Reference** strip: link back to Overview, note that this is not a workflow step.
- Architecture table (LLM vs policy), restricted gate, embedded compliance doc if present.
- Optional read-only policy snapshot for a stored case.

---

## If something goes wrong

| Symptom | Mitigation |
|---------|------------|
| No API key | Offline mode — same UI; heuristic classification; RAG skipped when policy would call embeddings |
| RAG / KB errors | Intake shows warning; pipeline continues without chunks |
| Stale Streamlit cache after code edits | **Clear cache** or restart Streamlit |
| `CaseRecord` validation on intake | Restart app after pulls; engine normalizes intake from dict |

---

## Suggested demo pairs (for interviews)

1. **IRMS MAX implementation** — PS routing, many proposed actions, checklist story.  
2. **FDA / TrialMaster audit prep** — compliance routing, audit-adjacent narrative.

See also [ARCHITECTURE.md](ARCHITECTURE.md) for the pipeline diagram and file map.
