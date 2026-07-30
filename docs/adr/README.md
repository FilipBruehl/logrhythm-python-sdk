# Architecture Decision Records

This directory records significant architecture decisions for
`logrhythm-python-sdk`, using a lightweight ADR format.

## Format

Each ADR contains:

- **Title**
- **Status** (e.g. `Proposed`, `Accepted`, `Superseded`)
- **Context** — the situation and forces at play
- **Decision** — what was decided
- **Consequences** — the resulting tradeoffs, positive and negative

## When to write one

A new ADR is required for any decision that materially shapes the SDK's public API,
its module structure, its dependency footprint, or its quality/security posture — for
example, choosing a transport library, a configuration format, or an authentication
strategy. Routine implementation details do not need an ADR.

## Index

| # | Title | Status |
|---|-------|--------|
| [0001](0001-python-313.md) | Python 3.13 as the development baseline | Accepted |
| [0002](0002-src-layout.md) | `src` layout and package namespace | Accepted |
| [0003](0003-quality-tooling.md) | Ruff, mypy, and pytest as quality tooling; Google-style docstrings | Accepted |
| [0004](0004-documentation-and-adrs.md) | Markdown documentation under `/docs` and Architecture Decision Records | Accepted |
