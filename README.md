# logrhythm-python-sdk

A typed Python SDK for the LogRhythm SIEM REST APIs.

## Status

**Early foundation stage — pre-alpha.** This repository currently contains project
scaffolding only: package layout, tooling configuration, documentation structure, and
a minimal importable package. There is **no** functional API client, authentication,
HTTP transport, TLS handling, or configuration loading yet. Nothing in this SDK can be
used to talk to a LogRhythm instance at this time.

## Planned API coverage

The SDK is intended to eventually support:

1. Administration API
2. AI Engine Cache Drilldown API
3. Metrics API
4. AI Engine API
5. Alarm API
6. Case API
7. Search API

See [docs/vision.md](docs/vision.md) for the full long-term vision and
[docs/architecture/overview.md](docs/architecture/overview.md) for the planned target
architecture.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Development setup

```powershell
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

This installs the project along with its development dependencies (Ruff, mypy,
pytest, pytest-cov, pre-commit) into a local virtual environment, then installs
the local git hooks that run formatting/linting/type-checks and secret
detection on every commit, and the test suite on every push — see
[docs/development/pre-commit.md](docs/development/pre-commit.md).

## Dependencies

The SDK's runtime dependency baseline is now in place, ahead of the runtime
implementation that will use it: **Pydantic v2** (models), **HTTPX** (HTTP
transport), and **PyYAML** (YAML configuration files) — see
[docs/development/dependencies.md](docs/development/dependencies.md) and
[ADR-0005](docs/adr/0005-pydantic-v2-models.md),
[ADR-0006](docs/adr/0006-httpx-transport.md), and
[ADR-0007](docs/adr/0007-configuration-file-formats.md) for the reasoning
behind each. No code uses them yet — see [Status](#status).

## Quality checks

```powershell
uv run ruff format --check .   # formatting check
uv run ruff format .           # apply formatting
uv run ruff check .            # linting
uv run mypy src/logrhythm_sdk  # static type checking
uv run pytest                  # tests + coverage
```

These same checks (minus `pytest`) run automatically at commit time, and
`pytest` runs automatically at push time, via the local git hooks — see
[docs/development/pre-commit.md](docs/development/pre-commit.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the short version, and the
[Developer Workflow](docs/development/workflow.md) for the full, binding
development workflow — branch types and strategy, commit strategy, pull
requests, and the Definition of Ready / Definition of Done every change is
checked against.

## Architecture (planned)

The SDK is designed around a central high-level facade backed by a shared `core`
(transport, configuration, authentication, TLS, logging) and a set of API modules,
each following the same internal structure (a `client.py` per API area, with
`resource.py`, models, filters, sorting, and options organized per resource). None
of this is implemented yet beyond the package skeleton — see
[docs/architecture/overview.md](docs/architecture/overview.md) for the full picture,
[docs/architecture/components.md](docs/architecture/components.md) for a component
diagram, and [docs/specifications/](docs/specifications/) for the numbered Design
Specifications that govern how these components are designed — starting with
[SPEC-000 — Design Principles](docs/specifications/design-principles.md),
[SPEC-001 — SDK Client](docs/specifications/sdk-client.md),
[SPEC-002 — Configuration](docs/specifications/configuration.md),
[SPEC-003 — Authentication](docs/specifications/authentication.md),
[SPEC-004 — TLS](docs/specifications/tls.md),
[SPEC-005 — Transport](docs/specifications/transport.md),
[SPEC-006 — Logging](docs/specifications/logging.md),
[SPEC-007 — Exception Handling](docs/specifications/exceptions.md),
[SPEC-008 — Models](docs/specifications/models.md),
[SPEC-009 — Filters, Pagination, Sorting and Options](docs/specifications/filters-and-options.md),
and [SPEC-010 — API Modules](docs/specifications/api-modules.md) (all currently
`Draft`, not implemented; see
[docs/specifications/README.md](docs/specifications/README.md) for the full,
linked index). Per-endpoint progress is tracked in
[docs/coverage/api-coverage.md](docs/coverage/api-coverage.md), which is currently an
empty structure — nothing has been inventoried or implemented yet.

## Security principles

- TLS certificate verification will be enabled by default once transport is
  implemented; disabling it will require an explicit, deliberate opt-in.
- Bearer tokens and other secrets are never logged, at any log level or format.
- See [SECURITY.md](SECURITY.md) for how to report a security concern.

## License

No license has been chosen for this project yet. Until a license is added, all rights
are reserved by default and no permissions are granted to use, copy, modify, or
distribute this code.
