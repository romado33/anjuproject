# Anju Internal Case Router

**Internal case-to-action automation** for **life sciences SaaS operations** (support, professional services, compliance, customer operations): turn unstructured inbound text into **classification**, **optional RAG**, **deterministic routing and selective proposed actions** (Jira, Teams, Salesforce / Veeva CRM, NetSuite, BambooHR, internal checklist mocks), **human-in-the-loop** decisions per action, **mock execution**, and an **append-only audit trail** persisted in SQLite.

**Scope:** Automates **internal** work *around* products such as TrialMaster, CTMS Master, IRMS MAX, TA Scan, and Medical Affairs offerings — not clinical treatment systems. See [docs/PRIVACY_AND_COMPLIANCE.md](docs/PRIVACY_AND_COMPLIANCE.md) before handling real sensitive text.

---

## Features

| Area | What you get |
|------|----------------|
| **Pipeline** | LangGraph: classify → conditional RAG → policy route → policy actions (no LLM planner for routing) |
| **Policy** | `src/policy/engine.py` — when RAG runs, queues, SLAs, which integrations are proposed |
| **Restricted gate** | Heuristic signals can block external LLM + embeddings; keyword path + same policy |
| **Modes** | Full (OpenAI) or offline (no API key / `OFFLINE_DEMO`) — shared policy matrix |
| **RAG** | Chunked Markdown in `data/knowledge_base/`; SQLite + vector retrieval |
| **UI** | Streamlit: **Home**, **Case intake**, **Review case actions**, **Integrations**, **Policy & privacy** (sidebar) |
| **UI (sidebar & review)** | Home: mock-adapters line + Luminee promo. Review: decision summary, AI/privacy expanders, per-action details, approvals, audit export. **Integrations:** adapter endpoints JSON |
| **Demo data** | Four showcase scenarios + extra scenarios in `src/demo_scenarios.py` |
| **Audit** | `CaseRecord.audit_trail`; JSON export on Review page |
| **Tests** | `pytest` — no key required |

---

## Why code over “just Zapier / n8n”?

Low-code tools excel at linear triggers. This repo shows **typed models**, **evaluable** steps, **approval gates**, **policy that is testable in CI**, and **audit exports** — patterns that matter when **ambiguity, policy, and review** dominate.

---

## AI vs rules (short)

| Mechanism | Role |
|-----------|------|
| **LLM** | **Classification** (structured output) when allowed |
| **Embeddings + RAG** | Only when `should_retrieve_context` approves |
| **Policy engine** | Routing, proposed actions, risk tier, RAG skip rules |
| **Restricted gate** | Can force offline path — no external model/embeddings |
| **Human** | Per-action approve / modify / reject before mock writes |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | File map, pipeline, config, UI behavior |
| [docs/PRIVACY_AND_COMPLIANCE.md](docs/PRIVACY_AND_COMPLIANCE.md) | Demo-scope privacy and compliance narrative |
| [docs/WORKFLOW_DISCOVERY.md](docs/WORKFLOW_DISCOVERY.md) | As-is vs to-be operational friction |

---

## Quick start

**Requirements:** Python 3.11+ recommended (per your environment).

```powershell
cd anju-case-router
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Add OPENAI_API_KEY to .env for full LLM + embeddings
```

**Seed the knowledge base** (embeddings need an API key):

```powershell
$env:PYTHONPATH="."
python scripts/seed_knowledge_base.py
# After changing files under data/knowledge_base/:
# python scripts/seed_knowledge_base.py --reset
```

**Run the app:**

```powershell
$env:PYTHONPATH="."
streamlit run app/Home.py
```

`streamlit run app/streamlit_app.py` runs the **same** multipage app as `Home.py`. Both use `st.navigation` so the first sidebar item is **Home** (not the script file name). Landing content lives in `app/pages/0_Home.py`.

**Tests:**

```powershell
pytest
```

## Conceptual flow

**Inbound text** → optional **PII redaction** for model path → **restricted gate** → **classification** → **RAG (optional)** → **deterministic routing + actions** → **human decisions** → **mock adapter execution** → **audit + export**.

Adapters are **mocked**; the registry pattern mirrors extending a bus (e.g. AnjuBUS-style) with new targets.

---

## License

Demo / portfolio project — confirm licensing before production reuse.
