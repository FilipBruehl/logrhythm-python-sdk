# Pre-Commit & Local Code Quality Automation

This page documents the project's local code-quality automation: the
[pre-commit](https://pre-commit.com/) framework, the hooks it runs at commit
and push time, and the official local quality check for running those same
checks on demand, outside of a commit. It complements
[Contributing](contributing.md) (local setup) and
[Definition of Done](definition-of-done.md) (the checklist this automation
partially enforces). This page is local-only; the same hooks now also run
server-side on every pull request and relevant push — see
[GitHub Actions: CI & Build](ci.md).

## Installation

### Chosen approach: a pinned dev dependency, not a global tool

The official pre-commit documentation suggests installing the `pre-commit` CLI
globally (for example via `uv tool install pre-commit`, `pipx`, or `brew`).
This project instead adds `pre-commit` to `pyproject.toml`'s
`[dependency-groups.dev]`, alongside Ruff, mypy, pytest, and pytest-cov (see
[Dependencies & Tooling](dependencies.md#dependency-placement)).

**Why:** a global `uv tool install` is not pinned by `uv.lock` — its exact
version can silently drift between contributors' machines (and Claude's
environment) over time. Adding `pre-commit` as a dev dependency instead means
`uv sync` installs the *exact same, lock-file-pinned* version for everyone,
consistent with this project's existing dependency-group convention and its
"reproducible technical basis" goal (see
[Dependencies & Tooling](dependencies.md)). The trade-off is one extra
character in every invocation (`uv run pre-commit ...` instead of bare
`pre-commit ...`), which this project accepts.

### First-time setup

```powershell
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
uv run pre-commit install --hook-type commit-msg
```

- `uv sync` installs `pre-commit` (and every other dev/runtime dependency) into
  the project's `.venv`, pinned exactly as recorded in `uv.lock`.
- `uv run pre-commit install` writes the commit-time git hook to
  `.git/hooks/pre-commit`.
- `uv run pre-commit install --hook-type pre-push` writes the push-time git
  hook to `.git/hooks/pre-push`. This is a **separate, explicit step** — it is
  not installed automatically by the first command, by design (see
  [Pre-Push Hook](#pre-push-hook)).
- `uv run pre-commit install --hook-type commit-msg` writes the
  message-validation git hook to `.git/hooks/commit-msg`. Also a **separate,
  explicit step**, for the same reason as `pre-push` above — see
  [Commit-Msg Hook](#commit-msg-hook).

**Existing clones** created before this hook type existed only need to run
the one new command above (`uv run pre-commit install --hook-type
commit-msg`) — the other two hook types are already installed and are
unaffected.

Both generated hook scripts invoke the project's own `.venv` interpreter
directly, so they work correctly even in a shell where the virtual environment
has not been separately activated.

### Updating

- **Updating the `pre-commit` tool itself** follows the normal dependency
  upgrade process — see
  [Dependencies & Tooling, Dependency upgrades](dependencies.md#dependency-upgrades):
  bump the version range in `pyproject.toml`, run `uv sync`, run the quality
  commands.
- **Updating the hook versions** pinned in `.pre-commit-config.yaml` (the
  `rev:` field for each repo) is done with:

  ```powershell
  uv run pre-commit autoupdate
  ```

  This rewrites each `rev:` to the latest tag of that hook repository. Review
  the diff, then run `uv run pre-commit run --all-files` to confirm nothing
  broke before committing the updated config — this is itself a dependency-like
  change and follows the same discipline as any other tooling upgrade.

## Hook types

Two independent git hook types are configured, each running only the hooks
explicitly assigned to its stage in `.pre-commit-config.yaml` (every hook
declares its `stages:` explicitly — nothing relies on an implicit default).

### Pre-Commit Hook

Runs on every `git commit`, via `.git/hooks/pre-commit`. Configured hooks:

| Hook | Source | Purpose |
| --- | --- | --- |
| `ruff-format` | `astral-sh/ruff-pre-commit` | Formatting, matching `ruff format --check .`. Auto-fixes and blocks the commit if it had to change something (see [Troubleshooting](#troubleshooting)). |
| `ruff-check` | `astral-sh/ruff-pre-commit` | Linting, matching `ruff check .`. |
| `trailing-whitespace` | `pre-commit/pre-commit-hooks` | Removes trailing whitespace. |
| `end-of-file-fixer` | `pre-commit/pre-commit-hooks` | Ensures files end with exactly one newline. |
| `mixed-line-ending` | `pre-commit/pre-commit-hooks` | Flags/fixes inconsistent line endings. |
| `check-merge-conflict` | `pre-commit/pre-commit-hooks` | Blocks committing unresolved conflict markers. |
| `check-added-large-files` | `pre-commit/pre-commit-hooks` | Blocks accidentally committing large files (default threshold). |
| `check-yaml` | `pre-commit/pre-commit-hooks` | Validates YAML syntax. |
| `check-toml` | `pre-commit/pre-commit-hooks` | Validates TOML syntax (e.g. `pyproject.toml`). |
| `debug-statements` | `pre-commit/pre-commit-hooks` | Blocks committing stray Python debugger/breakpoint statements. |
| `gitleaks` | `gitleaks/gitleaks` | Secret detection — see [Secret Detection](#secret-detection). |
| `uv-lock` | `astral-sh/uv-pre-commit` | Keeps `uv.lock` from being committed out of date — see [uv Integration](#uv-integration). |
| `actionlint` | `rhysd/actionlint` | Validates GitHub Actions workflow files under `.github/workflows/` — see [GitHub Actions: CI & Build](ci.md#actionlint). |
| `markdownlint-cli2` | `DavidAnson/markdownlint-cli2` | Markdown style/consistency checking, check-only — see [Templates, Markdownlint](templates.md#markdownlint). |
| `mypy` (local) | this repo | Static type checking, matching `mypy src/logrhythm_sdk`. |

A separate, `manual`-stage-only `markdownlint-cli2` hook applies `--fix`; it
never runs as part of a git hook — see
[Templates, Manual full-repository lint](templates.md#manual-full-repository-lint).

### Pre-Push Hook

Runs on `git push`, via `.git/hooks/pre-push`, and runs **only**:

| Hook | Source | Purpose |
| --- | --- | --- |
| `pytest` (local) | this repo | The full test suite, matching `uv run pytest`. |

This is deliberately the only push-time check. The full test suite is slower
than the commit-time hooks, so it runs once per push rather than once per
commit, while still guaranteeing nothing untested reaches a remote.

### Commit-Msg Hook

Runs on `git commit`, via `.git/hooks/commit-msg`, and runs **only**:

| Hook | Source | Purpose |
| --- | --- | --- |
| `commit-type-lowercase` (local) | this repo, via `.github/scripts/commit_types.py` | Exact-lowercase commit-type check — a gap `conventional-pre-commit` itself leaves open, see [Claude Code, `commit_types.py`](claude-code.md#commit_typespy-the-shared-lowercase-check). |
| `conventional-pre-commit` (local) | this repo, via the `conventional-pre-commit` dev dependency | Conventional Commit message validation — see [Claude Code, Commit message validation](claude-code.md#commit-message-validation). |

This is a separate git hook type from the commit-time
[Pre-Commit Hook](#pre-commit-hook) above (which validates file *content*):
`commit-msg` runs once, against the drafted commit *message*, after the
pre-commit-stage hooks have already passed. `conventional-pre-commit` is not
run with `--strict` — see
[Claude Code, Why no `--strict` locally](claude-code.md#why-no---strict-locally)
for why, and for both hooks' exact, empirically tested behavior around
casing, merge, revert, and `fixup!`/`squash!` commits.

### Secret Detection

[gitleaks](https://github.com/gitleaks/gitleaks) runs at commit time using its
**established default configuration** — no project-specific rules, and no
exceptions/allowlist entries. If gitleaks ever reports a genuine false
positive, adding an exception is itself a deliberate decision (not a routine
one) and should be discussed rather than silently added, consistent with
[Architecture Governance](claude-workflow.md#architecture-governance)'s
general stance on quietly working around a safeguard. No GitHub-side secret
scanning integration is configured — this is local-only, per this phase's
scope.

### uv Integration

The official [`astral-sh/uv-pre-commit`](https://github.com/astral-sh/uv-pre-commit)
hook provides `uv-lock`, which runs `uv lock` and fails the commit if doing so
changes `uv.lock` — exactly the official, documented pattern for this exact
goal ("make sure your `uv.lock` file is up to date even if your `pyproject.toml`
file was changed"). No custom script was written for this; the hook is used
exactly as published.

## Local quality check

**The project's official, complete local quality check is:**

```bash
uv run pre-commit run --all-files
```

This runs every pre-commit-stage hook — `ruff-format`, `ruff-check`, `mypy`,
plus the file-hygiene and secret-detection hooks — across the whole
repository, deliberately **without** `pytest` (which lives exclusively in the
[Pre-Push Hook](#pre-push-hook)). Nothing else needs to be run manually to get
the same result the commit-time hooks would produce.

**Why this, and not a separate named command:** uv has no built-in task
runner and does not support an arbitrary project-level command like
`uv run check`; a `[project.scripts]` entry would be the wrong tool, since
that ships an entry point as part of the published SDK, not as
developer-only tooling; and a bespoke orchestration script would be exactly
the kind of extra, hand-maintained machinery this project avoids when an
existing, officially maintained mechanism already does the job.
`pre-commit run --all-files` already exists once pre-commit is installed (see
[Installation](#installation)) and exactly matches the requirement, so it is
used directly rather than wrapped in a second, redundant command.

### Targeted manual checks

The individual commands remain valid and documented for a targeted, manual
check of just one concern — for example, right after fixing a type error,
without re-running every hook:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
```

These are ad hoc equivalents to individual hooks, not the official local
quality check — use `uv run pre-commit run --all-files` (above) when you want
the full, authoritative local check.

## Troubleshooting

- **A hook reports "files were modified by this hook" and fails.** This is
  expected for `ruff-format`, `end-of-file-fixer`, `trailing-whitespace`,
  `mixed-line-ending`, and `uv-lock` — they fix the issue in place and then
  fail once, so you can review the change. Run `git add` on the modified
  files and commit again; the second attempt passes.
- **`mypy` or `ruff-check` fails.** Fix the reported issue the same way you
  would for the [required quality commands](contributing.md#quality-checks) —
  these hooks run the identical commands.
- **`gitleaks` reports a finding.** Treat it as a real secret until proven
  otherwise: remove/rotate the credential per
  [SECURITY.md](../../SECURITY.md). Do not add a gitleaks exception to silence
  a finding without first confirming it is genuinely not a secret.
- **`uv-lock` fails / modifies `uv.lock`.** `pyproject.toml` changed without a
  matching `uv.lock` update. `git add uv.lock` (now regenerated) and commit
  again.
- **A hook environment needs to be rebuilt** (e.g. after corrupting the local
  cache): `uv run pre-commit clean` removes cached hook environments; the next
  run reinstalls them.
- **Emergency bypass.** `git commit --no-verify` and `SKIP=<hook-id> git commit`
  exist as pre-commit/git features, but bypassing a quality gate is itself a
  deliberate exception, not a routine convenience — it should not be used to
  avoid fixing a real failure, only for a clearly justified, temporary reason
  that is then resolved immediately after.

## Typical workflows

**Normal commit:**

```powershell
git add <files>
git commit -m "..."
# pre-commit runs automatically; if it modifies files, `git add` them and
# commit again.
```

**Normal push:**

```powershell
git push
# pytest runs automatically via the pre-push hook; a failing test suite
# blocks the push.
```

**Full local quality check on demand** (no commit yet, or after editing
`.pre-commit-config.yaml`):

```powershell
uv run pre-commit run --all-files
uv run pre-commit run --hook-stage pre-push --all-files  # to also re-run pytest
```

**Targeted manual check of one concern while developing:**

```powershell
uv run ruff format --check . ; uv run ruff check . ; uv run mypy src/logrhythm_sdk
```

**First-time setup on a fresh clone:**

```powershell
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
uv run pre-commit install --hook-type commit-msg
```

## See also

- [Contributing](contributing.md) — local setup and the required quality
  commands this automation mirrors.
- [Dependencies & Tooling](dependencies.md) — why `pre-commit` is a pinned dev
  dependency rather than a global tool.
- [Definition of Done](definition-of-done.md) — the completion checklist this
  automation partially enforces.
- [Claude Workflow & Architecture Governance](claude-workflow.md) — Claude's
  commit/push rules, which this automation runs underneath.
- [Claude Code: Technical Settings](claude-code.md#commit-message-validation) —
  the `conventional-pre-commit` tool's exact, tested behavior and its
  server-side counterpart.
- [GitHub Actions: CI & Build](ci.md) — the same hooks running server-side.
- [Repository Templates & Markdown Tooling](templates.md) — the
  `markdownlint-cli2` configuration and manual `--fix` invocation in detail.
