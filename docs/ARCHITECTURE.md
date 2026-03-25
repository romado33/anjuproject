# Architecture — Anju Internal Case Router

Technical reference for the repository: layout, runtime pipeline, Streamlit UI, and where to change behavior. Paths are relative to the project root (`anju-case-router/`).

## One-sentence summary

A Python + **Streamlit** app that classifies inbound internal work, optionally retrieves knowledge (**RAG** when **policy** allows), applies **deterministic** routing and **selective** proposed actions (Jira, Teams, CRM, NetSuite, BambooHR, checklist mocks), requires **human approval** per action, then runs **mock** adapter execution with an **append-only audit trail** persisted to SQLite.

## Design principle

**The LLM interprets ambiguity (classification only). Deterministic policy governs routing, which integrations appear, RAG on/off, and restricted-mode behavior.**

Routing and action planning are **not** free-form LLM plans; they come from `src/policy/engine.py` and LangGraph nodes that call that engine.

---

## Repository layout

```
anju-case-router/
├── app/
│   ├── Home.py                      # Entry: st.navigation — explicit sidebar titles
│   ├── streamlit_app.py             # Same behavior as Home.py (legacy filename)
│   ├── run_multipage.py             # st.Page list: Home, Case intake, Review, Policy
│   ├── ui_theme.py                  # CSS, breadcrumbs, Luminee promo, policy reference nav
│   └── pages/
│       ├── 0_Home.py                # Landing body (sidebar label: Home)
│       ├── 1_Case_intake.py        # Sample scenarios + optional custom intake
│       ├── 2_Review_case_actions.py  # Approvals, AI/privacy expanders, per-action details, execute, audit export
│       ├── 4_Integrations.py       # Adapter base URLs / parameters (JSON via Settings)
│       └── 3_Policy_and_Privacy.py # Reference: architecture + compliance markdown
│
├── src/
│   ├── agent/
│   │   ├── orchestrator.py        # Restricted gate → offline or LangGraph graph
│   │   ├── offline.py             # Keyword classification (no OpenAI)
│   │   ├── classifier.py          # OpenAI structured classification
│   │   ├── context_gatherer.py    # Conditional RAG node
│   │   ├── policy_nodes.py        # route_from_policy, build_actions_from_policy
│   │   ├── llm.py
│   │   └── state.py               # LangGraph state
│   ├── policy/
│   │   ├── engine.py              # RAG policy, routing matrix, action matrix, snapshots
│   │   └── restricted.py        # Restricted-content heuristic gate
│   ├── models/case.py             # CaseRecord, CaseIntake, Classification, etc.
│   ├── rag/                       # Chunking, embeddings, SQLite vector store
│   ├── integrations/            # Mock adapters + registry dispatch
│   ├── workflow/
│   │   ├── engine.py              # start_case, apply_approvals, execute_approved
│   │   └── store.py               # SQLite JSON persistence for cases
│   ├── utils/pii.py
│   └── showcase_scenarios.py      # Curated showcase keys + `load_showcase_scenarios()`
│
├── data/knowledge_base/          # Markdown corpus for RAG
├── config/settings.py            # Pydantic Settings (.env)
├── tests/                        # pytest (no API key required)
├── scripts/seed_knowledge_base.py
└── docs/                         # This folder + compliance source for Policy page
```

---

## Pipeline (end-to-end)

When intake runs (`CaseWorkflowEngine.start_case` → `run_agent_pipeline`):

1. **Restricted gate** (`orchestrator` + `analyze_restricted`) — regex-style signals may force **no external LLM/embeddings** and keyword classification.
2. **Classification** — `classifier.py` (OpenAI structured output) or `offline.py` (keywords) → `Classification`.
3. **Conditional RAG** (`context_gatherer` + `should_retrieve_context`) — policy may skip retrieval (cost, latency, restricted path).
4. **Deterministic routing** (`policy_nodes` → `route_from_policy`) — team, queue, SLA; optional KB nudges.
5. **Selective actions** (`build_actions_from_policy`) — not every ticket gets every integration; matrix depends on product/issue/urgency/tier.
6. **Persist** — `CaseStore` upserts `CaseRecord`; UI opens **Review case actions** for approvals.
7. **Human approval** — per-action **approved / modified / rejected**; submit validates all choices.
8. **Mock execution** — `execute_approved` dispatches only approved/modified actions; each run appends **audit** entries (`adapter_execution`).

---

## Streamlit UI notes

- **Multipage:** `app/Home.py` (and `streamlit_app.py`) call `st.navigation([st.Page(...)])` so sidebar labels are **Home**, **Case intake**, **Review case actions**, **Integrations**, **Policy & privacy** — independent of the entry script filename.
- **Workflow breadcrumb** (`render_process_breadcrumb`): **Home → Case intake → Review case actions**. Policy is **not** in this strip; see `render_policy_reference_nav` on the Policy page.
- **Luminee promo:** `render_luminee_sidebar_promo()` in `ui_theme.py`; URLs from `LUMINEE_*` settings (defaults point at public Anju/Luminee pages).
- **Primary buttons** (teal) and **page links** (outlined) are styled in `ui_theme.py` for contrast.
- **Case intake → engine**: `CaseIntake.model_validate(intake.model_dump())` in `start_case` avoids Pydantic `model_type` errors when Streamlit `@st.cache_resource` holds an old module identity after reload.
- **Approvals**: radio groups use `index=None` so reviewers must explicitly choose; **Execute** is shown only when status is `approved`, not while `pending_approval`.
- **Review page layout**: **Decision summary** (if routing) → **Proposed actions & approvals** → paired expanders (AI usage vs privacy policy narrative) → concise per-case snapshot → horizontal rule → action rows with **View action details** (rationale + payload). Full **Policy & privacy** reference is via the sidebar page link, not an extra full-width button on Review.
- **Home sidebar** (`0_Home.py`): mock-adapters line, divider, Luminee promo; `st.navigation` supplies the page list (avoid an extra `---` immediately under nav to prevent a double horizontal rule).

---

## Configuration (environment)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Enables LLM classification + embeddings when non-empty |
| `OFFLINE_MODE` | `true` forces heuristic path (see `Settings.use_offline_mode`) |
| `OPENAI_CHAT_MODEL` | Default `gpt-4o` |
| `OPENAI_EMBEDDING_MODEL` | Default `text-embedding-3-small` |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | Audit / policy signals (default `0.65`) |
| `CASE_STORE_PATH` | SQLite file for case JSON (default `data/cases.sqlite3`) |
| `CHROMA_PERSIST_DIRECTORY` | Vector artifact dir (default `data/chroma_db`) |

See `config/settings.py` for exact names (Pydantic reads env vars case-insensitively).

---

## Tests

Run `pytest` from the repo root: offline pipeline, policy matrix paths, restricted gate, PII redaction, integrations, aggregation helpers. No API key required.

---

## Further reading

| Doc | Content |
|-----|---------|
| [README.md](../README.md) | Quick start, feature list, doc index |
| [APP_WALKTHROUGH.md](APP_WALKTHROUGH.md) | Screen-by-screen walkthrough |
| [PRIVACY_AND_COMPLIANCE.md](PRIVACY_AND_COMPLIANCE.md) | Privacy / compliance narrative (non-production scope) |
| [WORKFLOW_DISCOVERY.md](WORKFLOW_DISCOVERY.md) | As-is vs to-be friction narrative |
