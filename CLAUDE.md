# CLAUDE.md

This file is the binding working guide for Claude Code sessions in this repository.
Read it before making changes.

## Project vision

`logrhythm-python-sdk` is a typed Python SDK for the LogRhythm SIEM REST APIs. It will
eventually cover seven API areas — Administration, AI Engine Cache Drilldown,
Metrics, AI Engine, Alarm, Case, and Search — all exposed through a single
high-level entry point backed by consistently structured API modules. See
[docs/vision.md](docs/vision.md) and
[docs/architecture/overview.md](docs/architecture/overview.md) for the full picture.

## Current development phase

**Phase A.2.1 — Architecture Framework (documentation only).** Beyond the Phase A.1
repository scaffolding, the project now also has a documented target architecture:
a [Component Model](docs/architecture/components.md), project-wide
[Design Principles](docs/specifications/design-principles.md), a
[Design Specifications](docs/specifications/README.md) process, and an (empty)
[API Coverage Matrix](docs/coverage/api-coverage.md). There is still no HTTP
transport, authentication, TLS logic, configuration loader, Pydantic models,
YAML/JSON/TOML handling, logging handlers, API clients, resources, filters, or
concrete LogRhythm endpoints in code. Do not add these until the task at hand
explicitly calls for that phase of work.

## Target architecture

- A central high-level facade composes shared `core` infrastructure with individual
  API modules.
- `logrhythm_sdk.core` holds everything shared across API modules: transport,
  configuration, authentication, TLS, logging. It never depends on a specific API
  module.
- Each API module (once implemented) follows the same internal shape: `models`,
  `filters`, `resources`, `client`. API-specific logic lives only there.
- Composition over inheritance; avoid deep or unnecessary class hierarchies.
- Full details: [docs/architecture/overview.md](docs/architecture/overview.md) and the
  [Component Model](docs/architecture/components.md). Project-wide architecture and
  implementation rules are collected in
  [Design Principles](docs/specifications/design-principles.md).

## Directory and module conventions

- `src`-layout; the importable package is `logrhythm_sdk` under `src/logrhythm_sdk/`.
- `src/logrhythm_sdk/py.typed` marks the package as typed (PEP 561) — keep it.
- `tests/unit/` for isolated tests; `tests/integration/` for tests exercising a real
  or mocked LogRhythm instance (added once there is a transport to integrate).
- Do not create empty placeholder directories for future API modules speculatively;
  create a module only when it is actually being implemented.
- Documentation lives under `/docs` in Markdown; significant architecture decisions
  get an ADR under `docs/adr/` (format: Title, Status, Context, Decision,
  Consequences).

## Naming conventions

- Import package: `logrhythm_sdk`. Distribution/PyPI name: `logrhythm-python-sdk`.
- Modules and functions: `snake_case`. Classes: `PascalCase`. Constants:
  `UPPER_SNAKE_CASE`.
- Keep names consistent with LogRhythm's own API terminology where it exists, rather
  than inventing SDK-specific synonyms.

## Typing rules

- All code under `src/logrhythm_sdk` must be fully typed; mypy runs in strict mode
  (`disallow_untyped_defs`, `disallow_incomplete_defs`, `no_implicit_optional`,
  `warn_unused_ignores`, `warn_unreachable`, and related strict options — see
  `pyproject.toml`).
- Do not add `# type: ignore` without a specific reason; unused ignores are treated
  as errors.

## Docstrings

- Google-style docstrings on all public modules, classes, and functions.
- Test functions are exempt from the docstring requirement (Ruff per-file-ignores for
  `tests/**`); a descriptive test name should carry that intent instead.

## Test requirements

- Every new public component needs tests that verify real behavior, not just
  coverage padding.
- Unit tests never perform real network calls.
- Run `uv run pytest` before considering any change complete.
- See [docs/development/testing.md](docs/development/testing.md).

## Security requirements

- TLS certificate verification will default to enabled once transport exists;
  disabling it must always be an explicit, deliberate action by the caller, never a
  default.
- Bearer tokens and other secrets must never be logged, printed, or included in
  exception messages, at any log level or output format.
- Never commit real secrets (tokens, credentials, customer data) anywhere in the
  repository — code, tests, fixtures, examples, or documentation.

## Do not invent API behavior

Never guess at or invent undocumented LogRhythm API behavior, fields, parameters, or
error semantics. If official documentation is missing, ambiguous, or contradictory,
say so explicitly (in code comments, docstrings, or `/docs`) instead of filling the
gap with an assumption. See
[docs/development/api-implementation-workflow.md](docs/development/api-implementation-workflow.md).

## Public vs. internal APIs

- Anything not explicitly exported from a package's `__init__.py` (via `__all__`) is
  internal and may change without notice.
- Internal package structure (e.g. helper submodules under `core`) must never become
  an accidental part of the public API surface. Import from and document only the
  intended public entry points.
- Changes to an already-public surface (client methods, models, exceptions) are
  compatibility-relevant and should be treated with corresponding care.

## Documentation duties

- New public components require corresponding documentation under `/docs` in the same
  change that introduces them.
- Significant architecture decisions require a new ADR under `docs/adr/`, following
  the existing format and numbering.
- Before implementing a component, prefer designing it as a Design Specification
  under `docs/specifications/` first — see
  [docs/specifications/README.md](docs/specifications/README.md) for the status model
  and how specifications relate to ADRs, code, and user documentation.
- Per-endpoint implementation progress belongs in
  [docs/coverage/api-coverage.md](docs/coverage/api-coverage.md), not invented ahead
  of the actual documentation inventory.

## Change discipline

- Keep changes small and focused on the requested task; do not perform unrelated
  cleanup, refactors, or drive-by changes in the same change.
- Do not modify files outside the scope of the current task.
- **Never create a git commit without an explicit instruction to do so** from the
  user, even after making and verifying changes.

## Required quality commands

A task is only complete once all four of the following succeed:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
```

Formatting issues and lint/type errors within the scope of the current task should be
fixed before reporting the task as done.
