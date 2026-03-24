# Privacy, security, and compliance (demo scope)

This repository is a **portfolio / interview demo**. It is **not** certified for HIPAA, HITECH, or any specific jurisdictional framework. Use this document to discuss **how you would harden** a real deployment at a life sciences SaaS company.

## What this demo assumes

- **Synthetic or anonymized** scenarios in the UI (pre-built demos). Do not paste real patient identifiers or live clinical data into a public demo.
- **Internal operations** use case (support, PS, finance handoffs)—not direct patient care systems. Even then, ticket text can contain **PHI/PII** depending on customer content; treat inbound text as **potentially sensitive**.

## United States: HIPAA / PHI (conceptual)

- **HIPAA** applies to **covered entities** and **business associates** handling **PHI** in defined circumstances.
- A vendor’s **internal** support tools may still process **sensitive** customer content; policies often include **data minimization**, **access controls**, **audit trails**, **encryption in transit/at rest**, **BAA**-governed subprocessors for LLMs, and **retention** limits.
- This demo **does not** implement a BAA, encryption at rest for all stores, or full access control—it shows **patterns** (approval gates, audit entries, optional redaction before model calls).

## Canada: privacy (high level)

- **PIPEDA** (federal) and **provincial** laws (e.g. Québec Law 25, BC PIPA, Alberta PIPA) may apply depending on data type and context.
- Health information may be subject to **additional provincial health privacy** statutes. Legal counsel determines applicability.

## Controls demonstrated in code (intentionally partial)

| Control | Where |
|--------|--------|
| **Human-in-the-loop** before mocked “writes” | Case run page (approvals), workflow engine |
| **Structured audit trail** | `CaseRecord.audit_trail`, export JSON |
| **Optional PII redaction** before LLM/RAG | `CaseIntake.redact_pii`, `src/utils/pii.py`, `CaseRecord.text_for_llm()` |
| **Data minimization narrative** | README, this doc |=

## Disclaimer

Not legal or compliance advice. For production systems, involve **Legal**, **Security**, and **Quality/Compliance** early.
