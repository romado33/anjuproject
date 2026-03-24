# Demo walkthrough — talking points (Anju context)

**Purpose:** Concise lines you can say while screen-sharing the **Anju Internal Case Router** demo.
**Sources:** Full site scrape of **anjusoftware.com** and **ta-scan.io** as of March 2026 — About, Technology, eClinical suite, CTMS Master, Luminee, TrialMaster, Medical Affairs (IRMS MAX, iCare MAX, Pubstrat MAX, MA Knowledge), Data Science / TA Scan, Careers, Management, FAQ pages, Partner Program.

---

## Recommended interview walkthrough (two scenarios)

Use **Case intake** with the scenario picker (order is tuned for this flow):

1. **Implementation kickoff — IRMS MAX** first: say *case-to-action automation across PS, delivery, and finance* — show **Case run** → policy snapshot → **Professional Services** routing → epic + NetSuite + checklist → approvals. This is *normal* cross-functional internal automation.

2. **Compliance — FDA audit prep** second: Q&C routing, audit checklist, then (optionally) a **restricted-content** example from **Policy & privacy** or a synthetic restricted intake — *regulated exception path*, no external LLM when policy blocks.

Keep scrolling minimal: anchor on policy snapshot, routing, proposed actions, approvals, audit export.

Framing: not *"ticket triage"* — *"case-to-action automation across internal systems."*

---

## 30-second opener

- *"Anju sells life sciences software across **eClinical**, **Medical Affairs**, and **Data Science** — flagships like **TrialMaster**, **IRMS MAX**, and **TA Scan**, plus newer AI like **Luminee** for protocol-to-build acceleration. They run two divisions — **eClinical** (Tim Lyons) and **Medical Affairs** (Reed McLaughlin) — under Valsoft."*
- *"The **Internal AI Automation Lead** role isn't to rebuild those products — it's to remove **internal** friction: support, professional services, finance, HR, and ops **around** those products."*
- *"This demo is a **case router**: messy inbound text → classify → optional retrieval from **internal playbooks** → route → **proposed actions** in Jira, Teams, Salesforce/Veeva CRM, NetSuite-style systems — with **human approval** and an **audit trail**. That's the same vocabulary as the job posting."*

---

## What Anju's software does (talk track, by suite)

### Company frame (About + Technology)

- *"Anju positions itself as **customer-first**, clinical research + medical affairs + data science, with solutions that **integrate** with third parties and move data across systems."*
- *"Their **Anju Technology** stack talks about a **secured repository**, **streamlined workflows**, **natural language queries** for reporting, **Office 365**, **pre-built adapters** to CRMs like Salesforce, Veeva, and MS CRM (bi-directional, real-time or batch), **SQL and No-SQL**, and **dashboard designer** — that's why I framed integrations as an **adapter registry**, not one-off scripts."*
- *"They're organized into two divisions: **eClinical Division** and **Medical Affairs Division**, each with a GM. My demo's routing mirrors this — TrialMaster/CTMS routes to **eClinical Engineering/Support**, IRMS routes to **MI Support/MI Integrations**."*

### eClinical suite

| Product | One-liner you can say |
|--------|------------------------|
| **TrialMaster** | *"EDC for Phase I–IV: **TrialBuilder**, exports toward **CDISC/SDTM**, **REST APIs**, ePRO, eConsent, RBQM-style monitoring, SSO auth — this is where 'export failed' or 'validation' tickets come from in support. 6,000+ trials, 65,000+ sites, 18 languages."* |
| **CTMS Master** | *"**Clinical trial management**: sites, visits, **finance/budgets** (site-specific budgets, accrued payments, invoicing), **100+ metrics**, SVR workflows, protocol deviation management, informed consent tracking, integration with **TrialMaster** and other EDCs — ops-heavy, lots of cross-system coordination."* |
| **Luminee** | *"**AI for trial build**: ingests **protocols**, auto-creates study objects, **NLP edit checks**, validation artifacts — cuts build time by up to **90%**. They just launched a **free Protocol Summarizer** for clinical sites. **Data sovereignty** guaranteed — 'your data is never monetized.' I'm **not** duplicating Luminee; my demo is **internal intake and routing**."* |
| **TA Scan** | *"Has its **own domain** at **ta-scan.io** — it's a full platform, not just a report tool."* (see Data Science section below) |

### Medical Affairs suite

| Product | One-liner |
|--------|------------|
| **IRMS MAX** | *"**Gold standard** medical information system: case intake from **email, fax, web, CTI**, CRM integration (Salesforce, Veeva, MS CRM via pre-built adapters), **AE and product complaint** modules with transfer to safety systems, **audit trails**, **GDPR / 21 CFR Part 11**, role-based access, multi-division global deployments, **natural language reporting** with visual dashboards. Exactly why I emphasize **approval gates** and **audit JSON**."* |
| **iCare MAX** | *"Self-service **content portal** for HCPs/consumers — secure, branded, searchable. Fully integrated with IRMS MAX content management. Self-attestation for HCP vs consumer access. Hosted on **Azure**. Studies show HCPs prefer online access over phone inquiries **2:1**."* |
| **Pubstrat MAX** | *"**Publication planning** and scientific communications. Only tool in the industry with **true online collaboration and simultaneous editing**. Integrates with **Journal Selector and Conference Authority (JSCA)** database for targeting the right venues."* |
| **MA Knowledge** | *"Content delivery for **MSLs and field reps** — smart filtering, search, dynamic workspace. Pulls vetted content from IRMS MAX and external links. Think of it as the field-facing access layer next to IRMS (case management) and iCare (self-service portal)."* |

### Data Science suite

| Product | One-liner |
|--------|------------|
| **TA Scan** | *"Separate brand at **ta-scan.io**. Four modules: **Site Selection** (capacity to recruit), **Investigator/KOL Identification** (score, rank, engage experts, fee disclosures), **Competitive Intelligence** (therapeutic landscape, trial timing, sponsor activity), **Strategic Feasibility** (predictive enrollment via **Feasibility Flex**). 480K+ trials, 2.4M+ HCPs, 350K+ sites, 550+ indications. Three delivery modes: **web platform**, **API services**, and **Data-as-a-Service** (48h turnaround for CROs). Good for 'data question', 'custom report', and scoping-style internal requests."* |
| **Services** | *"Data consolidation and integration services — TA Scan data into CTMS/CRM via API, or consolidation of customer's investigator/KOL data into a single source of truth. More evidence that **integration** is in their DNA."* |

### Name check: CTMS vs "CTSM"

- *"On the website the product is **CTMS Master** — **Clinical Trial Management System**. People say **CTMS** in the industry; I use **CTMS Master** when I want to match their branding."*

---

## How **this project** enhances Anju's world (without replacing products)

| Anju product AI (e.g. Luminee) | This demo |
|--------------------------------|-----------|
| Speeds **sponsor-facing** trial **build** and validation artifacts | Speeds **internal** triage of **who owns the work** and **what to create in Jira/Teams/CRM/PS systems** |
| Lives in the **eClinical product** boundary | Lives in **Sales, PS, Support, Finance, HR** **internal** tool chain (per job description) |
| **Data sovereignty** story for trial protocols | **Data minimization** story: optional **PII redaction** before LLM, **human approval** before mocked writes |

**Soundbite:** *"Luminee compresses **months of build**; my demo compresses **minutes of cross-tool coordination** — different layer, same 'operating leverage' mindset."*

---

## Walkthrough — screen by screen

### 1) Home (`streamlit_app.py`)

- *"You can see **offline vs full LLM+RAG** — I can run the UI with **no API key** for reliability, or full **OpenAI** for the interview."*
- *"Sidebar lists the **mock adapters**: Jira, Teams, Salesforce, Veeva CRM, NetSuite, BambooHR — aligned with systems named in the posting and on their Technology page."*

### 2) Case Intake

- *"Scenarios are **synthetic** — TrialMaster export issues, **IRMS** + CRM routing, **TA Scan** feasibility/KOL requests, **implementation** kickoffs — **product-aware** without touching real customer data."*
- *"**Redact** with **standard** or **strict** policy turns on **data minimization** before anything hits the model — see `docs/PRIVACY_AND_COMPLIANCE.md` for the compliance **talk track**, not legal claims."*

### 3) Case run (pipeline + policy snapshot + approvals)

- *"**Classification** picks product line and issue type — this is how you'd **separate** CTMS ops noise from **EDC** defects from **TA Scan** scoping."*
- *"**RAG** runs only when **policy** says so; otherwise you'll see an explicit **skip** in the audit — **rules first, semantics when needed**."*
- *"**Routing and proposed actions** come from a **deterministic policy matrix** — selective integrations, not spamming every system."*
- *"Expand **Policy snapshot** for risk tier, LLM allowed, and restricted path. **Approvals** are on the same page — nothing hits **mock integrations** until a human **approves**."*
- *"**Audit** and **export** live in an expander — **JSON-friendly** for **ELK/SIEM**."*
- *"Light **metrics** at the top (stored cases, restricted count, RAG skipped) are **illustrative** — in the role I'd wire real handle time and SLA."*

### 4) Policy & privacy

- *"This is the **controls** story: **LLM for interpretation**, **policy for execution**, **restricted gate** for sensitive patterns, plus the **privacy/compliance** doc inline for the interview."*

### Reference: as-is vs to-be (not a separate UI page)

- *"`docs/WORKFLOW_DISCOVERY.md` has the **friction map** if they want depth: manual triage vs one intake + approval-gated execution."*

---

## If they ask: "Are we duplicating something Anju already ships?"

- *"**No** for **Luminee** — that's **protocol → database build** AI for customers."*
- *"**No** for **IRMS case management** itself — this doesn't replace medical information workflow software; it could **sit beside** it for **internal** handoffs and **cross-system** actions."*
- *"**No** for **TA Scan** — that's clinical intelligence for sponsors/CROs; my demo routes **internal** requests **about** TA Scan data to the right team."*
- *"**Yes** to **alignment**: your **Technology** page already describes **adapters**, **CRM**, **real-time and batch** integration — I'm showing how I'd **orchestrate** and **govern** automation **above** that layer for **internal** ops."*

---

## Closing line (15 seconds)

- *"I'm not pitching a new EDC. I'm showing how I'd **measure**, **automate**, and **govern** the **internal** work that **surrounds** TrialMaster, **CTMS Master**, **IRMS MAX**, **TA Scan**, and the rest — **faster**, **auditable**, and **approval-first**."*

---

## Appendix — pages reviewed for this document

| URL / domain | Topic |
|------------|--------|
| `anjusoftware.com/about-anju/` | Mission, flagships, Valsoft |
| `anjusoftware.com/technology/` | Platform, adapters, NLQ, dashboard, suites |
| `anjusoftware.com/management/` | Tim Lyons (eClinical), Reed McLaughlin (MA), Ngoc Tang (HR) |
| `anjusoftware.com/careers/` | Only open role: Associate Director BD (Remote, US) |
| `anjusoftware.com/solutions/eclinical/` | Suite overview, Luminee, TA Scan, TrialMaster, CTMS Master |
| `anjusoftware.com/solutions/eclinical/trialmaster/` | EDC capabilities, APIs, exports, Gustave Roussy partnership |
| `anjusoftware.com/solutions/eclinical/luminee/` | AI build, Protocol Summarizer (free), data sovereignty |
| `anjusoftware.com/solutions/eclinical/ctms-master/` | CTMS features, SVR, finance, TrialMaster integration |
| `anjusoftware.com/solutions/medical-affairs/` | IRMS, iCare, Pubstrat overview |
| `anjusoftware.com/solutions/medical-affairs/irms-max/` | MI, multi-channel intake, AE/PC modules, CRM adapters, 21 CFR Part 11 |
| `anjusoftware.com/solutions/medical-affairs/icare-max/` | Self-service portal, Azure hosting, HCP self-attestation |
| `anjusoftware.com/solutions/medical-affairs/pubstrat-max/` | Publication planning, JSCA, online collaboration |
| `anjusoftware.com/medical-affairs-frequently-asked-questions/` | IRMS, iCare, Pubstrat, **MA Knowledge** FAQs |
| `anjusoftware.com/data-science/` | TA Scan, DaaS, data consolidation services |
| `anjusoftware.com/data-frequently-asked-questions/` | TA Scan capabilities, API, KOL, Feasibility Flex |
| `anjusoftware.com/partner-program/` | CRO partners, Luminee enablement |
| `anjusoftware.com/eclinical-frequently-asked-questions/` | TrialMaster, CTMS Master detailed FAQs |
| `ta-scan.io/` | Separate brand: Site Selection, Investigator ID, CI, Feasibility |

**Note:** Re-scrape or re-read product pages before interviews; marketing copy changes.
