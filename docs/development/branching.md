# Branch Types & Branch Strategy

This page defines the project's binding branch workflow: which branch types
exist, and how they are created, updated, merged, and removed. It applies to
every contributor, human or AI-assisted, per [CLAUDE.md](../../CLAUDE.md) and
[Claude Workflow](claude-workflow.md).

## Branch Types

Exactly four branch types are officially supported.

### `main`

- Always stable and releasable.
- No direct development on `main`, ever.
- Changed exclusively through pull requests — see [Pull Requests](pull-requests.md).

### `integration/*`

For larger, coherent work packages that span multiple resources or areas.
Examples:

```text
integration/admin-api
integration/alarm-api
integration/search-api
integration/developer-infrastructure
```

Properties:

- Created from `main`.
- Collects multiple `feature/*` (and, where needed, `fix/*`) branches.
- Merged into `main` as a single, combined pull request once its planned scope
  is complete.
- May exist for an extended period while its feature branches land one by one —
  unlike `feature/*` and `fix/*`, an `integration/*` branch is not expected to
  be short-lived.

### `feature/*`

Ordinary development branches. Examples:

```text
feature/admin-hosts
feature/admin-users
feature/search-query-builder
feature/transport-timeouts
```

Properties:

- Created from `main` **or** from an `integration/*` branch.
- Contains exactly one logically complete work package — not a bundle of
  unrelated changes (see [CLAUDE.md](../../CLAUDE.md), "Change discipline").
- Deleted immediately after a successful merge.

### `fix/*`

Bug fixes. Examples:

```text
fix/request-id
fix/config-validation
fix/search-timeout
```

Properties:

- Normally created from `main`.
- During an integration effort, also created from the relevant `integration/*`
  branch.
- Short-lived: created, fixed, reviewed, merged, deleted — no extended
  development on a `fix/*` branch.

### Not part of the official workflow

The following branch prefixes are **not** used in this project:

- `develop`
- `release/*`
- `hotfix/*`
- `experiment/*`
- `prototype/*`
- `docs/*`
- `refactor/*`

These categories of change exist, but are expressed through **commit types**
instead of dedicated branch prefixes — see [Commit Strategy](commits.md). A
documentation-only change, for example, is a `docs:` commit on an ordinary
`feature/*` (or, for a larger documentation effort, `integration/*`) branch, not
a `docs/*` branch; a refactor is a `refactor:` commit, not a `refactor/*`
branch; and so on. There is no separate release branch because `main` is always
releasable, and no separate hotfix branch because a production fix is simply a
`fix/*` branch created from `main`.

## Branch Strategy

Two official work-package models exist. Which one applies is decided by the
size of the work package, not by preference, and **no deeper branch hierarchy
is supported** beyond what these two models show — an `integration/*` branch
never itself branches into another `integration/*` branch, and a `feature/*` or
`fix/*` branch never gets its own child branches.

### Model A — small work package

```text
main
└── feature/<topic>
```

A single, self-contained change (one resource, one document, one fix) that can
be reviewed and merged as one unit.

- **Creation:** `feature/<topic>` (or `fix/<topic>` for a bug fix) is created
  directly from the current tip of `main`.
- **Update:** if `main` moves ahead while the branch is open, the branch is
  rebased onto `main` — never merged from `main` — to keep the eventual history
  linear (see [Commit Strategy](commits.md)).
- **Merge:** a single pull request from the branch directly into `main` — see
  [Pull Requests](pull-requests.md).
- **Lifecycle:** created → developed → reviewed → merged into `main` → deleted.
- **Deletion:** the branch is deleted immediately once its PR is merged. No
  merged branch is kept around "just in case."

### Model B — larger work package (integration branch)

```text
main
└── integration/<area>
    ├── feature/<resource-1>
    ├── feature/<resource-2>
    ├── feature/<resource-3>
    └── ...
```

- **Creation:**
  - `integration/<area>` is created from the current tip of `main`.
  - Each `feature/<resource-N>` (or `fix/<topic>`, for a fix discovered during
    the integration effort) is created from `integration/<area>` — **never**
    from `main` directly, and never from another `feature/*`/`fix/*` branch.
- **Update:**
  - Each `feature/*`/`fix/*` branch under the integration branch is rebased
    onto `integration/<area>` as that branch moves ahead, to stay current.
  - `integration/<area>` itself is rebased onto `main` if `main` moves ahead
    while the integration effort is in progress.
- **Merge order:**
  1. Each `feature/*`/`fix/*` branch is merged into `integration/<area>` first,
     one at a time, as it is completed and reviewed. The order between
     resources follows their logical/dependency order where one exists;
     otherwise completion order.
  2. Only after the planned set of resources for that `integration/<area>` has
     been merged into it — and the integration branch as a whole passes the
     required quality checks — does `integration/<area>` go through **one**
     pull request into `main`.
  3. A `feature/*`/`fix/*` branch created under an `integration/*` branch is
     never merged directly into `main`; it always reaches `main` through that
     integration branch.
- **Lifecycle:**
  - `feature/*` / `fix/*`: created → developed → reviewed → merged into
    `integration/<area>` → deleted.
  - `integration/<area>`: created → receives its feature/fix branches →
    reviewed as a whole → merged into `main` → deleted.
- **Deletion:**
  - Each `feature/*`/`fix/*` branch is deleted immediately once merged into
    `integration/<area>`.
  - `integration/<area>` is deleted immediately once its PR into `main` is
    merged.
  - No integration, feature, or fix branch outlives its own merge.

### Origin and destination at a glance

| Branch | Entsteht von | Merge nach |
| --- | --- | --- |
| `main` | – | – |
| `integration/*` | `main` | `main` |
| `feature/*` | `main` oder `integration/*` | Ursprungsbranch |
| `fix/*` | `main` oder `integration/*` | Ursprungsbranch |

"Ursprungsbranch" means whichever branch the `feature/*`/`fix/*` branch was
created from: `main` if it was created directly from `main` (Model A), or the
relevant `integration/*` branch if it was created under an integration effort
(Model B).

### Choosing a model

Use Model A unless the work package genuinely needs independent review of its
parts before they should land together — needing multiple, separately
reviewable resources merged as one coherent increment is the only reason to
open an `integration/*` branch. When in doubt, prefer Model A; an oversized
"small" change is a sign the work package should be split into smaller PRs, not
a reason to reach for an integration branch.

## See also

- [Commit Strategy](commits.md) — how history stays linear across these merges,
  and how change categories not covered by a branch prefix (docs, refactors,
  experiments) are expressed instead.
- [Pull Requests](pull-requests.md) — what a PR into `main` (or into an
  integration branch) requires.
- [Claude Workflow](claude-workflow.md) — which branch operations Claude may
  perform, and under what conditions.
- [Git Safety Rules](claude-workflow.md#git-safety-rules) — forbidden
  operations, including branch deletion outside the lifecycle described here.
