# Commit Strategy

This page defines the project's binding commit conventions: message format,
allowed types, scopes, commit size/content rules, and how history is kept
linear across merges. Message format, allowed types, and exact type casing
are mechanically enforced, both locally (two `commit-msg` git hooks) and
server-side (a CI job) — see
[Pre-Commit, Commit-message validation](pre-commit.md#commit-message-validation)
for the tooling, its exact tested behavior, and its known limitations.

## Conventional Commits

Every commit message follows [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <description>
```

- **type** — required, lowercase, one of [Allowed commit types](#allowed-commit-types).
- **scope** — optional but recommended; lowercase; names the affected component
  (see [Recommended scopes](#recommended-scopes)).
- **description** — imperative, present tense ("add", not "added"/"adds"), no
  trailing period, concise enough to stand alone in a one-line log.
- A longer **body** explains *why* when the reason isn't obvious from the diff
  (e.g. a link to the SPEC or ADR the change implements), consistent with
  [SPEC-000](../specifications/design-principles.md#implementation-principles)'s
  "Explicit over implicit" principle.

## Allowed commit types

| Type | Use for |
| --- | --- |
| `feat` | A new capability — a new resource, endpoint, model, or SPEC-driven feature. |
| `fix` | A bug fix. Pairs naturally with a `fix/*` branch (see [Branch Types](branching.md#fix)). |
| `docs` | A documentation-only change — this is how the excluded `docs/*` branch category is actually represented (see [Branch Types](branching.md#not-part-of-the-official-workflow)). |
| `refactor` | Internal restructuring with no behavior change — this is how the excluded `refactor/*` branch category is actually represented. |
| `test` | Adding or correcting tests only, with no production-code behavior change. |
| `chore` | Tooling, dependency bookkeeping, repository maintenance, and release bookkeeping. |
| `perf` | A performance improvement without a behavior change. |
| `style` | A formatting-only change (whitespace, import order) with no logic change. |
| `build` | Build system, packaging, toolchain, or dependency management — see [`build` vs. `ci`](#build-vs-ci) below. |
| `ci` | Continuous integration configuration — see [`build` vs. `ci`](#build-vs-ci) below. |
| `revert` | Reverts a previous commit. |

### `build` vs. `ci`

These two are easy to confuse and are kept deliberately distinct:

- **`build`** covers the build system, packaging, toolchain, and dependency
  management: `pyproject.toml`, `uv.lock`, dependency version bumps,
  `pre-commit` itself (the tool and its hook definitions in
  `.pre-commit-config.yaml`), and other local development tooling. In short:
  what a contributor installs and runs on their own machine to build the
  project or work on it.
- **`ci`** covers GitHub Actions and everything that runs the project's
  automation on GitHub's infrastructure rather than locally: workflow files
  under `.github/workflows/`, CI/CD pipeline configuration, build- and
  test-workflow definitions, pipeline automation, and branch-protection-adjacent
  infrastructure (status check names, required workflows) — see
  [GitHub Actions: CI & Build](ci.md). In short: what runs a check or builds
  something *for* the project, on a server, not what a contributor runs
  locally.

A change to `.pre-commit-config.yaml` itself is `build` (it configures local
tooling); a change to `.github/workflows/ci.yml` or `.github/workflows/build.yml`
is `ci` (it configures server-side automation) — even though the `ci.yml`
workflow's `quality` job happens to invoke that same local tooling
server-side. The commit changes the workflow, not the tooling, so it is `ci`.

### Example

```text
ci(github): introduce quality and package build workflows
```

## Recommended scopes

Scope names the most specific affected component:

- **Shared infrastructure** (per [SPEC-000](../specifications/design-principles.md)):
  `core`, `transport`, `config`, `auth`, `tls`, `logging`, `exceptions`,
  `models`, `filters`.
- **API modules** (once implemented, per
  [SPEC-010, Supported APIs](../specifications/api-modules.md#supported-apis)):
  `admin`, `drilldown`, `metrics`, `aie`, `alarms`, `cases`, `search`.
- **Documentation / governance**: `spec`, `adr`, `docs`, `workflow`.
- **Repository / tooling**: `deps`, `tooling`, `ci`.

When a change genuinely spans multiple components with no single dominant one,
omit the scope rather than picking an arbitrary one.

## Commit rules

- One logical change per commit.
- Imperative mood in the description.
- The body states *why*, not a restatement of *what* the diff already shows.
- No unrelated files or concerns bundled into one commit (see
  [`AGENTS.md`](../../AGENTS.md#working-agreements)).
- No secrets, ever, in a commit message or diff.
- The commit type accurately reflects the nature of the change — a refactor is
  never labeled `fix`, a new feature is never labeled `chore`, and so on.

## Commit size

- Small, atomic, and independently reviewable.
- A large or multi-part work package is split into a logically ordered sequence
  of commits rather than committed as one large change — consistent with
  [API Implementation Workflow](api-implementation-workflow.md)'s existing "prefer
  one focused commit… over one large, hard-to-review change."
- Each commit should, as a goal, leave the repository in a state that would pass
  the required quality commands. Local hooks and CI enforce these checks at
  commit/push and pull-request boundaries; keeping each individual commit
  healthy also preserves a bisectable history.

## Commit content

- Tests that verify a piece of behavior belong in the same commit as that
  behavior, not a separate "add tests" commit tacked on afterward — unless the
  work is explicitly test-only (`test:`).
- A documentation update required by a code change belongs in the same commit
  (or the same PR, for a larger work package), not deferred to a later, separate
  commit.
- Once runtime code exists, a commit does not mix unrelated SPEC/documentation
  changes with unrelated runtime code changes.

## Binding decision: linear history, no default squash-merge

**Decision: the binding rule is the result, not a specific technique — history
stays linear, and every commit is preserved. Squash-merge must not be used as
this project's default merge strategy** — squashing a branch into one commit
discards the reviewable, atomic commit history [Commit size](#commit-size) and
[Commit content](#commit-content) above are written to produce.

Instead:

- **Rebase and Merge** (or an equivalent fast-forward-preserving strategy) is
  the project's **preferred, default technique** for a `feature/*`/`fix/*`
  branch to reach its target (`main` or an `integration/*` branch), per
  [Branch Strategy](branching.md#branch-strategy). It is not the only
  technique that satisfies the binding rule above — any equivalent procedure
  that preserves individual commits and results in a linear history on the
  target branch is equally acceptable; Rebase and Merge is simply the
  project's default choice among them.
- Before merge, the source branch is typically rebased onto its target so the
  merge lands as a fast-forward (or as close to one as the hosting platform
  allows), keeping `main`'s history linear instead of an interleaved graph of
  merge commits.
- Squash-merge is only ever a deliberate, explicit exception — for example, a
  branch whose intermediate commits are genuinely not worth preserving (a
  string of "fix typo" commits against the same PR) — never the default choice,
  and never for an `integration/*` branch, whose entire purpose is to preserve
  the reviewable structure of the resources merged into it.
- Actually configuring the GitHub merge-button settings to enforce this is a
  Branch Protection concern — see
  [Pull Requests, Branch Protection](pull-requests.md#branch-protection)
  — and remains a manual repository-administration step.

## Mapping the excluded branch categories

[Branch Types](branching.md#not-part-of-the-official-workflow) lists branch
prefixes this project does not use (`develop`, `release/*`, `hotfix/*`,
`experiment/*`, `prototype/*`, `docs/*`, `refactor/*`) because these categories
of change are represented through commit types and existing branch types
instead:

| Excluded category | How it's actually handled |
| --- | --- |
| `docs/*` | A `docs:` commit on an ordinary `feature/*` branch (or `integration/developer-infrastructure` for a larger documentation effort). |
| `refactor/*` | A `refactor:` commit on an ordinary `feature/*` branch. |
| `hotfix/*` | A `fix/*` branch created from `main` — no separate hotfix concept, since `main` is always releasable (see [Branch Types](branching.md#main)). |
| `release/*` | Not needed: `main` is always releasable; a release is a tag on `main`, accompanied by a `chore:` commit (e.g. changelog update) where one is needed, not a branch. |
| `develop` | Not needed: this project has no long-lived integration-of-everything branch — `main` plus short-lived `feature/*`/`fix/*`/`integration/*` branches serve that role (see [Branch Strategy](branching.md#branch-strategy)). |
| `experiment/*`, `prototype/*` | Not tracked as an official project branch. Exploratory work stays local and unpushed until a decision is made to keep it; if kept, it is rebuilt as a proper `feature/*` branch with a clean, Conventional-Commits history before it is ever opened as a PR. |

## See also

- [Branch Types & Branch Strategy](branching.md)
- [Pull Requests](pull-requests.md)
- [Definition of Done](definition-of-done.md) — commit-strategy compliance is
  part of "done."
- [GitHub Actions: CI & Build](ci.md) — the `CI / commit-message` status
  check.
- [Pre-Commit, Commit-message validation](pre-commit.md#commit-message-validation) —
  the local `commit-msg` hooks and their server-side counterpart.
