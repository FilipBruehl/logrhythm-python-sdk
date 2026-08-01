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

**Phase A.2 — Architecture & Specification (documentation only) — complete.** The
project now has a complete architecture and specification basis: a
[Component Model](docs/architecture/components.md), project-wide
[Design Principles](docs/specifications/design-principles.md), a
[Design Specifications](docs/specifications/README.md) process, and the full,
numbered Design Specification series from
[SPEC-000](docs/specifications/design-principles.md) through
[SPEC-010](docs/specifications/api-modules.md) — covering Design Principles, SDK
Client, Configuration, Authentication, TLS, Transport, Logging, Exception
Handling, Models, Filters/Pagination/Sorting/Options, and API Modules. The
[API Coverage Matrix](docs/coverage/api-coverage.md) exists as a structure only —
no endpoint has been inventoried yet.

**Phase A.3.1 — Developer Workflow & Governance (documentation only) — complete.**
The project now also has a binding development workflow: branch types and
strategy, commit strategy, pull request requirements, Definition of Ready,
Definition of Done, testing rules by change type, ADR policy, and the governance
rules that constrain Claude's own behavior in this repository — see
[Developer Workflow](docs/development/workflow.md) and
[Claude Workflow & Architecture Governance](docs/development/claude-workflow.md).
No hooks, CI, or templates exist yet to enforce any of this automatically; it is
applied manually until a later phase adds that tooling.

**Phase A.3.2 — Dependencies & Tooling Baseline (documentation + dependency
declarations only) — complete.** The SDK's runtime dependency baseline is now
declared: Pydantic v2, HTTPX, and PyYAML (see
[Dependencies & Tooling](docs/development/dependencies.md),
[ADR-0005](docs/adr/0005-pydantic-v2-models.md),
[ADR-0006](docs/adr/0006-httpx-transport.md), and
[ADR-0007](docs/adr/0007-configuration-file-formats.md)), and the Pydantic mypy
plugin is enabled. SPEC-002's previously open configuration-file-format question
is now closed by ADR-0007.

**None of this is implemented in runtime code yet.** `src/logrhythm_sdk` remains
the Phase A.1 package skeleton: there is still no HTTP transport, authentication,
TLS logic, configuration loader, Pydantic models, YAML/JSON/TOML handling, logging
handlers, API clients, resources, filters, or concrete LogRhythm endpoints in code
— the runtime dependencies declared in Phase A.3.2 are not yet used by any code.
Do not add these until the task at hand explicitly calls for that phase of work.

## Target architecture

- A central high-level facade composes shared `core` infrastructure with individual
  API modules.
- `logrhythm_sdk.core` holds everything shared across API modules: transport,
  configuration, authentication, TLS, logging. It never depends on a specific API
  module.
- Each API module (once implemented) follows the same internal shape: a `client.py`
  per API area, with `resource.py`, models, filters, sorting, and options organized
  per resource beneath it. API-specific logic lives only there.
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
- Runtime dependencies go in `pyproject.toml`'s `[project.dependencies]`;
  development tools stay in `[dependency-groups.dev]`; `uv.lock` is versioned. See
  [Dependencies & Tooling](docs/development/dependencies.md).

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
- The official Pydantic mypy plugin (`pydantic.mypy`) is enabled, with
  `init_typed`, `init_forbid_extra`, and `warn_required_dynamic_aliases` set — see
  [ADR-0005](docs/adr/0005-pydantic-v2-models.md) and
  [Dependencies & Tooling](docs/development/dependencies.md).

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
  the existing format and numbering — see
  [ADR Policy](docs/adr/README.md#when-an-adr-is-required) for when this applies.
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

## Branching, commits, and pull requests

The binding process is documented in full under
[Developer Workflow](docs/development/workflow.md); this is the summary:

- **Branches:** exactly four types — `main` (stable, PR-only), `integration/*`
  (larger, multi-resource efforts), `feature/*` (one logically complete work
  package), `fix/*` (bug fixes). No deeper hierarchy. See
  [Branch Types & Branch Strategy](docs/development/branching.md).
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/).
  Commit history is preserved — **squash-merge is not the default**; prefer
  Rebase and Merge to keep `main` linear. See
  [Commit Strategy](docs/development/commits.md).
- **Pull requests:** every change reaching `main` goes through a PR. See
  [Pull Requests](docs/development/pull-requests.md) for required content and
  merge prerequisites.
- **Before starting work**, check
  [Definition of Ready](docs/development/definition-of-ready.md); before
  reporting a task done, check
  [Definition of Done](docs/development/definition-of-done.md).

## Architecture governance

**Claude does not make architecture decisions.** If a task turns out to touch a
SPEC, an ADR, the Public API's shape, Security Defaults, Ownership, or Lifecycle
— and the existing documentation doesn't already give a clear, binding answer —
**stop and get an explicit decision from the user before proceeding.** Report
what was found and why it's a decision, not an implementation detail; do not
silently pick the most reasonable-looking option and continue. See
[Architecture Governance](docs/development/claude-workflow.md#architecture-governance)
and [ADR Policy](docs/adr/README.md#when-an-adr-is-required).

## Claude's git and PR permissions

- **Branches:** may create an explicitly named `feature/*` or `integration/*`
  branch, switch to it, and check its status. Never plans or creates additional
  branch structure on its own initiative.
- **Commits:** only after explicit approval for that specific commit, and only
  once all four quality commands pass. No WIP commits.
- **Push:** only on explicit instruction. Never directly to `main`. Never force
  push.
- **Pull requests:** may prepare/draft a PR description; creates the actual PR
  only on explicit instruction. Never merges a PR, changes branch protection, or
  triggers a release.

Full detail: [Claude Workflow](docs/development/claude-workflow.md).

## Git safety rules

Never performed without the user's explicit, scoped approval for that exact
operation: `git reset --hard`, `git clean`, force push (including
`--force-with-lease`), `git commit --amend`, branch deletion, or `git rebase`
(interactive or not). Before any command that could discard uncommitted work,
run `git status` first; existing user changes are never discarded or overwritten
without asking. Stage only the files relevant to the approved change (avoid
`git add -A`/`git add .`); review `git status` and `git diff` before every
commit. Full detail:
[Git Safety Rules](docs/development/claude-workflow.md#git-safety-rules).

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
