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

## When an ADR is required

An ADR is required, before the decision is acted on, whenever a change involves any
of the following:

- **A new core/runtime library**, or replacing one already in use (e.g. choosing
  `httpx`, Pydantic, or swapping either out) — unless that exact choice is already
  fixed as a binding decision in an `Accepted` [Design Specification](../specifications/README.md),
  in which case implementing it is not a new decision.
- **A security-relevant default or mechanism** — TLS verification behavior, secret
  handling/redaction, or the supported authentication mechanism.
- **The Public API's shape or compatibility contract** — client methods, models, or
  exceptions actually exported, once something has shipped as public.
- **Ownership** of a shared component — who creates, holds, or releases it.
- **Lifecycle** of a shared component — creation, closing, or reuse rules.
- **A dependency change** with structural consequences — adding, removing, or
  changing the constraints on a dependency in a way that affects the public surface
  or supported environment (e.g. raising the minimum Python version, as in
  [ADR-0001](0001-python-313.md)).
- **A long-term architectural decision** that reverses or materially changes a
  decision already recorded in a SPEC or a previous ADR.

In general: any decision that materially shapes the SDK's public API, module
structure, dependency footprint, or quality/security posture needs an ADR; routine
implementation details do not.

See [Architecture Governance](../development/claude-workflow.md#architecture-governance)
for what happens when this is discovered mid-implementation: work stops until the
ADR (and any dependent SPEC update) exists.

## When an ADR is not required

- The change is purely an internal implementation detail with no effect on the
  public surface, security posture, ownership/lifecycle rules, or dependency
  footprint.
- The change follows a decision already recorded in an `Accepted` SPEC or an
  existing ADR — implementing an already-decided design does not need a new ADR,
  only the SPEC/code itself.
- Routine bugfixes, refactors, documentation edits, or test additions that do not
  change an already-decided architectural rule.
- Adding a new resource or endpoint to an already-decided API module, following the
  shape [SPEC-010](../specifications/api-modules.md) already establishes — this
  implements an existing decision rather than making a new one.

## Index

| # | Title | Status |
|---|-------|--------|
| [0001](0001-python-313.md) | Python 3.13 as the development baseline | Accepted |
| [0002](0002-src-layout.md) | `src` layout and package namespace | Accepted |
| [0003](0003-quality-tooling.md) | Ruff, mypy, and pytest as quality tooling; Google-style docstrings | Accepted |
| [0004](0004-documentation-and-adrs.md) | Markdown documentation under `/docs` and Architecture Decision Records | Accepted |
| [0005](0005-pydantic-v2-models.md) | Use Pydantic v2 for SDK models | Accepted |
| [0006](0006-httpx-transport.md) | Use HTTPX as HTTP transport library | Accepted |
| [0007](0007-configuration-file-formats.md) | Support YAML, JSON, and TOML configuration files | Accepted |
