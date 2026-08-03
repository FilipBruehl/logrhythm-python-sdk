# Contributing

Thanks for your interest in contributing to `logrhythm-python-sdk`. This project is in
an early, pre-alpha foundation stage — see [README.md](README.md) for current status.

## Local setup

Requirements: Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```powershell
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

The last two commands install the local git hooks (formatting/linting/type
checks + secret detection on commit, the test suite on push) — see
[docs/development/pre-commit.md](docs/development/pre-commit.md).

## Quality checks

All four of the following must pass before a change is considered complete:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
```

The official local quality check — formatting, linting, and type checking,
without the test suite — is `uv run pre-commit run --all-files`; see
[docs/development/pre-commit.md](docs/development/pre-commit.md#local-quality-check).
The local git hooks (see [Workflow](#workflow) below) run the same checks
automatically at commit and push time.

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

## Workflow

- **Branching:** `main` is always stable; work happens on `feature/*`/`fix/*`
  branches, with `integration/*` branches for larger, multi-resource efforts. See
  [docs/development/branching.md](docs/development/branching.md).
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/); history
  is preserved (rebase-and-merge, no default squash-merge). See
  [docs/development/commits.md](docs/development/commits.md).
- **Pull requests:** every change to `main` goes through a PR, and runs
  through the `CI / quality` and `CI / test` checks automatically. See
  [docs/development/pull-requests.md](docs/development/pull-requests.md) and
  [docs/development/ci.md](docs/development/ci.md).
- **Before starting:** check [Definition of Ready](docs/development/definition-of-ready.md).
- **Before calling it done:** check [Definition of Done](docs/development/definition-of-done.md).

For more detail, see [docs/development/contributing.md](docs/development/contributing.md),
[docs/development/testing.md](docs/development/testing.md),
[docs/development/pre-commit.md](docs/development/pre-commit.md),
[docs/development/ci.md](docs/development/ci.md), and the full
[Developer Workflow](docs/development/workflow.md) index.
