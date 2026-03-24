# Interview cheat sheet — Internal AI Automation Lead (Anju-style)

## One-liner

*“I built **case-to-action automation across internal systems**—support, PS, compliance, customer ops—turning messy inbound work into classification, retrieval when policy says so, deterministic routing and selective actions across Jira, Teams, CRM, and finance-adjacent systems, with human approval and an audit trail.”*

## What to understand (job fit)

| They want | Your demo |
|-----------|-----------|
| Find friction, automate | `docs/WORKFLOW_DISCOVERY.md`: before/after + pain tags (not a separate UI page) |
| Integrations (Jira, NetSuite, Teams, CRM) | Mock adapters + registry pattern (AnjuBUS-style story) |
| Agentic AI + RAG when useful | Full mode: LangGraph + embeddings retrieval; offline: rules |
| Security / audit / responsible AI | Privacy doc + redaction toggle + approvals + audit JSON |
| Ship working systems | Runnable Streamlit + pytest |

## When to use RAG vs rules (sound smart)

- **Rules / keywords:** clear intents, high volume, low ambiguity (cheap, testable).
- **Embeddings + RAG:** ambiguous language, need product/process docs, or evolving playbooks.
- **LLM structured outputs:** triage (**classification**); routing and actions are **deterministic policy** in this demo.

## Zapier / n8n vs code (Cursor, Claude Code)

- **Zapier / n8n:** great for **straightforward** triggers and linear flows.
- **Custom pipeline:** when you need **typed contracts**, **evals**, **complex branching**, **approval gates**, **audit**, and **same-repo CI**—agent-assisted coding makes that **fast without giving up** engineering rigor.

## Questions to ask them

1. Where are the top **manual** bottlenecks today (Support, PS, Finance)?
2. Which systems are **source of truth** for accounts, tickets, and billable work?
3. What **compliance** gates apply to internal automation (ITGC, change control)?
4. How would they measure **success in 90 days**?

## If something breaks in the demo

- **No API key:** offline mode—same UI, heuristic routing.
- **Empty KB:** run `python scripts/seed_knowledge_base.py` (needs key once).
