# Anju Internal Case Router

**Case-to-action automation** across internal systems for **life sciences SaaS operations** (support, professional services, compliance, customer ops — not ticket triage alone): classify inbound work, retrieve product/process context (**RAG when policy says so**), apply **deterministic routing and selective actions**, propose **AnjuBUS-style adapter invocations** (Jira, Teams, Salesforce/Veeva CRM, NetSuite, BambooHR, internal checklist), and enforce **human-in-the-loop approval** before mock execution.

**Scope:** This automates **internal** work *around* products like TrialMaster, CTMS Master, IRMS MAX, TA Scan (ta-scan.io), and the Medical Affairs suite (support, PS, handoffs) — not clinical data pipelines. See [`docs/PRIVACY_AND_COMPLIANCE.md`](docs/PRIVACY_AND_COMPLIANCE.md).

---

## Why this vs “just Zapier / n8n”?

- **Zapier / n8n** excel at linear triggers and quick integrations.
- This demo shows **typed workflows**, **evaluable** agent steps, **approval gates**, **audit trails**, and **same-repo** tests—patterns you’d ship when **policy, ambiguity, and compliance** matter. Agent-assisted coding (Cursor, Claude Code) makes custom pipelines **fast** without giving up engineering rigor.

## When we use AI vs rules

| Mechanism | Use when |
|-----------|----------|
| **Keyword / offline mode** | No API key, smoke tests, or obvious keyword routes |
| **Embeddings + RAG** | Policy says retrieve: low confidence, compliance, implementation, etc. (skipped when high-confidence training/general paths) |
| **LLM structured outputs** | **Classification only** (interpret ambiguity); routing + actions are **deterministic policy** (`src/policy/engine.py`) |
| **Restricted-case gate** | Regex signals (PHI/AE language, trial IDs, etc.) → **no external LLM/embeddings**; offline policy path |
| **Human approval** | Before any mocked “write” to Jira, Teams, CRM, NetSuite |

## Highlights

- **LangGraph** pipeline: classify → **conditional** RAG → **policy** route → **policy** actions (no LLM router/planner)  
- **Deterministic policy engine**: selective integrations (not Jira+Teams+CRM every time); optional KB **routing nudges** when chunks warrant it  
- **OpenAI** (`gpt-4o` + `text-embedding-3-small`) when `OPENAI_API_KEY` is set  
- **Offline mode**: keyword heuristics when no API key (or `OFFLINE_DEMO=true`) — CI-safe, same policy matrix as online  
- **RAG**: SQLite + NumPy cosine retrieval over chunked Markdown in `data/knowledge_base/`  
- **Optional PII redaction** (`CaseIntake.redact_pii`, optional `redaction_policy=strict` for NCT/site-style tokens) — demo-only; not a HIPAA tool  
- **Structured audit trail** (JSON export as ELK-style narrative)  
- **Streamlit** UI (three pages): **Case intake**, **Case run** (pipeline + policy snapshot + approvals + export), **Policy & privacy** (architecture + compliance doc); see also `docs/WORKFLOW_DISCOVERY.md` for as-is vs to-be narrative  

## Documentation

| Doc | Purpose |
|-----|---------|
| [`docs/PRIVACY_AND_COMPLIANCE.md`](docs/PRIVACY_AND_COMPLIANCE.md) | HIPAA/PHI/Canada privacy **talk track**, data minimization, production hardening |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **File map, pipeline flow, component explanations** — read this first to understand the project |
| [`docs/WORKFLOW_DISCOVERY.md`](docs/WORKFLOW_DISCOVERY.md) | As-is vs to-be friction narrative (formerly a Streamlit page) |

## Quick start

```powershell
cd anju-case-router
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Add OPENAI_API_KEY to .env for full LLM + embeddings
```

Seed the knowledge base (requires OpenAI key for embeddings):

```powershell
$env:PYTHONPATH="."
python scripts/seed_knowledge_base.py
# After adding new files under data/knowledge_base/, re-embed with:
# python scripts/seed_knowledge_base.py --reset
```

Run the app:

```powershell
$env:PYTHONPATH="."
streamlit run app/streamlit_app.py
```

Run tests:

```powershell
pytest
```

## Configuration

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required for LLM + embedding paths |
| `OFFLINE_DEMO` | `true` to force heuristic routing (no OpenAI calls) |
| `OPENAI_CHAT_MODEL` | Default `gpt-4o` |
| `OPENAI_EMBEDDING_MODEL` | Default `text-embedding-3-small` |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | Flags low-confidence runs in audit |
| `CASE_STORE_PATH` | SQLite path for persisted cases |
| `CHROMA_PERSIST_DIRECTORY` | Directory for vector SQLite + artifacts |

## Architecture (conceptual)

Unstructured request → **restricted gate** (optional) → **classification** (LLM when allowed) → **RAG** (only when policy says so) → **deterministic routing + action matrix** → **human approval** → **mock adapter execution** with full audit logging.

Adapters are intentionally **mocked** but follow a registry pattern analogous to extending **AnjuBUS** with new endpoints (Jira, Teams, Salesforce/Veeva CRM, NetSuite, etc.).

## Interview narrative

- **Product-aware + workflow-aware:** KB references TrialMaster / CTMS Master / IRMS MAX / TA Scan (incl. KOL, feasibility, site selection) / iCare MAX / Pubstrat MAX / MA Knowledge — focus is **internal leverage**, not a product chatbot.  
- **AI layer** above integration infrastructure (not rip-and-replace).  
- **Explainability**, **auditability**, and **approval gates** for regulated-adjacent operations.  
- Maps to CRM / Jira / Teams / ERP / HR systems named in enterprise job descriptions.
## License

Demo project — verify licensing before any reuse in production.
