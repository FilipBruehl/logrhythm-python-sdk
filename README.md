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
2. AI Engine API
3. Metrics API
4. Alarm API
5. Search API
6. Further APIs, added in later phases

See [docs/vision.md](docs/vision.md) for the full long-term vision and
[docs/architecture/overview.md](docs/architecture/overview.md) for the planned target
architecture.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Development setup

```powershell
uv sync
```

This installs the project along with its development dependencies (Ruff, mypy,
pytest, pytest-cov) into a local virtual environment.

## Quality checks

```powershell
uv run ruff format --check .   # formatting check
uv run ruff format .           # apply formatting
uv run ruff check .            # linting
uv run mypy src/logrhythm_sdk  # static type checking
uv run pytest                  # tests + coverage
```

## Architecture (planned)

The SDK is designed around a central high-level facade backed by a shared `core`
(transport, configuration, authentication, TLS, logging) and a set of API modules,
each following the same internal structure (models, filters, resources, client). None
of this is implemented yet beyond the package skeleton — see
[docs/architecture/overview.md](docs/architecture/overview.md) for the full picture,
[docs/architecture/components.md](docs/architecture/components.md) for a component
diagram, and [docs/specifications/](docs/specifications/) for the numbered Design
Specifications that govern how these components are designed — starting with
[SPEC-000 — Design Principles](docs/specifications/design-principles.md),
[SPEC-001 — SDK Client](docs/specifications/sdk-client.md),
[SPEC-002 — Configuration](docs/specifications/configuration.md),
[SPEC-003 — Authentication](docs/specifications/authentication.md), and
[SPEC-004 — TLS](docs/specifications/tls.md) (all currently `Draft`, not
implemented). Per-endpoint progress is tracked in
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
