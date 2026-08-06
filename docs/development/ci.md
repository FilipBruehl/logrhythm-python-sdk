# GitHub Actions: CI & Build

This page documents the project's server-side automation: the CI workflow
(`.github/workflows/ci.yml`) and the build workflow
(`.github/workflows/build.yml`). It complements
[Pre-Commit & Local Code Quality Automation](pre-commit.md), which these
workflows largely re-run in a clean, server-side environment on every pull
request and relevant push. No publishing, release, or tag-based workflow is
introduced here — see [Build vs. Publish](#build-vs-publish).

## Purpose

- **`ci.yml`** reproduces the local quality gates (formatting, linting, type
  checking, file hygiene, secret detection, lockfile freshness, workflow
  linting, Markdown linting), Conventional Commit message validation, and the
  test suite, server-side, so a check does not depend on whether a
  contributor's local hooks actually ran.
- **`build.yml`** independently confirms the SDK can be built into
  distributable artifacts (wheel + sdist) and that those artifacts actually
  install and import correctly — without publishing them anywhere.

## Triggers

### `ci.yml`

- `pull_request` targeting `main` or `integration/**`.
- `push` to `main` or `integration/**`.
- `workflow_dispatch` (manual run).

Pushing to a `feature/*` or `fix/*` branch alone does **not** trigger `ci.yml`
— per [Branch Types](branching.md), those branches aren't listed in the
`push.branches` filter. Opening a pull request *from* such a branch *against*
`main` or `integration/**` does trigger it, because `pull_request.branches`
filters on the PR's **target** branch, not its source.

### `build.yml`

- `pull_request` targeting `main` or `integration/**`, but only when a
  packaging- or runtime-relevant path changed.
- `push` to `main` (not `integration/**` — build verification for an
  in-progress integration effort happens through the PRs that feed it,
  per [Branch Strategy, Model B](branching.md#model-b--larger-work-package-integration-branch)).
- `workflow_dispatch`.

Path filter (`paths:`), applied to both `pull_request` and `push`:

```text
src/**
pyproject.toml
uv.lock
README.md
.pre-commit-config.yaml
.github/workflows/build.yml
.github/scripts/verify_package.py
```

A documentation-only change outside these paths (e.g. an edit under
`docs/specifications/`) does not trigger a build. `README.md` is included
because it is embedded as the package's long description
(`readme = "README.md"` in `pyproject.toml`) and is therefore packaging
metadata, not just documentation. `.pre-commit-config.yaml` is included
because `ci.yml`'s quality job — which every packaging-relevant change also
goes through — depends on it; a change there is a signal the build
environment's tooling contract changed. The workflow's own file and the
verification script are included so that editing either re-validates itself.

## Commit-message job

`commit-message` validates every commit a pull request or push actually
introduces against [Commit Strategy](commits.md), using
[`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py),
the project's `conventional-pre-commit` dev dependency, and the shared
[`.github/scripts/commit_types.py`](../../.github/scripts/commit_types.py)
exact-lowercase check — the exact same tool, version, allowed-type list, and
casing rule the local `commit-msg` hooks use (see
[Pre-Commit, Commit-message validation](pre-commit.md#commit-message-validation)
for the full tool behavior, special-case handling, and empirically tested
results this job relies on). It runs in parallel with `quality`, and `test`
now requires both to succeed — see [CI Pipeline](#ci-pipeline-quality--test)
below.

Unlike the other jobs, its checkout uses `fetch-depth: 0` (full history)
rather than `fetch-depth: 1` — resolving an arbitrary `base..head` range
needs history a shallow clone would not have. This is the one, explicitly
scoped exception to this project's otherwise-minimal-checkout policy (see
[Least-Privilege & Permissions](#least-privilege--permissions)); every other
job keeps `fetch-depth: 1`.

## CI commit range

The commit range `commit-message` validates depends on what triggered the
workflow, resolved in a dedicated step before validation runs:

| Trigger | Base | Head |
| --- | --- | --- |
| `pull_request` | `github.event.pull_request.base.sha` | `github.event.pull_request.head.sha` |
| `push` | `github.event.before` | `github.sha` |
| `workflow_dispatch` | *(none)* | `github.sha` |

All four values come from GitHub-controlled SHA fields (never free-text like
a PR title or commit message) and are passed into the range-resolution step
through `env:` rather than interpolated directly into the `run:` script, as
a defense-in-depth practice consistent with
[Least-Privilege & Permissions](#least-privilege--permissions).

[`validate_commits.py`](../../.github/scripts/validate_commits.py) then
applies two documented, non-silent fallbacks rather than guessing at a
range it cannot reliably compute:

- **No base at all** (`workflow_dispatch`), or a **`push` whose `before` is
  git's all-zeros sentinel** (`0000000000000000000000000000000000000000`,
  meaning a new branch/ref's first push has no prior history to diff
  against) — falls back to validating `head` alone. This is always exactly
  one commit, never zero, so it cannot masquerade as an empty range passing
  silently.
- **An explicit `base`/`head` pair that resolves to zero commits** (should
  not normally happen) — treated as a hard failure, not a silent pass, per
  this phase's explicit requirement that an empty or undeterminable range
  must never be reported as successfully validated.

Enumeration itself uses `git rev-list --first-parent --reverse base..head`:
`--first-parent` means a merge commit landing directly on the branch being
validated (for example, a PR merged into `main` via GitHub's "Create a merge
commit" strategy) is still seen and structurally recognized as a merge
commit — see
[Pre-Commit, Commit-message validation](pre-commit.md#commit-message-validation)
— without also re-walking and re-validating every individual commit from
the branch it merged in, which would already have been validated by that
branch's own pull request.

## CI Pipeline: `quality` → `test`

```text
commit-message ─┐
quality         ├──> test
```

- **`commit-message`** runs first (in parallel with `quality`) — see
  [Commit-message job](#commit-message-job) above.
- **`quality`** runs first, on `ubuntu-latest` with Python 3.13. It runs the
  entire pre-commit-stage hook set from
  [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) — Ruff format,
  Ruff check, mypy, gitleaks, the `uv-lock` freshness check, file-hygiene
  hooks, actionlint, and markdownlint-cli2 — via one command:

  ```bash
  uv run pre-commit run --all-files --show-diff-on-failure
  ```

  `pytest` deliberately never runs here: it is pinned to the `pre-push` stage
  in `.pre-commit-config.yaml`, and `pre-commit run` without
  `--hook-stage pre-push` only runs `pre-commit`-stage hooks (see
  [Pre-Commit & Local Code Quality Automation, Hook types](pre-commit.md#hook-types)).
- **`test`** declares `needs: [commit-message, quality]`, so it never starts
  if either job fails, and runs on the same platform/Python version. It installs
  dependencies the same way, then runs:

  ```bash
  uv run pytest --cov-report=xml
  ```

  This produces **both** a terminal coverage report and an XML report:
  `pyproject.toml`'s `[tool.pytest.ini_options]` `addopts` already sets
  `--cov=src/logrhythm_sdk --cov-report=term-missing` for every `pytest`
  invocation (locally and in CI); the workflow appends `--cov-report=xml` on
  top rather than duplicating the whole configuration. No `fail_under`
  threshold, Codecov, Coveralls, or other external coverage service is
  introduced — the long-term coverage target remains documented in
  [Testing](testing.md#coverage-target) and stays informational until real
  runtime implementation exists for it to meaningfully gate.

## Build workflow: `build` (with verification)

Build and verification run as clearly separated steps within one `build`
job, rather than two jobs — this avoids needing `actions/download-artifact`
just to pass files between jobs for a single, fast job:

```text
build
   ↓
verify-package
```

**Build:**

```bash
uv sync --locked
uv build
```

Produces a wheel and a source distribution under `dist/`.

**Verify** (see [`.github/scripts/verify_package.py`](../../.github/scripts/verify_package.py)):

- Both the wheel and the source distribution exist.
- The source distribution contains the package source
  (`src/logrhythm_sdk/__init__.py`).
- The wheel contains `logrhythm_sdk/__init__.py` and `logrhythm_sdk/py.typed`.
- The wheel contains **no** test, cache, or local-settings artifacts
  (`tests/`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.venv`, `.git/`,
  `.claude`, `.coverage`, `__pycache__`, `htmlcov`, `.pre-commit-config.yaml`).
- The wheel's `Requires-Dist` metadata matches `pyproject.toml`'s
  `[project.dependencies]` exactly (name and version constraints, tolerant of
  specifier reordering).
- The wheel installs cleanly into a **fresh, isolated** environment
  (`uv venv .verify-venv` + `uv pip install --python .verify-venv <wheel>` —
  never the job's own project environment).
- `logrhythm_sdk` imports successfully in that isolated environment,
  `__version__` can be read, and it matches both the installed distribution's
  own metadata (`importlib.metadata.version(...)`) and `pyproject.toml`'s
  `[project.version]`.

**Why a small CI-only script instead of inline steps:** ten distinct
structural and metadata assertions — including negative content checks and a
specifier-tolerant metadata comparison — are not reliably or readably
expressible as a handful of inline shell one-liners. The script
(`.github/scripts/verify_package.py`) uses **only the Python standard
library** (`argparse`, `subprocess`, `tarfile`, `tomllib`, `zipfile`,
`pathlib`) — no new runtime or development dependency — and lives under
`.github/scripts/`, not `src/logrhythm_sdk/`: it is CI tooling, never part of
the published SDK.

On success, the verified `dist/*` files are uploaded as the
`distribution-packages` artifact, retained for 7 days. Nothing is published
to any registry.

## Build vs. Publish

**Build is not publishing.** `build.yml` only confirms the package builds and
installs correctly; it has no credentials, no registry access, and no step
that could publish anything, by construction (see
[Permissions](#least-privilege--permissions) and
[Actions & SHA Pinning](#actions--sha-pinning)). Ordinary pull requests and
pushes — including to `main` — can **never** publish a package through this
phase's automation.

Release and publish automation is explicitly deferred to a later phase,
**A.3.7 — Release & Publishing**, which will be implemented before the first
real release. No `publish.yml` exists yet. The eventual publish workflow is
expected to publish only already-verified build artifacts and to be triggered
by release tags and/or a deliberately gated manual release process — these
details are not finalized now, on purpose, so this phase does not
prematurely lock in a design for a problem it isn't solving yet.

## Local equivalents

| CI check | Local equivalent |
| --- | --- |
| `commit-message` job | The `commit-msg` git hook, which runs automatically on every local `git commit` — see [Pre-Commit, Installation](pre-commit.md#installation). To check an already-made commit or range manually: `uv run python .github/scripts/validate_commits.py --head <sha>` (or `--base <sha> --head <sha>` for a range). |
| `quality` job | `uv run pre-commit run --all-files` — see [Pre-Commit, Local quality check](pre-commit.md#local-quality-check). |
| `test` job | `uv run pytest` (add `--cov-report=xml` to also produce the XML report locally). |
| `build` job | `uv build`, then the same verification steps — see [`.github/scripts/verify_package.py`](../../.github/scripts/verify_package.py); can be run manually with `uv venv .verify-venv && uv pip install --python .verify-venv dist/*.whl && uv run python .github/scripts/verify_package.py --installed-python .verify-venv/bin/python` (adjust the interpreter path on Windows: `.verify-venv/Scripts/python.exe`). |
| `actionlint` | Runs automatically as part of `pre-commit run --all-files` (see [actionlint](#actionlint)). |
| `markdownlint-cli2` | Runs automatically as part of `pre-commit run --all-files` (see [Templates, Markdownlint](templates.md#markdownlint)). |

Passing everything locally before pushing means CI is confirming, not
discovering, problems.

## Status check names

GitHub names a status check `<workflow name> / <job name>`. With
`name: CI` in `ci.yml` and jobs named `commit-message`, `quality`, and
`test`, the resulting, stable status check names are:

- `CI / commit-message`
- `CI / quality`
- `CI / test`

`build.yml` (`name: Build`, job `build`) would produce `Build / build`, but
is **not** configured as a universally required status check (see
[Branch Protection](#branch-protection--rulesets-recommendations)), because it
deliberately does not run for non-packaging-relevant changes — a required
check that sometimes never starts would permanently block merging.

## Cache

`astral-sh/setup-uv` is configured with `enable-cache: true`, which caches
uv's own package cache (keyed off `uv.lock`/`pyproject.toml` by default)
across runs — this speeds up `uv sync --locked` without affecting its
correctness or reproducibility guarantees (see
[uv setup and lockfile behavior](#uv-setup-and-lockfile-behavior)).

## Artifacts

`build.yml` uploads the verified `dist/*` (wheel + source distribution) as a
single artifact:

- **Name:** `distribution-packages`
- **Retention:** 7 days
- **Contents:** exactly what `uv build` produced and
  `verify_package.py` already checked — nothing is published to PyPI,
  TestPyPI, or any other registry.

## Concurrency

Both workflows cancel a superseded, still-running execution for the same
workflow and ref/PR:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

`github.workflow` (`CI` vs. `Build`) keeps the two workflows' concurrency
groups from ever colliding with each other, even for the same branch or PR.

## Least-Privilege & Permissions

Both workflows declare, at the workflow level (nothing more permissive at the
job level):

```yaml
permissions:
  contents: read
```

No write scope, and no `pull-requests`, `packages`, `releases`,
`deployments`, or `id-token` permission is granted — no job needs to
write to the repository, comment on a PR, publish a package, create a
release, deploy anywhere, or mint an OIDC token. Checkout uses
`persist-credentials: false` (the checked-out `.git` config never retains a
usable token) and, for every job except `commit-message`, `fetch-depth: 1`
(a shallow clone — no other job needs history; see
[Commit-message job](#commit-message-job) for that one, explicitly scoped
exception). Neither workflow uses `pull_request_target`, and neither uses
any repository secret. The `commit-message` job additionally passes every
GitHub-context SHA value through `env:` rather than interpolating it
directly into a `run:` script — the values themselves are GitHub-controlled
SHAs, not attacker-influenceable free text, but the indirection is a cheap,
standard defense-in-depth practice against the general class of
`${{ }}`-expression injection in `run:` steps.

## Actions & SHA Pinning

Every external action is pinned to a full, immutable commit SHA, with the
corresponding released version in a trailing comment — never a mutable tag
or branch:

| Action | Pinned at | Used for |
| --- | --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` (`v7.0.1`) | Checking out the repository. |
| `astral-sh/setup-uv` | `c771a70e6277c0a99b617c7a806ffedaca235ff9` (`v9.0.0`) | Installing uv and Python 3.13. |
| `actions/upload-artifact` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (`v7.0.1`) | Uploading `distribution-packages` in `build.yml`. |

Only these three, established actions are used — no additional marketplace
action was added. **Updating a pin** is a deliberate step: resolve the new
release's commit SHA (e.g.
`git ls-remote --tags https://github.com/<org>/<repo> <new-tag>`, or the
GitHub UI's "Copy SHA" on the release tag), update both the SHA and the
version comment together, then re-run
[actionlint](#actionlint) and a manual workflow dispatch to confirm nothing
broke — the same discipline as any other dependency upgrade (see
[Dependencies & Tooling, Dependency upgrades](dependencies.md#dependency-upgrades)).

## uv setup and lockfile behavior

**Decision: CI uses `uv sync --locked`** (not the originally proposed
`uv sync --locked --dev`) — verified against the installed uv version
(`uv sync --help`): `--dev` is not a valid flag. The development dependency
group is already included by default in `uv sync` (no `[tool.uv]
default-groups` override exists in `pyproject.toml`, so uv's built-in default
— include the `dev` group — applies), exactly as every `uv sync` throughout
this project's local workflow has always relied on. `--locked` (not
`--frozen`) is used because it actively **asserts the lockfile would not
change** — it fails the moment `pyproject.toml` and `uv.lock` disagree,
rather than silently using a possibly-stale lock. Concretely, this guarantees
every job in both workflows:

- never modifies `uv.lock`,
- fails immediately if `pyproject.toml` and `uv.lock` have drifted apart, and
- never performs a new dependency resolution during CI — only installs
  exactly what `uv.lock` already pins.

`astral-sh/setup-uv`'s `python-version: "3.13"` input sets `UV_PYTHON`, so
`uv sync`/`uv run` use that interpreter without a separate
`actions/setup-python` step.

## actionlint

[actionlint](https://github.com/rhysd/actionlint) validates GitHub Actions
workflow syntax, expressions, and (where `shellcheck` is available) the
`run:` steps' shell scripts. It is configured as the established
`actionlint` pre-commit hook — not a custom syntax checker — in
[`.pre-commit-config.yaml`](../../.pre-commit-config.yaml):

```yaml
- repo: https://github.com/rhysd/actionlint
  rev: v1.7.12
  hooks:
    - id: actionlint
      stages: [pre-commit]
```

Its built-in file filter (`files: ^\.github/workflows/`) means it
automatically covers every file under `.github/workflows/` — currently
`ci.yml` and `build.yml` — without listing them individually. It runs:

- **Locally**, as part of `uv run pre-commit run --all-files` (or targeted:
  `uv run pre-commit run actionlint`).
- **In CI**, inside the `quality` job's single
  `pre-commit run --all-files` invocation — no separate CI step or bespoke
  workflow-syntax check was written for this.

No ADR was needed for this addition (it is tooling configuration, not an
architectural decision — see
[ADR Policy](../adr/README.md#when-an-adr-is-not-required)).

## Troubleshooting

- **`quality` fails on a hook that also fixes files** (Ruff format,
  end-of-file-fixer, etc.). The CI log shows the diff
  (`--show-diff-on-failure`); apply the same fix locally
  (`uv run pre-commit run --all-files`), commit, and push again — see
  [Pre-Commit, Troubleshooting](pre-commit.md#troubleshooting).
- **`quality` fails on `uv-lock`.** `pyproject.toml` and `uv.lock` have
  drifted apart. Run `uv lock` locally, commit the regenerated `uv.lock`,
  and push again.
- **`test` never starts.** Check the `quality` job first — `needs: quality`
  means `test` is skipped, not failed, when `quality` fails.
- **`build` doesn't run on my PR.** Check whether your change actually
  touched a path in the [path filter](#triggers) — a documentation-only
  change is expected not to trigger it. Use `workflow_dispatch` to run it
  manually if you need to confirm packaging anyway.
- **`build` fails in "Verify package".** Read the `FAIL:` line from
  `verify_package.py`'s output — it names exactly which check failed (missing
  file, forbidden path in the wheel, metadata mismatch, or an isolated-install
  failure) and reproduces the same way locally (see
  [Local equivalents](#local-equivalents)).
- **A workflow fails only in CI, not locally.** Confirm you're on Python
  3.13 and used `uv sync --locked` (not a plain `uv sync`, which would
  silently update the lock instead of failing on drift) — see
  [uv setup and lockfile behavior](#uv-setup-and-lockfile-behavior).

## Branch Protection / Rulesets recommendations

Branch protection is **not** configured through the GitHub API or UI as part
of this phase — the rules below are to be applied manually.

### `main`

- Require a pull request before merging (no direct pushes).
- Block force pushes.
- Block branch deletion.
- Require status checks to pass before merging:
  - `CI / commit-message`
  - `CI / quality`
  - `CI / test`
- Require the branch to be up to date with `main` before merging.
- Require conversation resolution before merging.
- Do **not** require a second approval yet, given the current one-person
  contributor constellation (revisit once that changes).
- Do not use the administrator bypass as a routine path around these rules —
  it exists for genuine emergencies, not convenience.

### `integration/**`

If the GitHub plan in use supports rulesets with branch **patterns** (not
just single branch names — this is a plan-dependent capability, not
guaranteed on every GitHub tier):

- Require a pull request before merging (covers `feature/*`/`fix/*` branches
  merging into the integration branch, per
  [Branch Strategy, Model B](branching.md#model-b--larger-work-package-integration-branch)).
- Require the same status checks: `CI / commit-message`, `CI / quality`,
  `CI / test`.
- Block direct pushes and force pushes.
- No approval requirement (consistent with `main`'s current one-person
  constellation).

`feature/*` and `fix/*` branches themselves are **not** protected — they are
short-lived and deleted routinely per [Branch Strategy](branching.md), which
is expected, normal behavior for them, not something to guard against.

All of the above is applied by hand in the repository's GitHub settings
(Settings → Branches / Rules); no automation configures it, per this phase's
scope.

## What this phase deliberately does not include

Per Scope: publishing to PyPI/TestPyPI, GitHub Releases, tag-based
publishing, Trusted Publishing, an enforced coverage gate or external
coverage service (Codecov/Coveralls), Dependabot/Renovate, and a merge
queue. (Commit-message linting, the `commit-msg` hook, Markdown linting, and
PR/issue templates were out of scope when this page was first written, but
have since been added — see [Commit-message job](#commit-message-job) /
[Pre-Commit](pre-commit.md#commit-message-validation) and
[Templates](templates.md), respectively.) See
[Build vs. Publish](#build-vs-publish) above for where publishing
is planned (A.3.7).

## See also

- [Pre-Commit & Local Code Quality Automation](pre-commit.md)
- [Dependencies & Tooling](dependencies.md)
- [Pull Requests](pull-requests.md)
- [Definition of Done](definition-of-done.md)
- [Branch Types & Branch Strategy](branching.md)
