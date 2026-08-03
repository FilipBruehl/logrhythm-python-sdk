# Claude Code: Technical Settings

This page documents the technical configuration that enforces, in tooling,
the rules [Claude Workflow & Architecture Governance](claude-workflow.md)
already states as binding process: which commands Claude Code may run
without asking, which always require approval, which are blocked outright,
and how commit messages are validated, locally and in CI.
[claude-workflow.md](claude-workflow.md) remains the normative source for
*why* these boundaries exist and what Claude may decide on its own;
this page documents *how* that is technically configured and enforced.

## Purpose

Before this phase, every rule in [Claude Workflow](claude-workflow.md) — "only
commit after explicit approval," "never force-push," "never bypass a hook" —
was enforced by discipline and review alone; nothing technical prevented a
mistake. This phase adds a second, mechanical layer underneath that
discipline: Claude Code's own permission system (`.claude/settings.json`)
and a Conventional Commit message validator (locally via a `commit-msg` git
hook, and server-side in CI). Neither replaces the process in
[Claude Workflow](claude-workflow.md) — a technical permission is not a
substitute for the content decision a user makes when approving a specific
commit, push, or PR (see
[A technical permission is not content approval](#a-technical-permission-is-not-content-approval)).

## Settings layers

Two `.claude/` settings files exist, with a deliberately different purpose
and version-control status each:

### Project settings (`.claude/settings.json`)

Versioned, committed, and shared by every clone of this repository. It holds
the project-wide, deliberately-decided permission rules documented on this
page: `defaultMode`, the narrow `allow` list, `ask` rules, and `deny` rules.
Nothing temporary or task-specific belongs here — see
[Changing `.claude/settings.json`](#changing-claudesettingsjson).

### Local settings (`.claude/settings.local.json`)

Machine-specific and **never committed** —
[`.gitignore`](../../.gitignore) already excludes it
(`.claude/settings.local.json`). It is where an individual clone's temporary
approvals, one-off commands, and machine-dependent paths accumulate (for
example, when a permission prompt is answered "yes, don't ask again" during
a session) without ever becoming a project-wide rule. `git status` on
`.claude/` should only ever show `settings.json` as tracked; `settings.local.json`
existing untracked alongside it is expected and correct.

## Default permission mode

`.claude/settings.json` sets:

```json
"defaultMode": "default"
```

This is Claude Code's standard mode: it prompts for approval on first use of
any tool or command not otherwise covered by an `allow`/`ask`/`deny` rule
below. `acceptEdits` (auto-accepts file edits) and `bypassPermissions`
(skips prompts almost entirely) are deliberately **not** used — the normal
approval dialog stays in place for anything not explicitly, narrowly
allowed.

## Allow, ask, and deny rules

Claude Code evaluates rules in a fixed order — **deny, then ask, then
allow** — and the first match wins regardless of how specific a
lower-priority rule is. A broad `deny` rule blocks a call even if a narrower
`allow` rule also matches it; a matching `ask` rule always prompts, even if a
more specific `allow` rule would otherwise have skipped the prompt. This is
Claude Code's own documented precedence, not a project-specific convention —
see [Claude Code: Configure permissions](https://code.claude.com/docs/en/permissions).

### Allowed read and quality commands

`allow` is intentionally narrow — exact commands, not prefix wildcards —
covering only the read-only git inspection and quality commands this project
actually documents and runs routinely:

```text
git status
git status --short
git diff
git diff --stat
git diff --check
git diff --cached
git diff --cached --stat
git diff --cached --check
git log
git show
git branch --show-current
git rev-parse <anything>
git remote -v

uv sync
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy src/logrhythm_sdk
uv run pytest
uv run pre-commit run <anything>
uv build
```

`git rev-parse` and `uv run pre-commit run` are allowed with a trailing
wildcard because both are always invoked with further arguments in practice
(a ref/flag for `rev-parse`; `--all-files`, `--hook-stage pre-push
--all-files`, a specific hook ID, or `--files <path>` for `pre-commit run` —
see [Pre-Commit, Local quality check](pre-commit.md#local-quality-check));
every other entry is an exact string, deliberately not
`Bash(git *)`/`Bash(uv *)` or similar broad prefixes. No blanket `Bash`,
`Bash(git:*)`, or `Edit` allow rule exists anywhere in
`.claude/settings.json`.

Note that Claude Code already treats **read-only forms of `git`** (including
`status`, `diff`, `log`, `show`, and `rev-parse` with arbitrary arguments) as
a built-in read-only command class that never prompts, in every permission
mode, independent of any rule in this file. The explicit `allow` entries
above are still written out — an explicit, versioned rule instead of relying
solely on that built-in behavior, consistent with
[SPEC-000](../specifications/design-principles.md)'s "Explicit over
implicit" principle, and a safety net if that built-in classification is
ever narrower than expected for a specific invocation.

File inspection (reading, searching, listing files) deliberately has **no**
corresponding Bash allow rules for `cat`, `find`, `grep`, or `ls` — Claude
Code's built-in Read, Glob, and Grep tools cover the same need without a
shell command.

### Approval-required git actions

The following remain approval-required on every invocation — no `allow`
rule exists for them, and `.claude/settings.json` additionally lists them
under `ask` as an explicit, self-documenting backstop:

```text
git switch <anything>
git checkout <anything>
git add <anything>
git commit <anything>
git push <anything>
gh pr create <anything>
uv add <anything>
uv remove <anything>
uv lock --upgrade <anything>
```

`git branch` is a deliberate exception to the `ask`-backstop pattern above:
an `ask` rule is matched on the full literal Bash prefix, and a broad rule
like `Bash(git branch *)` would also match — and force a prompt for — the
narrower `Bash(git branch --show-current)` **allow** rule above, since `ask`
always outranks `allow` regardless of specificity. Branch creation/deletion
by name (`git branch <name>`, already separately hard-denied for `-D`) is
therefore left to `defaultMode: "default"`'s own baseline behavior — every
Bash command without a matching `allow` rule already prompts — rather than
adding an `ask` rule that would also swallow the intended `--show-current`
allowance.

### Hard deny rules

`deny` blocks destructive or governance-bypassing operations outright,
regardless of any `allow`/`ask` rule and regardless of who — human or
Claude — would otherwise approve them in the moment:

```text
git reset --hard
git clean -f / -fd / -fdx / -x
git push --force / -f (in any argument position)
git push --force-with-lease (in any argument position)
git commit --amend (in any argument position)
git branch -D / --delete --force
git rebase
git checkout -- .
git restore . / --source <anything>
git tag -d / --delete
git push --delete / origin --delete / --delete (in any argument position)
```

Deny patterns use a wildcard on both sides where a flag can realistically
appear in more than one position (`git push origin main --force` as well as
`git push --force origin main`), consistent with
[Git Safety Rules](claude-workflow.md#git-safety-rules)'s forbidden-operations
list — this page adds the mechanical enforcement, that page states the rule
and its rationale.

#### Hook-bypass prevention

```text
Bash(* --no-verify *)
Bash(* --no-verify)
Bash(git commit --no-verify)
Bash(git push --no-verify)
```

`--no-verify` is denied wherever it appears in a command, catching both
`git commit --no-verify` and `git push --no-verify` regardless of what other
flags surround it.

**`SKIP=<hook-id>` cannot be denied the same way, and this is a deliberate,
documented gap rather than an oversight.** Claude Code's deny-rule matching
strips *any* leading environment-variable assignment before comparing a
Bash command against a pattern (so a deny rule can't be defeated by
prefixing an unrelated variable) — which means a literal `SKIP=` pattern
can never match, because the assignment is discarded before the comparison
happens. The actual protection is structural, not pattern-based: `git
commit`/`git push` have no `allow` rule at all (see
[Approval-required git actions](#approval-required-git-actions)), so
`defaultMode: "default"` already forces a prompt for *every* invocation,
`SKIP=...` prefix or not — the human reviewing that prompt sees the full,
literal command, including any `SKIP=` prefix, before it runs.

### A technical permission is not content approval

Even where `.claude/settings.json` allows a Bash command to run without a
prompt (the read/quality commands above), that is a **technical**
permission only. It says nothing about whether creating a specific branch,
commit, push, or PR was actually requested in the current task — that
remains governed entirely by
[Claude Workflow](claude-workflow.md#claude-workflow) and
[CLAUDE.md](../../CLAUDE.md). A technical `allow` rule never substitutes for
the user's explicit, scoped authorization a git write action or a `.claude/settings.json`
change still requires.

## Sensitive files

`deny` rules block Claude's built-in file tools (Read and Edit — which also
covers Write/NotebookEdit for the same paths) from touching:

```text
.env, .env.*
*.pem, *.key, *.p12, *.pfx
credentials*, secrets*
token, token.txt, token.json, *.token, *_token.txt, *_token.json
```

These match at any depth in the repository (bare-filename gitignore
semantics), per [SECURITY.md](../../SECURITY.md) and
[CLAUDE.md](../../CLAUDE.md)'s "Security requirements." No file in this
repository currently matches any of these patterns (checked explicitly when
these rules were introduced and re-checked whenever they change).

The token-related patterns are deliberately **narrow, specific filenames and
extensions** rather than a broad `token*` prefix — an earlier draft of this
rule used exactly that broad form, but it would also have blocked entirely
legitimate future source files such as `token.py`, `token_model.py`, or
`token_validation.py` (all plausible module names once
[SPEC-003](../specifications/authentication.md)'s Bearer-token handling is
implemented under `logrhythm_sdk.core.auth`). The six patterns above target
the shape of an actual local secret dump (a bare `token` file, a
`.token`-suffixed file, or a `*_token.txt`/`*_token.json` export) without
matching ordinary `.py` source, test, or documentation files. If a future,
genuinely secret-shaped filename doesn't already fit one of these patterns,
adding a new, equally specific pattern for it is a deliberate, reviewed
change to this file — not a reason to widen an existing pattern back into a
broad prefix.

`.claude/settings.local.json` additionally has its own `Edit` deny rule —
Claude may read it (for example, to report its contents) but never edit it,
since it is the user's own machine-specific file, not something Claude
manages.

## Network policy

No Bash allow rule exists for `curl`, `wget`, or any other network-fetch
command, and none existed for those tools before this phase either, other
than task-specific, temporary entries left over in `.claude/settings.json`
from earlier phases (a one-off `curl` fetch of uv's own documentation, and
two `grep` patterns from an earlier documentation-correction task) — both
removed as part of this phase, per
[CLAUDE.md](../../CLAUDE.md)'s "temporary or task-specific approvals must
never be promoted into `.claude/settings.json`." A network fetch Claude
genuinely needs goes through the built-in `WebFetch`/`WebSearch` tools
instead of a Bash network command, or is approved individually, in the
moment, for that specific task.

## Branch creation

Unchanged by this phase — `.claude/settings.json` grants no blanket
permission for `git switch`/`git checkout`/`git branch`; every invocation is
approval-required (see
[Approval-required git actions](#approval-required-git-actions)). The
content rule for *which* branch Claude may create at all is
[Claude Workflow, Branches](claude-workflow.md#branches): an explicitly
named `feature/*` or `integration/*` branch, never a branch structure Claude
decides on its own initiative.

## Commit workflow

The technical steps [Definition of Done](definition-of-done.md#change-hygiene)
and [Claude Workflow, Commits](claude-workflow.md#commits) already require —
review status, review diff, run quality checks, confirm scope — are restated
here as the concrete pre-commit checklist:

Before ever proposing that a commit be made, Claude checks:

```powershell
git status --short
git diff --cached --check
git diff --cached --stat
```

and confirms, from that output and the work just done:

- All required quality checks have passed (see
  [Definition of Done, Quality checks](definition-of-done.md#quality-checks)).
- Tests pass per [Definition of Done, Tests](definition-of-done.md#tests).
- Only the files in scope for the approved change are staged — nothing
  picked up by accident.
- No secrets, credentials, or real customer data appear in the staged diff.
- No harness- or machine-local file (`.claude/settings.local.json`, `.env`,
  etc.) is staged.
- The drafted commit message follows
  [Commit Strategy](commits.md) and will pass the `commit-msg` hook (see
  [Commit message validation](#commit-message-validation) below).
- No hook is being bypassed (`--no-verify`, `SKIP=`).

Claude then proposes the exact commit (message and file list) and creates it
only after the user's explicit approval for that specific commit — never
before, and never as a WIP/placeholder commit — per
[Claude Workflow, Commits](claude-workflow.md#commits).

## Commit message validation

Every commit message is checked against [Commit Strategy](commits.md), both
locally (two `commit-msg` git hooks, at the moment a commit is created) and
server-side (a dedicated CI job, against every commit a pull request or push
actually introduces). Both use the same tool, the same
`uv.lock`-pinned version, the same allowed-type list, and the same exact
type-casing check, so a message that passes locally cannot then fail in CI
for a different reason.

### Tool

[`conventional-pre-commit`](https://github.com/compilerla/conventional-pre-commit)
(PyPI package `conventional-pre-commit`) — a Python-native Conventional
Commits validator, added as a `[dependency-groups.dev]` dev dependency in
`pyproject.toml` (not Node.js/npm/`package.json`/Commitlint — see
[ADR-0006](../adr/0006-httpx-transport.md)'s and
[Dependencies & Tooling](dependencies.md)'s existing Python-native tooling
preference). Adding it as a dev dependency, exactly like `pre-commit` itself
(see [Pre-Commit, Chosen approach](pre-commit.md#chosen-approach-a-pinned-dev-dependency-not-a-global-tool)),
means the local `commit-msg` hook and
[`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py)
both resolve to the exact same `uv.lock`-pinned version — there is no second,
independently-versioned copy of this tool anywhere.

This tool alone is not sufficient, though: empirically, it does not reject a
valid type in the wrong case (`Feat(config): ...` passes both its default
and `--strict` modes — see
[Empirically tested behavior](#empirically-tested-behavior)). The exact-
lowercase rule is therefore enforced by a small, additional, shared check —
see [`commit_types.py`](#commit_typespy-the-shared-lowercase-check) below.

### `commit_types.py`: the shared lowercase check

[`.github/scripts/commit_types.py`](../../.github/scripts/commit_types.py)
is the **single, shared implementation** of two things every commit-message
check in this project needs: `ALLOWED_TYPES` (the type list, matching
[Commit Strategy, Allowed commit types](commits.md#allowed-commit-types)
exactly) and `casing_error(subject)`, which extracts the type token from a
commit subject and returns an error message if — and only if — it is a
valid type in the wrong case. A subject with no recognizable `type:` prefix
at all, or a type that is not a valid type in *any* case (e.g. `feature:`),
is intentionally left alone: `conventional-pre-commit` already rejects both
on its own.

It is deliberately **not** a Conventional Commits parser or a competing
validator — it checks exactly one thing `conventional-pre-commit` does not,
and nothing more. Both consumers use it instead of re-implementing the same
rule:

- The local `commit-type-lowercase` hook (below) calls its CLI entry point
  directly.
- [`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py)
  imports `ALLOWED_TYPES` and `casing_error` from it directly (both scripts
  live under `.github/scripts/`, so a plain `import commit_types` resolves
  without any package machinery).

The one place this list is still necessarily duplicated as plain text is
`conventional-pre-commit`'s own hook `entry:` args in
`.pre-commit-config.yaml` — a third-party tool's CLI arguments, not
something YAML can import from a Python module. `commit_types.py` remains
the one normative, *importable* source for every Python-side check.

### Local: the `commit-msg` hooks

Configured in [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) as
two `local` hooks (`language: system`, invoked via `uv run`, matching the
project's `mypy` hook), both pinned to the `commit-msg` stage only:

```yaml
- id: commit-type-lowercase
  name: commit-type-lowercase
  entry: uv run python .github/scripts/commit_types.py
  language: system
  stages: [commit-msg]

- id: conventional-pre-commit
  name: conventional-pre-commit
  entry: uv run conventional-pre-commit feat fix docs refactor test chore perf style build ci revert
  language: system
  stages: [commit-msg]
```

`commit-type-lowercase` runs first and catches the exact-casing gap
described above; `conventional-pre-commit` then checks the rest of
Conventional Commits syntax. pre-commit runs every hook bound to a stage and
reports all of their results, so a message can fail either or both — there
is no short-circuiting between the two hook entries.

The type list passed to `conventional-pre-commit` matches
[Commit Strategy, Allowed commit types](commits.md#allowed-commit-types)
exactly. `--scopes`/`--force-scope` are deliberately **not** passed: scopes
stay optional, and no fixed scope enum is technically enforced — the
[Recommended scopes](commits.md#recommended-scopes) list stays a
documentary and review-time convention, per this phase's explicit
instruction not to build a bespoke scope validator. `--strict` is
deliberately **not** used either — see
[Why no `--strict` locally](#why-no---strict-locally) below.

### Server-side: the `commit-message` CI job

A new `commit-message` job in
[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) runs in
parallel with `quality`; `test` now requires both to succeed before it
starts:

```text
commit-message ─┐
quality         ├──> test
```

It resolves the correct commit range for the triggering event, then runs
[`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py)
against every commit in that range — see
[GitHub Actions: CI & Build, CI commit range](ci.md#ci-commit-range) for the
exact base/head resolution per trigger, and
[GitHub Actions: CI & Build, Commit-message job](ci.md#commit-message-job)
for the job itself. The status check this produces is `CI / commit-message`
(see [Status check names](ci.md#status-check-names)).

### Why no `--strict` locally

`conventional-pre-commit --strict` "disallows fixup! and merge commits" —
but this project wants those two cases *skipped*/*handled specifically*, not
uniformly rejected, and wants normal local work (a `fixup!` commit destined
for an interactive squash, or a routine `integration/*` merge) to stay
possible. Passing `--strict` would block both outright with the tool's own
generic message, so
[`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py)
implements this project's specific handling itself (see
[Special-case handling](#special-case-handling-merge-revert-fixupsquash)
below) instead of relying on the tool's blanket strict mode.

### Empirically tested behavior

The tool's actual, non-strict behavior — and, separately, `commit_types.py`'s
casing check — were tested directly (never assumed) before being relied on
anywhere in this project's tooling:

| Message | `conventional-pre-commit` (default) | `conventional-pre-commit` (`--strict`) | `commit_types.casing_error` | Combined local hook result |
| --- | --- | --- | --- | --- |
| `feat(config): add configuration loader` | Pass | Pass | No error | **Pass** |
| `ci(github): add commit validation` | Pass | Pass | No error | **Pass** |
| `docs: update contribution guide` | Pass | Pass | No error | **Pass** |
| `fix!: remove invalid fallback` | Pass | Pass | No error | **Pass** |
| `update files` | **Fail** | **Fail** | No error (no type prefix at all) | **Fail** |
| `feature: add loader` (unknown type) | **Fail** | **Fail** | No error (not a casing issue) | **Fail** |
| `feat(config) add loader` (missing colon) | **Fail** | **Fail** | No error (no type prefix matched) | **Fail** |
| `Feat(config): add loader` (capitalized type) | Pass | Pass | **Error** | **Fail** |
| `FIX: correct timeout` (capitalized type) | Pass | Pass | **Error** | **Fail** |
| `Docs: update guide` (capitalized type) | Pass | Pass | **Error** | **Fail** |
| `CI(github): add workflow` (capitalized type) | Pass | Pass | **Error** | **Fail** |
| A commit with a body | Pass | Pass | No error | **Pass** |
| A commit with a `BREAKING CHANGE:` footer | Pass | Pass | No error | **Pass** |
| `revert: remove configuration loader` (Conventional-style revert) | Pass | Pass | No error | **Pass** |
| `Revert "feat(config): add configuration loader"` (git's own default revert subject) | **Fail** | **Fail** | No error (no type prefix matched) | **Fail** |
| `Merge branch 'main' into feature/x` | Pass (auto-approved) | **Fail** | No error (no type prefix matched) | **Pass** |
| `Merge pull request #12 from ...` (GitHub-generated) | Pass (auto-approved) | **Fail** | No error (no type prefix matched) | **Pass** |
| `fixup! feat(config): add configuration loader` | Pass (auto-approved) | **Fail** | No error (no type prefix matched) | **Pass** |
| `squash! feat(config): add configuration loader` | Pass (auto-approved) | **Fail** | No error (no type prefix matched) | **Pass** |

"Combined local hook result" is what actually happens on `git commit`: both
`commit-type-lowercase` and `conventional-pre-commit` must pass. Note that
`commit_types.casing_error` never fires for the merge/`fixup!`/`squash!`/
git-revert rows — its regex only matches a `type:`/`type(scope):` prefix
immediately at the start of the subject, so those messages fall through to
`conventional-pre-commit`'s own (separately documented) handling unaffected.

One result remains genuinely non-obvious and worth calling out explicitly
rather than letting it stay implicit:

- **`conventional-pre-commit` itself is not case-sensitive on the commit
  type**, with or without `--strict` — `Feat(config): ...` passes it either
  way. This is a real, tested gap between
  [Commit Strategy](commits.md#conventional-commits) ("type — required,
  lowercase") and what the tool alone mechanically enforces. It is why
  `commit_types.py`'s exact-lowercase check exists as a small, targeted
  addition alongside the tool rather than a reason to trust the tool's
  casing leniency or build a full replacement validator.
- **Git's own default revert subject fails validation even without
  `--strict`.** A plain `git revert` (with its message left untouched) will
  therefore fail the local `commit-msg` hook. Use `revert: <description>`
  (Conventional-Commit style, matching the `revert` type's entry in
  [Allowed commit types](commits.md#allowed-commit-types)) instead of
  relying on git's auto-generated message, or edit the revert commit's
  message (`git revert --edit`) into that form before committing.
  [`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py)
  recognizes git's exact default format (`Revert "<original subject>"`) as
  an accepted exception server-side, but the local hook has no such
  exception — it runs the tool directly.

### Special-case handling: merge, revert, fixup/squash

[`.github/scripts/validate_commits.py`](../../.github/scripts/validate_commits.py)
applies this exact order to every commit in the resolved range:

1. **Merge commit** (two or more parents, detected structurally via
   `git log --format=%P`) → skipped, not validated. Recognized purely by
   parent count, independent of message content.
2. **`fixup!`/`squash!` prefix** → rejected outright, unconditionally. The
   tool itself would accept these without `--strict` (see the table above),
   but they must never remain in a commit range about to land on
   `main`/`integration/**`.
3. **Git's default revert subject** (`Revert "<original subject>"`, matched
   literally) → accepted as a recognized exception, without invoking the
   tool at all for that message.
4. **A valid type in the wrong case** (`commit_types.casing_error`, the same
   shared check the local `commit-type-lowercase` hook uses) → rejected
   outright, without invoking `conventional-pre-commit` at all for that
   message.
5. Everything else → validated with the tool itself, in its default
   (non-strict) mode.

This is intentionally more specific than either "no `--strict`" (which would
also silently accept `fixup!`/`squash!`) or "`--strict`" (which would reject
merge commits and git's own revert format instead of recognizing them) —
see [Why no `--strict` locally](#why-no---strict-locally).

## Push and PR boundaries

Unchanged by this phase, restated for completeness alongside the technical
rules above: Claude pushes only on explicit instruction, never to `main`,
never force-pushed; creates a PR only on explicit instruction; never merges,
changes branch protection, or triggers a release — see
[Claude Workflow, Push](claude-workflow.md#push) and
[Pull Requests](claude-workflow.md#pull-requests). `git push`, `git commit`,
and `gh pr create` have no `allow` rule in `.claude/settings.json` (see
[Approval-required git actions](#approval-required-git-actions)), so this is
also mechanically true, not only a matter of process.

## Changing `.claude/settings.json`

`.claude/settings.json` is versioned, ordinary repository content — a
change to it goes through the same process as any other documentation or
tooling-configuration change in this project: a small, reviewable change
(see [CLAUDE.md](../../CLAUDE.md), "Change discipline"), and is never edited
to promote a temporary or task-specific approval into a project-wide rule
(see [Settings layers](#settings-layers) above). A permission change that
would loosen an existing `deny` rule or the git-write boundaries in
[Claude Workflow](claude-workflow.md) is architecture-governance-adjacent —
raise it explicitly rather than adjusting it quietly alongside unrelated
work, per
[Architecture Governance](claude-workflow.md#architecture-governance).

## Troubleshooting

- **A Bash command prompts even though it looks like it should be
  allowed.** Check for an exact match, including trailing punctuation —
  `allow` entries in this project are exact strings or a single documented
  trailing wildcard, not broad prefixes; a slightly different invocation
  (extra flag, different argument order) will not match and will correctly
  fall through to a prompt.
- **`git branch` (no arguments) prompts instead of running silently.** This
  is expected — see [Approval-required git actions](#approval-required-git-actions)'s
  explanation of why `git branch` has no `ask`/`allow` wildcard.
- **The `commit-msg` hooks reject a message you believe is valid.** Confirm
  the type is one of
  [Commit Strategy's allowed types](commits.md#allowed-commit-types),
  **written in exact lowercase** (`feat`, not `Feat`/`FEAT`), the colon and
  description are present, and — if reverting — see
  [Empirically tested behavior](#empirically-tested-behavior) above for
  git's default revert-message gap. The `commit-type-lowercase` hook's error
  message names the exact offending token when casing is the problem.
- **`CI / commit-message` fails but the local hook passed every commit
  individually.** The local hook only ever sees one message at a time, at
  the moment of that commit; the CI job additionally rejects any
  `fixup!`/`squash!` message still present in the final range (the local
  hook, by design, does not) — see
  [Special-case handling](#special-case-handling-merge-revert-fixupsquash).
  Squash/rebase those commits away before the range reaches `main`/`integration/**`.
- **A fresh clone doesn't validate commit messages locally.** The
  `commit-msg` hook type is a separate, explicit install step — see
  [Pre-Commit, Installation](pre-commit.md#installation).
- **Confirming this file's own structure.** `.claude/settings.json` is
  plain JSON; validate it the same way as any other JSON file in the
  repository (see [Pre-Commit, Hook types](pre-commit.md#hook-types) for the
  general file-hygiene hooks this project already runs) if a change to it is
  suspected of being malformed.

## See also

- [Claude Workflow & Architecture Governance](claude-workflow.md) — the
  governance and process rules this page technically enforces.
- [Commit Strategy](commits.md) — the message format and allowed types this
  page's validation checks against.
- [Pre-Commit & Local Code Quality Automation](pre-commit.md) — installation
  of all three hook types, including `commit-msg`.
- [GitHub Actions: CI & Build](ci.md) — the `commit-message` job, commit
  range resolution, and the `CI / commit-message` status check.
- [Definition of Done](definition-of-done.md) — the completion checklist the
  [Commit workflow](#commit-workflow) section above restates as a concrete,
  pre-commit checklist.
- [CLAUDE.md](../../CLAUDE.md) — the always-loaded summary these settings
  enforce.
