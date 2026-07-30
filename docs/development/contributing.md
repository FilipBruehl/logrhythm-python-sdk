# Contributing (Development Guide)

This page covers local setup and the quality checks expected to pass before any
change is considered done. See also the repository root [CONTRIBUTING.md](../../CONTRIBUTING.md)
for the short version, and [testing.md](testing.md) for test-suite conventions.

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Setup

```powershell
uv sync
```

This creates a local virtual environment and installs the project together with its
development dependencies (Ruff, mypy, pytest, pytest-cov).

## Quality checks

Every change must pass all four of the following commands before it is considered
complete:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
```

To auto-format instead of only checking:

```powershell
uv run ruff format .
```

## Conventions

- Google-style docstrings on all public modules, classes, and functions.
- Full type annotations everywhere; mypy runs in strict mode against
  `src/logrhythm_sdk`.
- Shared logic belongs in `logrhythm_sdk.core`; API-specific logic stays inside its
  own API module.
- Prefer composition over inheritance.
- New public components require tests and documentation in the same change.
- Significant architecture decisions are recorded as an ADR under `docs/adr/`.
