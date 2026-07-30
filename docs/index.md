# LogRhythm Python SDK Documentation

Welcome to the documentation for `logrhythm-python-sdk`, a typed Python SDK for the
LogRhythm SIEM REST APIs.

> **Status:** early foundation stage. No API clients, authentication, transport, or
> configuration handling are implemented yet. See [Vision](vision.md) and the
> [Architecture Overview](architecture/overview.md) for what is planned.

## Where to start

- [Vision](vision.md) — long-term goals, target audience, and design philosophy.
- [Architecture Overview](architecture/overview.md) — the planned target architecture.
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
