# 0001 — App structure: router/service split

- Status: Accepted
- Date: 2026-06-21
- Context: Initial FastAPI scaffolding for the StockAnalyzer API.

## Context and Problem Statement

The initial version of the app put all logic in a single `main.py` (route handler
that imported yfinance directly, parsed CSV, and returned the JSON). It was hard
to test, hard to extend (we knew analysis features were coming in v1.2.0), and
hard to swap data providers later. As the workshop progressed we needed a
separation between the HTTP layer and the data layer.

## Considered Options

1. Single-file FastAPI app (status quo).
2. Router / service split: routers depend only on FastAPI; services depend only
   on the data provider. No `app.routers` imports yfinance, and no
   `app.services` imports FastAPI.
3. Full clean architecture / hexagonal with adapters, ports, DTOs.

## Decision

Option 2. We reorganized the codebase into:

```
app/
├── main.py              # FastAPI() + include_router
├── routers/
│   ├── ticker.py        # HTTP layer for /ticker/{symbol}
│   └── analysis.py      # HTTP layer for /analysis and /chart.png
└── services/
    ├── yfinance_service.py
    ├── analysis_service.py
    └── chart_service.py
```

## Consequences

Good:
- Adding `/analysis` and `/chart.png` in v1.2.0 only touched new files in
  `routers/` and `services/`. No modifications to `main.py` beyond
  `include_router`.
- yfinance is replaceable by editing only `services/yfinance_service.py`.
- Tests can be written against services without spinning up FastAPI.

Bad / trade-offs:
- Slight overhead for a one-endpoint app. Worth it given the v1.2.0 roadmap.

Rejected option 3 because the workshop's learning objectives are Kubernetes
and GitOps, not hexagonal architecture. Option 2 is enough to demonstrate
separation of concerns without becoming the topic itself.
