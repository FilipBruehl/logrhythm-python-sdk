# Definition of Done

A work package is complete only once every item below is satisfied. This is
the binding completion checklist for every change, regardless of size or
author.

## Tests

- Every new or changed public behavior has tests verifying real behavior, per
  [Testing Rules](testing.md#testing-rules-by-change-type) — not coverage
  padding.
- All tests pass (`uv run pytest`).
- Unit tests perform no real network calls.

## Documentation

- Documentation under `/docs` is updated in the same change for any new or
  changed public component (see
  [`AGENTS.md`](../../AGENTS.md#definition-of-done)).
- Google-style docstrings exist for all public modules, classes, and functions
  touched.
- [API Coverage Matrix](../coverage/api-coverage.md) is updated for any
  endpoint-level implementation work.
- `CHANGELOG.md` is updated under `Unreleased` for every user-visible change.
- A release-preparation change satisfies the version, changelog, build,
  verification, and release-readiness requirements in
  [Release & Publishing](release.md).

## Architecture conformance

- The change matches the relevant `Accepted` SPEC(s); any necessary deviation
  is itself documented in the same change (a SPEC update) or escalated per
  [Architecture Governance](../../AGENTS.md#architecture-governance) —
  never a silent departure.
- No new architectural decision (SPEC content, ADR-worthy choice) was made
  without following
  [Architecture Governance](../../AGENTS.md#architecture-governance).

## Public API

- Any new or changed public export is deliberate, added via `__all__`, and
  documented — see [`AGENTS.md`](../../AGENTS.md#implementation-rules).
- Any change to an already-public surface (client methods, models, exceptions)
  is flagged as compatibility-relevant in the PR (see
  [Pull Requests, Required PR content](pull-requests.md#required-pr-content)).

## Security

- No secrets, credentials, tokens, or real customer data appear anywhere in
  the change — code, tests, fixtures, docs, or commit messages.
- Security-relevant defaults (TLS verification, redaction, secret handling)
  follow
  [SPEC-000's security principles](../specifications/design-principles.md#security-principles)
  wherever the change touches them.

## Quality checks

All four pass, with results recorded in the completion report:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
```

These are enforced automatically, twice over: locally via git hooks (see
[Pre-Commit & Local Code Quality Automation](pre-commit.md)) and server-side
through the required `CI / commit-message`, `CI / quality`, and `CI / test`
status checks (see [GitHub Actions: CI, Build & Release](ci.md)); `quality` and
`test` enforce the four commands above. Running them locally first, and reporting
the results, is still expected — the automation is a backstop, not a substitute
for checking before reporting a task done.

## Change hygiene

- `git diff` has been reviewed and confirmed to touch only files within the
  task's stated scope — no drive-by changes.
- `git status` is clean of stray or unintended untracked/modified files before
  the change is reported complete.
- Commits follow [Commit Strategy](commits.md) (Conventional Commits,
  appropriate size and scope) — mechanically checked by the local
  `commit-msg` hook and the `CI / commit-message` status check, per
  [Pre-Commit, Commit-message validation](pre-commit.md#commit-message-validation).

## Completion report

A short report is produced covering: files added/changed, what changed and
why, assumptions, open risks, known limitations, quality-check results,
`git diff --stat`, `git status --short`, and — for AI-assisted work — whether
any commit, push, PR, merge, release, or repository-administration action
occurred. See [`AGENTS.md`](../../AGENTS.md#completion-reports).

## See also

- [Definition of Ready](definition-of-ready.md)
- [Testing Rules](testing.md#testing-rules-by-change-type)
- [Architecture Governance](../../AGENTS.md#architecture-governance)
- [GitHub Actions: CI, Build & Release](ci.md)
- [Release & Publishing](release.md)
- [`AGENTS.md`](../../AGENTS.md) — binding AI Development governance.
