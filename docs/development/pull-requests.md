# Pull Requests

This page defines when a pull request is required, what it must contain, how
it is reviewed, and what must be true before it can be merged. No PR or issue
template is created in this phase (see Scope); the requirements below are
applied manually until a template exists.

## When a PR is required

- **Every** change that reaches `main` goes through a PR — no direct pushes to
  `main`, ever (see [Branch Types](branching.md#main) and
  [Git Safety Rules](claude-workflow.md#git-safety-rules)).
- Every `feature/*`/`fix/*` branch merging into an `integration/*` branch also
  goes through a PR, so each resource receives the same review discipline
  before the combined integration effort reaches `main` (see
  [Branch Strategy, Model B](branching.md#model-b-larger-work-package-integration-branch)).
- This applies regardless of author (human or Claude) and regardless of change
  size — there is no "too small for a PR" exception once work leaves a
  contributor's local branch.

## Required PR content

Every PR description states, at minimum:

- **What** changed and **why** — the problem or goal, not just a restatement of
  the diff.
- Which **SPEC(s)** and/or **ADR(s)** the change implements or is governed by,
  if any.
- **Scope** — which files/components were touched, and confirmation that
  nothing outside that scope was touched (see [CLAUDE.md](../../CLAUDE.md),
  "Change discipline").
- **Test plan** — what was tested and how: new tests added, existing tests
  still passing, any manual verification performed.
- **Quality check results** — confirmation that `ruff format --check`,
  `ruff check`, `mypy`, and `pytest` all pass (see
  [Definition of Done](definition-of-done.md)).
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
  [Architecture Governance](claude-workflow.md#architecture-governance)).

## Merge prerequisites

A PR may be merged only once:

- All four required quality commands pass — currently confirmed manually and
  reported in the PR / completion report; automated enforcement via hooks or
  CI is a later phase (see Scope).
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
  [Branch Strategy, Model B](branching.md#model-b-larger-work-package-integration-branch)).

## Branch Protection (conceptual)

No GitHub branch protection settings are configured in this phase (see Scope).
The following is the conceptual target for a later phase, once hooks/CI are
introduced:

- `main` requires a pull request before any change lands — no direct pushes.
- `main` requires the [merge prerequisites](#merge-prerequisites) above to be
  satisfied before the merge option becomes available (review completed,
  checks green once CI exists).
- Force-pushes to `main` — and, once opened, to an `integration/*` branch with
  more than one contributor — are disabled.
- Branch deletion protection is not needed for `main` (never deleted);
  `integration/*`/`feature/*`/`fix/*` branches are deleted routinely per
  [Branch Strategy](branching.md#branch-strategy), which is expected, normal
  behavior, not something to guard against.

## See also

- [Branch Types & Branch Strategy](branching.md)
- [Commit Strategy](commits.md)
- [Definition of Done](definition-of-done.md)
- [Claude Workflow](claude-workflow.md#pull-requests) — Claude's specific PR
  permissions.
