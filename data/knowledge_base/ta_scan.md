# TA Scan — Clinical and commercial intelligence platform

TA Scan (ta-scan.io) aggregates public-domain clinical trial, publication, presentation, and demographic data into a single intuitive platform. It serves Clinical Operations, Medical Affairs, and commercial teams.

## Platform modules

- **Site Selection**: Prioritize sites with proven experience, available capacity, and the right patient mix globally. Site Capacity Calculator estimates workload and recruitment potential.
- **Investigator / KOL Identification**: Score, rank, and engage key opinion leaders (KOLs) and investigators using publication, presentation, trial, and fee disclosure data. Proprietary tiering algorithms reduce manual effort in ranking.
- **Competitive Intelligence**: Map the therapeutic landscape — compare sponsor activity, overlapping sites, trial timing. Identify whitespace opportunities.
- **Strategic Feasibility (Feasibility Flex)**: Predictive enrollment modeling, country-level timeline visualization, data-backed feasibility plans.

## Scale

- 480K+ clinical trials, 2.4M+ HCPs, 350K+ sites, 550+ indications, 7.2M+ publications, 790K+ presentations.
- Data refreshed weekly from hundreds of public sources including trial registries, PubMed, conferences, fee disclosures, census data.

## Delivery modes

- **Web platform**: Intuitive interface with dashboards, analytics, filtering, reporting.
- **API services**: TA Scan data directly into customer systems (CTMS, CRM, data lakes).
- **Data-as-a-Service (DaaS)**: Tailored datasets, rapid RFP responses (48h turnaround for CROs), custom competitive analyses.

## Common issue categories for internal routing

- **Custom data requests**: Scoping, delivery format, or refresh cadence — route to `TA-DataServices` with SLA 48–120h depending on scope.
- **API / delivery**: Authentication, rate limits, or payload errors — `TA-Platform` with SLA 24–48h.
- **Feasibility / KOL requests**: Investigator identification, site capacity analysis, or KOL profiling — may involve Data Science team and account management.
- **Content questions**: Clarify therapeutic area, geography, or time window before routing.

## Default routing

- **Primary queue**: `TA-Support` — general product issues.
- **Escalation**: `TA-DataServices` — bespoke reports, competitive intelligence, or feasibility packages.
- **Professional Services**: Large enterprise onboarding, multi-source data contracts, or API integration projects.

## Integration notes

- TA Scan data can be integrated into third-party CTMS and CRM systems via API.
- Data consolidation services available: combine customer's investigator/KOL data with TA Scan public data into single source of truth.
