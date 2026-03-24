# Demo walkthrough — talking points (Anju context)

**Purpose:** Concise lines you can say while screen-sharing the **Anju Internal Case Router** demo.  
**Sources:** Public copy from **anjusoftware.com** key pages (About, Technology, eClinical suite, CTMS Master, Luminee, TrialMaster, Medical Affairs / IRMS MAX, Data Science / TA Scan). This is **not** an exhaustive crawl of every URL; it reflects **marketing-facing** positioning as of fetch date.

---

## Recommended interview walkthrough (two scenarios)

Use **Case intake** with the scenario picker (order is tuned for this flow):

1. **Implementation kickoff — IRMS MAX** first: say *case-to-action automation across PS, delivery, and finance* — show **Case run** → policy snapshot → **Professional Services** routing → epic + NetSuite + checklist → approvals. This is *normal* cross-functional internal automation.

2. **Compliance — FDA audit prep** second: Q&C routing, audit checklist, then (optionally) a **restricted-content** example from **Policy & privacy** or a synthetic restricted intake — *regulated exception path*, no external LLM when policy blocks.

Keep scrolling minimal: anchor on policy snapshot, routing, proposed actions, approvals, audit export.

Framing: not *“ticket triage”* — *“case-to-action automation across internal systems.”*

---

## 30-second opener

- *“Anju sells life sciences software across **eClinical**, **Medical Affairs**, and **Data Science**—flagships like **TrialMaster**, **IRMS MAX**, and **TA Scan**, plus newer AI like **Luminee** for protocol-to-build acceleration.”*
- *“The **Internal AI Automation Lead** role isn’t to rebuild those products—it’s to remove **internal** friction: support, professional services, finance, HR, and ops **around** those products.”*
- *“This demo is a **case router**: messy inbound text → classify → optional retrieval from **internal playbooks** → route → **proposed actions** in Jira, Teams, CRM, NetSuite-style systems—with **human approval** and an **audit trail**. That’s the same vocabulary as the job posting.”*

---

## What Anju’s software does (talk track, by suite)

### Company frame (About + Technology)

- *“Anju positions itself as **customer-first**, clinical research + medical affairs + data science, with solutions that **integrate** with third parties and move data across systems.”*
- *“Their **Anju Technology** stack talks about a **secured repository**, **streamlined workflows**, **search**, **Office 365**, **adapters** to CRMs like Salesforce and Veeva, **SQL and No-SQL**, and **dashboards**—that’s why I framed integrations as an **adapter registry**, not one-off scripts.”*

### eClinical suite

| Product | One-liner you can say |
|--------|------------------------|
| **TrialMaster** | *“EDC for Phase I–IV: **TrialBuilder**, exports toward **CDISC/SDTM**, **REST APIs**, ePRO, RBQM-style monitoring—this is where ‘export failed’ or ‘validation’ tickets come from in support.”* |
| **CTMS Master** | *“**Clinical trial management**: sites, visits, **finance/budgets**, **metrics**, SVR workflows, integration with **TrialMaster** and other EDCs—ops-heavy, lots of cross-system coordination.”* |
| **Luminee** | *“**AI for trial build**: ingests **protocols**, auto-creates study objects, **NLP edit checks**, validation artifacts—**customer-facing** product AI, not internal Jira glue. I’m **not** duplicating Luminee; my demo is **internal intake and routing**.”* |
| **TA Scan** (also highlighted under eClinical hub) | *“**Intelligence** on feasibility, sites, landscape—often **API** and **data services**; good for ‘data question’ and scoping-style requests.”* |

### Medical Affairs suite

| Product | One-liner |
|--------|------------|
| **IRMS MAX** | *“**Medical information**: case intake from **email, fax, web, CTI**, CRM integration, **audit trails**, **GDPR / 21 CFR Part 11** language on their page—exactly why I emphasize **approval gates** and **audit JSON** in the demo.”* |
| **iCare MAX** | *“Self-service **content portal** for HCPs/consumers tied to MA.”* |
| **Pubstrat MAX** | *“**Publication planning** and scientific communications.”* |

### Data Science suite

| Product | One-liner |
|--------|------------|
| **TA Scan** (Data Science) | *“Aggregates **public** clinical/commercial data; **API**, reporting, feasibility, diversity, KOL—supports ‘custom report / API’ style internal requests.”* |
| **Services** | *“They also sell **data consolidation and integration** services—more evidence that **integration** is in their DNA.”* |

### Name check: CTMS vs “CTSM”

- *“On the website the product is **CTMS Master**—**Clinical Trial Management System**. People say **CTMS** in the industry; I use **CTMS Master** when I want to match their branding.”*

---

## How **this project** enhances Anju’s world (without replacing products)

| Anju product AI (e.g. Luminee) | This demo |
|--------------------------------|-----------|
| Speeds **sponsor-facing** trial **build** and validation artifacts | Speeds **internal** triage of **who owns the work** and **what to create in Jira/Teams/CRM/PS systems** |
| Lives in the **eClinical product** boundary | Lives in **Sales, PS, Support, Finance, HR** **internal** tool chain (per job description) |
| **Data sovereignty** story for trial protocols | **Data minimization** story: optional **PII redaction** before LLM, **human approval** before mocked writes |

**Soundbite:** *“Luminee compresses **months of build**; my demo compresses **minutes of cross-tool coordination**—different layer, same ‘operating leverage’ mindset.”*

---

## Walkthrough — screen by screen

### 1) Home (`streamlit_app.py`)

- *“You can see **offline vs full LLM+RAG**—I can run the UI with **no API key** for reliability, or full **OpenAI** for the interview.”*
- *“Sidebar lists the **mock adapters**: Jira, Teams, Salesforce, NetSuite, BambooHR—aligned with systems named in the posting.”*

### 2) Case Intake

- *“Scenarios are **synthetic**—TrialMaster export issues, **IRMS** + CRM routing, **TA Scan** data requests, **implementation** kickoffs—**product-aware** without touching real customer data.”*
- *“**Redact** with **standard** or **strict** policy turns on **data minimization** before anything hits the model—see `docs/PRIVACY_AND_COMPLIANCE.md` for the compliance **talk track**, not legal claims.”*

### 3) Case run (pipeline + policy snapshot + approvals)

- *“**Classification** picks product line and issue type—this is how you’d **separate** CTMS ops noise from **EDC** defects from **TA Scan** scoping.”*
- *“**RAG** runs only when **policy** says so; otherwise you’ll see an explicit **skip** in the audit—**rules first, semantics when needed**.”*
- *“**Routing and proposed actions** come from a **deterministic policy matrix**—selective integrations, not spamming every system.”*
- *“Expand **Policy snapshot** for risk tier, LLM allowed, and restricted path. **Approvals** are on the same page—nothing hits **mock integrations** until a human **approves**.”*
- *“**Audit** and **export** live in an expander—**JSON-friendly** for **ELK/SIEM**.”*
- *“Light **metrics** at the top (stored cases, restricted count, RAG skipped) are **illustrative**—in the role I’d wire real handle time and SLA.”*

### 4) Policy & privacy

- *“This is the **controls** story: **LLM for interpretation**, **policy for execution**, **restricted gate** for sensitive patterns, plus the **privacy/compliance** doc inline for the interview.”*

### Reference: as-is vs to-be (not a separate UI page)

- *“`docs/WORKFLOW_DISCOVERY.md` has the **friction map** if they want depth: manual triage vs one intake + approval-gated execution.”*

---

## If they ask: “Are we duplicating something Anju already ships?”

- *“**No** for **Luminee**—that’s **protocol → database build** AI for customers.”*
- *“**No** for **IRMS** **case management** itself—this doesn’t replace **medical information** workflow software; it could **sit beside** it for **internal** handoffs and **cross-system** actions.”*
- *“**Yes** to **alignment**: your **Technology** page already describes **adapters**, **CRM**, **real-time and batch** integration—I'm showing how I’d **orchestrate** and **govern** automation **above** that layer for **internal** ops.”*

---

## Closing line (15 seconds)

- *“I’m not pitching a new EDC. I’m showing how I’d **measure**, **automate**, and **govern** the **internal** work that **surrounds** TrialMaster, **CTMS Master**, **IRMS MAX**, **TA Scan**, and the rest—**faster**, **auditable**, and **approval-first**.”*

---

## Appendix — pages reviewed for this document

| URL (path) | Topic |
|------------|--------|
| `/about-anju/` | Mission, flagships, Valsoft |
| `/technology/` | Platform, adapters, suites |
| `/eclinical/` | Suite overview, Luminee, TA Scan, TrialMaster, CTMS Master |
| `/trialmaster/` | EDC capabilities, APIs, exports |
| `/eclinical/luminee/` | AI build, protocol ingestion, data sovereignty |
| `/eclinical/ctms-master/` | CTMS features, TrialMaster integration |
| `/medical-affairs/` | IRMS, iCare, Pubstrat |
| `/medical-affairs/irms-max/` | MI, CRM integration, audit, compliance |
| `/data-science/` | TA Scan, data services |

**Note:** Re-scrape or re-read product pages before interviews; marketing copy changes.
