# Architecture — how to explain this project in an interview

Use this doc to walk yourself (or an interviewer) through the codebase in about 5 minutes. File references are relative to the project root.

## One sentence

A Python + Streamlit app that classifies inbound work requests, optionally retrieves internal knowledge, applies **deterministic policy** (not more LLM) for routing and selective actions across Jira/Teams/CRM/NetSuite-style systems, then requires human approval before mock execution — with an audit trail.

## Key design principle

**LLM interprets ambiguity (classification). Deterministic policy governs everything else (routing, actions, gates).**

This is the single most important thing to say in the interview. It separates the project from generic "AI agent" demos.

## File map (what lives where)

```
anju-case-router/
├── app/                        # Streamlit UI (3 pages)
│   ├── streamlit_app.py        # Landing page
│   ├── ui_theme.py             # Shared CSS/config
│   └── pages/
│       ├── 1_Case_Intake.py    # Submit request, pick scenario, redaction
│       ├── 2_Case_Run.py       # Pipeline output + policy + approvals + export
│       └── 3_Policy_and_Privacy.py  # Controls narrative + compliance doc
│
├── src/
│   ├── agent/                  # Pipeline orchestration
│   │   ├── orchestrator.py     # Entry point: restricted gate → offline or LangGraph
│   │   ├── offline.py          # Keyword classification (no API key needed)
│   │   ├── classifier.py       # OpenAI structured-output classification node
│   │   ├── context_gatherer.py # Conditional RAG retrieval node
│   │   ├── policy_nodes.py     # Deterministic routing + action nodes (LangGraph)
│   │   ├── llm.py              # OpenAI client factory
│   │   └── state.py            # LangGraph shared state type
│   │
│   ├── policy/                 # Deterministic policy engine (the core differentiator)
│   │   ├── engine.py           # Risk tier, conditional RAG, routing matrix, action matrix,
│   │   │                       #   KB nudges, operator metrics, policy snapshot
│   │   └── restricted.py       # Regex-based restricted-content detection
│   │
│   ├── models/
│   │   └── case.py             # Pydantic models: CaseRecord, Classification, etc.
│   │
│   ├── rag/
│   │   ├── retriever.py        # Embedding + SQLite vector retrieval
│   │   └── vector_store.py     # SQLite + NumPy cosine similarity store
│   │
│   ├── integrations/           # Mock adapters (Jira, Teams, Salesforce, NetSuite, etc.)
│   │   ├── registry.py         # Dispatch pattern (AnjuBUS-style)
│   │   └── *_client.py         # Individual mock adapters
│   │
│   ├── workflow/
│   │   ├── engine.py           # CaseWorkflowEngine: start → approve → execute
│   │   └── store.py            # SQLite JSON persistence
│   │
│   ├── utils/
│   │   └── pii.py              # PII redaction (standard + strict modes)
│   │
│   └── demo_scenarios.py       # Pre-built intake scenarios for interviews
│
├── data/knowledge_base/        # Markdown files for RAG (product + process context)
├── config/settings.py          # Pydantic settings from .env
├── tests/                      # pytest suite (offline, policy, redaction, integrations)
├── docs/                       # Interview docs, compliance, workflow discovery
└── scripts/seed_knowledge_base.py  # One-time KB embedding script
```

## Pipeline flow (what happens when you click "Run pipeline")

```
1. RESTRICTED GATE (orchestrator.py)
   └─ analyze_restricted() scans text for PHI/AE/trial-ID patterns
   └─ If triggered → skip LLM entirely, use offline keyword path

2. CLASSIFICATION (classifier.py or offline.py)
   └─ Online: OpenAI structured output → Classification model
   └─ Offline: keyword regex → same Classification model

3. CONDITIONAL RAG (context_gatherer.py)
   └─ should_retrieve_context() checks policy rules:
      - Compliance/implementation → always retrieve
      - High confidence + training → skip (save cost/latency)
      - Restricted → skip (no embedding API calls)

4. DETERMINISTIC ROUTING (policy_nodes.py → engine.py)
   └─ route_from_policy(): classification → team + queue + SLA
      - Compliance → Quality & Compliance / QNC-Audit-Review
      - Implementation → Professional Services / PS-{product}-Onboarding
      - Bug → eClinical Engineering or MI Support (by product)
   └─ KB nudges: if RAG chunks mention integration/audit → adjust queue/SLA

5. SELECTIVE ACTIONS (policy_nodes.py → engine.py)
   └─ build_actions_from_policy(): different paths produce different actions
      - Simple TA data question → CRM + Teams only (NO Jira)
      - Implementation → Epic + Teams + CRM + NetSuite + BambooHR + checklist
      - Compliance → Jira + Teams + CRM + audit checklist
      - Bug → Jira + conditional Teams (only if high/critical)

6. HUMAN APPROVAL (workflow/engine.py → UI)
   └─ Nothing executes until a human approves each proposed action

7. MOCK EXECUTION (integrations/registry.py)
   └─ Adapter dispatch → mock payloads logged in audit trail
```

## What to say about each major component

### Policy engine (`src/policy/engine.py`)
"This is where the real logic lives. After classification, everything is deterministic — routing, actions, risk tier, whether RAG runs. The LLM only interprets; policy controls."

### Restricted gate (`src/policy/restricted.py`)
"If the text mentions patient IDs, adverse events, trial registry IDs — the system blocks external LLM calls entirely and falls back to keyword classification + policy. In production this would be DLP, not regex."

### Offline mode (`src/agent/offline.py`)
"The same policy engine runs whether we have an API key or not. Offline uses keyword classification; online uses OpenAI. Routing and actions are identical either way — that's intentional."

### RAG (`src/rag/`)
"Retrieval is conditional. Policy decides when to skip it (high confidence, training, restricted) and when to require it (compliance, implementation, low confidence). When it runs, KB chunks can nudge routing — e.g. IRMS data question with integration context gets rerouted to MI Integrations."

### Adapters (`src/integrations/`)
"All mocked, but the pattern is real: a registry dispatches by action type, like extending AnjuBUS with new endpoints. Each adapter logs structured results."

### Tests (`tests/`)
"13 tests cover: offline end-to-end, policy routing (PS path, selective actions, RAG skip, KB nudge), restricted gate, PII redaction (standard + strict), and adapter dispatch. All run without an API key."

## Two-scenario interview demo

1. **Implementation kickoff — IRMS MAX**: shows PS routing, epic, NetSuite, checklist — "cross-functional automation, not just ticket triage."
2. **Compliance — FDA audit prep**: shows Q&C routing, audit checklist, restricted gate — "regulated exception path."

See `docs/DEMO_WALKTHROUGH_TALKING_POINTS.md` for exact lines to say on each screen.
