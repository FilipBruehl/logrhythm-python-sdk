# LogRhythm Python SDK Documentation

Welcome to the documentation for `logrhythm-python-sdk`, a typed Python SDK for the
LogRhythm SIEM REST APIs.

> **Status:** early foundation stage. No API clients, authentication, transport, or
> configuration handling are implemented yet. See [Vision](vision.md) and the
> [Architecture Overview](architecture/overview.md) for what is planned.

## Where to start

- [Vision](vision.md) — long-term goals, target audience, and design philosophy.
- [Architecture Overview](architecture/overview.md) — the planned target architecture.
- [Component Model](architecture/components.md) — the planned components and how they
  depend on each other, as a diagram.
- [Design Specifications](specifications/README.md) — how "why" (ADRs), "how"
  (specifications), "implementation" (code), and user documentation relate, plus the
  numbering scheme, status model, and review criteria specifications follow.
- [SPEC-000 — Design Principles](specifications/design-principles.md) — project-wide
  architecture and implementation rules that future specifications build on.
- [SPEC-001 — SDK Client](specifications/sdk-client.md) — the `LogRhythmClient`
  composition root: responsibilities, public shape, ownership, and lifecycle
  (currently `Draft`, not implemented).
- [SPEC-002 — Configuration](specifications/configuration.md) — the `Configuration`
  component: sources, validation, secrets handling, and integration with
  `LogRhythmClient` (currently `Draft`, not implemented).
- [SPEC-003 — Authentication](specifications/authentication.md) — how authentication
  information is represented, its integration with `Configuration` and
  `LogRhythmClient`, and secret handling (currently `Draft`, not implemented).
- [SPEC-004 — TLS](specifications/tls.md) — secure defaults, certificate and
  hostname verification, and trust store configuration (currently `Draft`, not
  implemented).
- [SPEC-005 — Transport](specifications/transport.md) — the SDK's single HTTP
  boundary: URL resolution, HTTP client management, authentication and TLS
  integration, response handling, and redaction (currently `Draft`, not
  implemented).
- [SPEC-006 — Logging](specifications/logging.md) — structured events, request IDs,
  the logger hierarchy, and the Transport/API-module logging split (currently
  `Draft`, not implemented).
- [SPEC-007 — Exception Handling](specifications/exceptions.md) — the public
  exception hierarchy, HTTP-to-exception mapping, exception context, and
  redaction (currently `Draft`, not implemented).
- [SPEC-008 — Models](specifications/models.md) — the Pydantic v2 model
  hierarchy, request/response validation strictness, aliasing, and UTC date/time
  normalization (currently `Draft`, not implemented).
- [SPEC-009 — Filters, Pagination, Sorting and Options](specifications/filters-and-options.md) —
  filter/pagination/sorting/options models, query and header serialization, and
  conflict handling (currently `Draft`, not implemented).
- [SPEC-010 — API Modules](specifications/api-modules.md) — the seven API modules,
  the client/resource hierarchy, dependency injection, and the high-level vs. Raw
  API split (currently `Draft`, not implemented).
- [API Coverage Matrix](coverage/api-coverage.md) — tracks, per LogRhythm API area,
  how far each endpoint has progressed from not-yet-inventoried to implemented.
- [Developer Workflow](development/workflow.md) — contributor-oriented navigation
  for branching, commits, pull requests, readiness/completion criteria, and testing.
- [AI Coding Agent Governance](../AGENTS.md) — the single, vendor-neutral source
  of truth for AI Coding Agent roles, lifecycle, context recovery, authority,
  Git safety, quality gates, security, and completion reports.
- [Branch Types & Branch Strategy](development/branching.md) — `main`,
  `integration/*`, `feature/*`, `fix/*`; creation, updates, merge order, and
  deletion.
- [Commit Strategy](development/commits.md) — Conventional Commits, allowed types
  and scopes, and the linear-history (rebase-and-merge) decision.
- [Pull Requests](development/pull-requests.md) — when a PR is required, required
  content, Definition of Review, merge prerequisites, and Branch Protection
  recommendations.
- [Definition of Ready](development/definition-of-ready.md) — when an
  implementation task may begin.
- [Definition of Done](development/definition-of-done.md) — when a work package is
  complete.
- [Dependencies & Tooling](development/dependencies.md) — the runtime dependency
  baseline (Pydantic, HTTPX, PyYAML), dependency placement/versioning, and the
  dependency-upgrade process.
- [Development: Contributing](development/contributing.md) — local setup and quality checks.
- [Pre-Commit & Local Code Quality Automation](development/pre-commit.md) — hook
  installation, hook types (pre-commit/pre-push), the local quality check
  (`pre-commit run --all-files`), and troubleshooting.
- [Development: Testing](development/testing.md) — how the test suite is organized,
  and testing rules by change type.
- [GitHub Actions: CI & Build](development/ci.md) — the server-side `CI / quality`
  → `CI / test` pipeline, the separate build/package-verification workflow,
  actionlint, SHA-pinning, and Branch Protection recommendations.
- [Repository Templates & Markdown Tooling](development/templates.md) — the
  pull request template, GitHub Issue Forms, document templates (ADR, SPEC,
  API Resource), Template Governance, and markdownlint.
- [Claude Code: Technical Settings](development/claude-code.md) — the
  tool-specific `.claude/settings.json` permission model. The repository-root
  tool adapters are [`CLAUDE.md`](../CLAUDE.md) and [`CODEX.md`](../CODEX.md);
  different AI Coding Agents may use the repository under the same AGENTS.md
  rules, and further adapters may be added only when technically needed.
- [API Implementation Workflow](development/api-implementation-workflow.md) — the process
  used to add support for a new LogRhythm API.
- [Architecture Decision Records](adr/README.md) — recorded, significant architecture
  decisions and their rationale, and the policy for when a new ADR is required.

## Project layout

```text
src/logrhythm_sdk/   Importable package (src layout)
tests/unit/          Unit tests
tests/integration/   Integration tests (added once there is something to integrate with)
docs/                This documentation
AGENTS.md             Vendor-neutral AI Development governance
CLAUDE.md             Claude Code adapter
CODEX.md              Codex adapter
```
