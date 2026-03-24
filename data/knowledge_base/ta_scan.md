# TA Scan — Competitive intelligence and data delivery

TA Scan aggregates public-domain intelligence and delivers data via UI or API.

## Common issue categories

- **Custom data requests**: Scoping, delivery format, or refresh cadence — route to `TA-DataServices` with SLA 48–120h depending on scope.
- **API / delivery**: Authentication, rate limits, or payload errors — `TA-Platform` with SLA 24–48h.
- **Content questions**: Clarify therapeutic area, geography, or time window before routing.

## Default routing

- **Primary queue**: `TA-Support` — general product issues.
- **Escalation**: `TA-DataServices` — bespoke reports or competitive intelligence packages.
- **Professional Services**: Large enterprise onboarding or multi-source data contracts.
