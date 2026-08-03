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
  changed public component (see [CLAUDE.md](../../CLAUDE.md), "Documentation
  duties").
- Google-style docstrings exist for all public modules, classes, and functions
  touched.
- [API Coverage Matrix](../coverage/api-coverage.md) is updated for any
  endpoint-level implementation work.
- `CHANGELOG.md` is updated for user-visible changes, once the SDK has
  user-visible functionality.

## Architecture conformance

- The change matches the relevant `Accepted` SPEC(s); any necessary deviation
  is itself documented in the same change (a SPEC update) or escalated per
  [Architecture Governance](claude-workflow.md#architecture-governance) —
  never a silent departure.
- No new architectural decision (SPEC content, ADR-worthy choice) was made
  without following [Architecture Governance](claude-workflow.md#architecture-governance).

## Public API

- Any new or changed public export is deliberate, added via `__all__`, and
  documented — see [CLAUDE.md](../../CLAUDE.md), "Public vs. internal APIs."
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
via the `CI / quality` and `CI / test` status checks (see
[GitHub Actions: CI & Build](ci.md)). Running them locally first, and
reporting the results, is still expected — the automation is a backstop, not
a substitute for checking before reporting a task done.

## Change hygiene

- `git diff` has been reviewed and confirmed to touch only files within the
  task's stated scope — no drive-by changes.
- `git status` is clean of stray or unintended untracked/modified files before
  the change is reported complete.
- Commits follow [Commit Strategy](commits.md) (Conventional Commits,
  appropriate size and scope).

## Completion report

A short report is produced covering: files added/changed, what changed and
why, quality-check results, `git diff --stat`, `git status --short`, and — for
Claude-driven work — confirmation that no commit, push, or PR was made without
the explicit authorization [Claude Workflow](claude-workflow.md) requires.

## See also

- [Definition of Ready](definition-of-ready.md)
- [Testing Rules](testing.md#testing-rules-by-change-type)
- [Architecture Governance](claude-workflow.md#architecture-governance)
- [GitHub Actions: CI & Build](ci.md)
