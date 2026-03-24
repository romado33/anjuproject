# Interview cheat sheet — Internal AI Automation Lead (Anju-style)

## One-liner

*"I built **case-to-action automation across internal systems** — support, PS, compliance, customer ops — turning messy inbound work into classification, retrieval when policy says so, deterministic routing and selective actions across Jira, Teams, Salesforce/Veeva CRM, and finance-adjacent systems, with human approval and an audit trail."*

## What to understand (job fit)

| They want | Your demo |
|-----------|-----------|
| Find friction, automate | `docs/WORKFLOW_DISCOVERY.md`: before/after + pain tags |
| Integrations (Jira, NetSuite, Teams, CRM) | Mock adapters + registry pattern (AnjuBUS-style story) |
| Agentic AI + RAG when useful | Full mode: LangGraph + embeddings retrieval; offline: rules |
| Security / audit / responsible AI | Privacy doc + redaction toggle + approvals + audit JSON |
| Ship working systems | Runnable Streamlit + pytest |

## Know the org

- **Two divisions:** eClinical (GM: Tim Lyons) and Medical Affairs (GM: Reed McLaughlin), under Valsoft.
- **eClinical products:** TrialMaster (EDC), CTMS Master, Luminee (AI trial build)
- **Medical Affairs products:** IRMS MAX, iCare MAX, Pubstrat MAX, MA Knowledge
- **Data Science:** TA Scan (ta-scan.io) — feasibility, site selection, KOL/investigator ID, competitive intelligence
- **Only open role on careers page:** Associate Director BD (Remote, US). Your role isn't posted publicly.

## When to use RAG vs rules (sound smart)

- **Rules / keywords:** clear intents, high volume, low ambiguity (cheap, testable).
- **Embeddings + RAG:** ambiguous language, need product/process docs, or evolving playbooks.
- **LLM structured outputs:** triage (**classification**); routing and actions are **deterministic policy** in this demo.

## Zapier / n8n vs code (Cursor, Claude Code)

- **Zapier / n8n:** great for **straightforward** triggers and linear flows.
- **Custom pipeline:** when you need **typed contracts**, **evals**, **complex branching**, **approval gates**, **audit**, and **same-repo CI** — agent-assisted coding makes that **fast without giving up** engineering rigor.

## Questions to ask them

1. Where are the top **manual** bottlenecks today (Support, PS, Finance)?
2. Which systems are **source of truth** for accounts, tickets, and billable work?
3. What **compliance** gates apply to internal automation (ITGC, change control)?
4. How would they measure **success in 90 days**?
5. How does TA Scan data flow into internal systems today — API, manual export, or DaaS?
6. What's the relationship between IRMS MAX case management and Veeva CRM in practice?

## How to quickly re-learn the codebase

Read `docs/ARCHITECTURE.md` — it has a file map, pipeline flow diagram, and one-liner explanations for every major component. Takes about 5 minutes.

## If something breaks in the demo

- **No API key:** offline mode — same UI, heuristic routing.
- **Empty KB:** run `python scripts/seed_knowledge_base.py` (needs key once).
