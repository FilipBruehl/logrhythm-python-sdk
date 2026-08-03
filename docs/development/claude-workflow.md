# Claude Workflow & Architecture Governance

This page documents how Claude Code operates within this repository's
workflow: which architecture decisions Claude may never make on its own, and
which git operations it may and may not perform, and under what conditions.
[CLAUDE.md](../../CLAUDE.md) carries the short, always-loaded summary of these
rules; this page is the full elaboration of *why* and *what*. The technical
configuration that mechanically enforces these rules — `.claude/settings.json`'s
permission model, and Conventional Commit message validation — is documented
separately in [Claude Code: Technical Settings](claude-code.md), so this page
does not repeat *how* it is configured.

## Architecture Governance

**Claude does not make architecture decisions.**

This project's architecture is governed by
[SPEC-000 through SPEC-010](../specifications/README.md) and by the
[Architecture Decision Records](../adr/README.md). Both are deliberate,
reviewed artifacts — not something an implementation task quietly reinterprets
along the way.

If, during implementation, a task turns out to touch any of the following, and
the existing documentation does not already give a clear, binding answer,
**work stops and an explicit decision is obtained from the user before
proceeding**:

- a **SPEC** (its scope, decisions, or Open Questions),
- an **ADR** (an existing decision, or whether a new one is needed — see
  [ADR Policy](../adr/README.md#when-an-adr-is-required)),
- a **Public API** shape or compatibility contract,
- **Security Defaults** (TLS verification, secret handling, redaction,
  authentication),
- **Ownership** of a component (who creates/holds/releases it), or
- **Lifecycle** of a component (creation, closing, reuse rules).

This is distinct from ordinary implementation judgment (choosing an internal
helper's name, how a loop is written, which private function does what) —
those remain a normal part of doing the work. The stop-and-ask rule applies
specifically to decisions that would be architecturally significant under
[SPEC-000](../specifications/design-principles.md) or the
[ADR criteria](../adr/README.md#when-an-adr-is-required).

Stopping means: report what was found, why it's a decision rather than an
implementation detail, and the options as understood — not silently picking
the option that seems most reasonable and continuing.

## Claude Workflow

### Branches

Claude may:

- create an explicitly named `feature/*` branch, once its name has been given
  or confirmed by the user, per [Branch Types](branching.md#feature),
- create an explicitly named `integration/*` branch, once its name has been
  given or confirmed by the user, per
  [Branch Types](branching.md#integration),
- switch to either, and
- check their status (`git status`, `git branch`, `git log`, and similar
  read-only inspection).

Claude does **not** independently plan or create any additional branch
structure — no speculative `feature/*` branches for future work, no
`fix/*` branch opened without being asked, and no branching strategy decided
on Claude's own initiative beyond what
[Branch Types & Branch Strategy](branching.md) already documents.

### Commits

Claude:

- commits only after **explicit approval** from the user for that specific
  commit,
- commits only after all four required quality commands have passed (see
  [Definition of Done](definition-of-done.md#quality-checks)), and
- never creates a WIP or placeholder commit.

This does not change the existing, broader rule already in
[CLAUDE.md](../../CLAUDE.md): a commit is never created without an explicit
instruction to do so, even after changes are made and verified.

### Push

Claude:

- pushes only on **explicit instruction**,
- never pushes directly to `main`, and
- never force-pushes, under any circumstance (see
  [Git Safety Rules](#git-safety-rules)).

### Pull Requests

Claude may:

- prepare/draft a PR description, following
  [Pull Requests, Required PR content](pull-requests.md#required-pr-content), and
- create the actual PR — but only on **explicit instruction**.

Claude never:

- merges a PR itself,
- changes branch protection settings, or
- triggers a release.

## Git Safety Rules

### Forbidden operations

The following are never performed without the user's explicit, scoped
approval for that exact operation — never as a default or convenience action:

- `git reset --hard`
- `git clean` (any destructive variant)
- force push, including `--force` and `--force-with-lease`
- `git commit --amend` — a new commit is created instead, per
  [CLAUDE.md](../../CLAUDE.md)'s existing git-safety protocol
- branch deletion — including a branch whose merge lifecycle would otherwise
  call for it per [Branch Strategy](branching.md#branch-strategy); deletion is
  still confirmed explicitly, not assumed automatic
- `git rebase`, interactive or non-interactive, without prior approval —
  rebase is central to
  [Commit Strategy](commits.md#binding-decision-linear-history-no-default-squash-merge)'s
  linear-history workflow, but rewriting history is never done silently

### Handling existing state

- Before any command that could discard uncommitted work (`checkout`,
  `restore`, `reset`, `clean`, or similar), `git status` is run first.
- Existing, uncommitted user changes are never discarded, stashed-and-forgotten,
  or overwritten without asking. A non-destructive alternative (stash, a new
  branch) is preferred, and the user is asked before proceeding whenever
  there's doubt about whether in-progress work would be affected.

### Staging, status, and diff

- `git add` stages only the specific files relevant to the approved change —
  `git add -A` / `git add .` are avoided, to prevent accidentally staging
  unrelated or sensitive files.
- `git status` and `git diff` (both staged and unstaged) are reviewed before
  every commit, to confirm scope and catch accidental inclusion of secrets or
  unrelated files, per [Definition of Done, Change hygiene](definition-of-done.md#change-hygiene).

## See also

- [CLAUDE.md](../../CLAUDE.md) — the always-loaded summary of these rules.
- [Claude Code: Technical Settings](claude-code.md) — the technical
  permission model and commit message validation that mechanically enforce
  the rules on this page.
- [Branch Types & Branch Strategy](branching.md)
- [Commit Strategy](commits.md)
- [Pull Requests](pull-requests.md)
- [ADR Policy](../adr/README.md#when-an-adr-is-required)
