# Pull Requests

This page defines when a pull request is required, what it must contain, how
it is reviewed, and what must be true before it can be merged. The
[pull request template](../../.github/pull_request_template.md) — one shared
template for every PR, per
[Repository Templates & Markdown Tooling](templates.md) — mirrors the
requirements below as fill-in-the-blank sections and a checklist; this page
remains the normative source if the two ever disagree (see
[Template Governance](templates.md#template-governance)).

## When a PR is required

- **Every** change that reaches `main` goes through a PR — no direct pushes to
  `main`, ever (see [Branch Types](branching.md#main) and
  [`AGENTS.md`, Git workflow](../../AGENTS.md#git-workflow)).
- Every `feature/*`/`fix/*` branch merging into an `integration/*` branch also
  goes through a PR, so each resource receives the same review discipline
  before the combined integration effort reaches `main` (see
  [Branch Strategy, Model B](branching.md#model-b--larger-work-package-integration-branch)).
- This applies regardless of author (human or AI Coding Agent) and regardless of change
  size — there is no "too small for a PR" exception once work leaves a
  contributor's local branch.

## Required PR content

Every PR description states, at minimum:

- **What** changed and **why** — the problem or goal, not just a restatement of
  the diff.
- Which **SPEC(s)** and/or **ADR(s)** the change implements or is governed by,
  if any.
- **Scope** — which files/components were touched, and confirmation that
  nothing outside that scope was touched (see
  [`AGENTS.md`](../../AGENTS.md#working-agreements)).
- **Test plan** — what was tested and how: new tests added, existing tests
  still passing, any manual verification performed.
- **Quality check results** — confirmation that `ruff format --check`,
  `ruff check`, `mypy`, and `pytest` all pass (see
  [Definition of Done](definition-of-done.md)). The `CI / quality` and
  `CI / test` checks (see [GitHub Actions: CI, Build & Release](ci.md)) confirm this
  automatically once the PR is open — restating it in the description is
  still expected, since the checks run after the description is written.
- **Documentation impact** — which docs were updated in the same change, or an
  explicit note that none were needed and why.
- **Breaking-change flag** — explicitly called out if the change affects the
  public API's shape or compatibility contract.
- **Open questions / follow-ups**, if any remain.

## Definition of Review

Before approving, a reviewer confirms:

- The change matches the relevant `Accepted` SPEC(s)/ADR(s) — or, if it
  doesn't, that the deviation is itself explicitly documented and justified,
  never silent.
- The change stays within its stated scope; no unrelated drive-by edits.
- New or changed public behavior has tests verifying real behavior (see
  [Testing Rules](testing.md#testing-rules-by-change-type)).
- Documentation was updated in the same change where required (see
  [Definition of Done](definition-of-done.md)).
- No secrets, credentials, or real customer data appear anywhere in the diff.
- Commit history follows [Commit Strategy](commits.md) (types, scopes, size,
  content).
- Any change touching Public API, Ownership, Lifecycle, Security Defaults, a
  SPEC, or an ADR was explicitly, deliberately decided — not something that
  happened incidentally as part of unrelated work (see
  [Architecture Governance](../../AGENTS.md#architecture-governance)).

## Merge prerequisites

A PR may be merged only once:

- All four required quality commands pass. This is now automatically
  confirmed server-side by `CI / quality` and `CI / test` (see
  [GitHub Actions: CI, Build & Release](ci.md)), in addition to the local pre-commit
  hooks from [Pre-Commit & Local Code Quality Automation](pre-commit.md) —
  still restated and reported in the PR / completion report.
- At least one review has been completed against the
  [Definition of Review](#definition-of-review) above. Where no second
  reviewer is available yet, the author explicitly performs and records a
  self-review against the same checklist rather than skipping it.
- All review feedback is resolved — addressed, or explicitly discussed and
  dismissed with reasoning — with no comments left unresolved.
- The source branch is up to date with its target (rebased, per
  [Commit Strategy](commits.md#binding-decision-linear-history-no-default-squash-merge))
  so the merge lands as a linear, fast-forward-style merge.
- For an `integration/*` branch: every planned `feature/*`/`fix/*` branch for
  that effort has already been merged into it (see
  [Branch Strategy, Model B](branching.md#model-b--larger-work-package-integration-branch)).

## Branch Protection

Concrete branch protection / ruleset recommendations — including the required
status checks `CI / quality` and `CI / test` now that
[GitHub Actions: CI, Build & Release](ci.md) exists — are documented in
[GitHub Actions, Branch Protection / Rulesets recommendations](ci.md#branch-protection--rulesets-recommendations).
These are **not** configured through the GitHub API or UI as part of any
phase so far; they are applied by hand, per that page.

## See also

- [Branch Types & Branch Strategy](branching.md)
- [Commit Strategy](commits.md)
- [Definition of Done](definition-of-done.md)
- [GitHub Actions: CI, Build & Release](ci.md) — the `CI / quality` and `CI / test`
  checks, and branch protection recommendations.
- [`AGENTS.md`, Push and pull requests](../../AGENTS.md#push-and-pull-requests) —
  AI Coding Agent authority for PR-related actions.
- [Repository Templates & Markdown Tooling](templates.md) — the pull request
  template, issue forms, and document templates.
