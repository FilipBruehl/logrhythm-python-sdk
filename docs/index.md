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
- [API Coverage Matrix](coverage/api-coverage.md) — tracks, per LogRhythm API area,
  how far each endpoint has progressed from not-yet-inventoried to implemented.
- [Development: Contributing](development/contributing.md) — local setup and quality checks.
- [Development: Testing](development/testing.md) — how the test suite is organized.
- [API Implementation Workflow](development/api-implementation-workflow.md) — the process
  used to add support for a new LogRhythm API.
- [Architecture Decision Records](adr/README.md) — recorded, significant architecture
  decisions and their rationale.

## Project layout

```text
src/logrhythm_sdk/   Importable package (src layout)
tests/unit/          Unit tests
tests/integration/   Integration tests (added once there is something to integrate with)
docs/                This documentation
```
