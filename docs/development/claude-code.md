# Claude Code: Technical Settings

## Purpose

This page documents the technical behavior of the versioned
`.claude/settings.json` adapter. Vendor-neutral AI Development governance is
defined exclusively in [`AGENTS.md`](../../AGENTS.md); the repository-root
[`CLAUDE.md`](../../CLAUDE.md) is the short Claude Code adapter.

The settings file enforces a subset of AGENTS.md mechanically. It does not
grant content authority and cannot replace repository review or human approval.

## Settings layers

### Project settings

`.claude/settings.json` is versioned repository content. It defines shared
Claude Code permissions that apply to every clone using that tool.

### Local settings

`.claude/settings.local.json` is machine-local, ignored by Git, and may hold
temporary approvals for one clone. It must not become project governance, must
not be committed, and is protected from tool-driven edits by the project
settings.

## Default permission mode

The project sets `defaultMode` to `default`. Claude Code may execute a matching
`allow` rule without another tool prompt, asks for approval when an `ask` rule
matches, and blocks a matching `deny` rule.

Claude Code evaluates these technical rules according to its own permission
matcher. The conceptual order is deny, then ask, then allow. Repository
governance still applies when a command is technically allowed.

## Allow rules

The allow list is intentionally narrow. It covers:

- read-only Git inspection such as status, diff, log, show, revision lookup,
  and remote inspection;
- dependency synchronization through `uv`;
- the required Ruff, mypy, pytest, pre-commit, and build commands.

Ordinary file inspection uses Claude Code's built-in file tools and therefore
does not need broad shell allow rules for commands such as `cat`, `find`, or
`grep`.

## Ask rules

The ask list covers operations that can change repository or dependency state:

- branch switching or checkout;
- staging and committing;
- pushing;
- creating a pull request;
- adding, removing, or upgrading dependencies.

An interactive technical approval is not equivalent to the explicit content
approval required by AGENTS.md. Both boundaries apply.

## Deny rules

The deny list blocks technical forms of:

- destructive reset and clean operations;
- force pushes;
- commit amendment;
- forced branch deletion;
- rebase;
- broad restore/checkout operations that discard work;
- tag or remote-branch deletion;
- hook bypasses such as `--no-verify`.

Some AGENTS.md restrictions cannot be represented perfectly by command-prefix
matching. The absence of a matching deny rule is never permission to bypass a
governance rule.

## Sensitive files

Read and edit access is denied for common secret-bearing paths and extensions,
including environment files, private-key/certificate formats, credential and
secret files, and narrowly named token files. Patterns are deliberately scoped
to avoid blocking legitimate source files merely because their names contain a
word such as `token`.

Secret protection in `.claude/settings.json` supplements, but does not replace,
the repository-wide security rules and gitleaks checks.

## Network policy

The project settings grant no blanket network-fetch permission. A task-specific
network operation may therefore require tool approval and must still be within
the user's authorized scope. Temporary approvals must not be promoted into the
versioned settings file.

## Commit-message validation

Commit-message validation is repository tooling, not Claude Code behavior. It
applies to every contributor and AI Coding Agent through local `commit-msg`
hooks and the `CI / commit-message` job.

The implementation and its special cases are documented in
[Pre-Commit & Local Code Quality Automation](pre-commit.md#commit-message-validation)
and [GitHub Actions: CI & Build](ci.md#commit-message-job).

## Changing the settings

Changes to `.claude/settings.json` are ordinary, reviewable repository changes:

- keep the change limited to a demonstrated Claude Code integration need;
- do not place general project rules in the settings or this page;
- do not promote one-session approvals into project policy;
- validate JSON syntax and review allow/ask/deny interactions;
- update this technical page when behavior changes.

Any broader governance change belongs in `AGENTS.md` and remains human-owned.

## References

- [`AGENTS.md`](../../AGENTS.md) — binding vendor-neutral governance.
- [`CLAUDE.md`](../../CLAUDE.md) — repository-root Claude Code adapter.
- [Pre-Commit](pre-commit.md) — repository-wide local automation.
- [CI & Build](ci.md) — repository-wide server-side automation.
