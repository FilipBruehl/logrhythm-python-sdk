# Contributing

Thanks for your interest in contributing to `logrhythm-python-sdk`. This project is in
an early, pre-alpha foundation stage — see [README.md](README.md) for current status.

## Local setup

Requirements: Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```powershell
uv sync
```

## Quality checks

All four of the following must pass before a change is considered complete:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
```

## Guidelines

- Keep changes small and focused; avoid mixing unrelated changes in one PR.
- Public components need type annotations, Google-style docstrings, tests, and
  documentation in `/docs`.
- Shared logic belongs in `logrhythm_sdk.core`; API-specific logic stays in its own
  API module.
- Prefer composition over inheritance; avoid deep class hierarchies.
- Record significant architecture decisions as an ADR under `docs/adr/` (see
  [docs/adr/README.md](docs/adr/README.md)).
- Never invent or guess undocumented LogRhythm API behavior — see
  [docs/development/api-implementation-workflow.md](docs/development/api-implementation-workflow.md).
- Never commit real secrets (tokens, credentials) in code, tests, examples, or logs.

For more detail, see [docs/development/contributing.md](docs/development/contributing.md)
and [docs/development/testing.md](docs/development/testing.md).
